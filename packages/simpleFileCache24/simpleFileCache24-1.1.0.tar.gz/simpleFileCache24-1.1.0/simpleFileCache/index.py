from functools import cache
import os
from typing_extensions import TypedDict
import typing
from sioDict import SioWrapper
import simpleFileCache.utils.crypt as crypt
from simpleFileCache.meta import getTargetKeyring, available_literal

@cache
def init_directInput(privateKey):
    if isinstance(privateKey, str):
        privateKey = privateKey.encode()
    
    private_key = crypt.deserialize_keys(privateKey)
    public_key = private_key.public_key()
    return private_key, public_key

@cache
def init_moduleFile():

    module_key_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "key.pem")
    if os.path.exists(module_key_file):
        with open(module_key_file, "rb") as f:
            private_key = crypt.deserialize_keys(f.read())
            public_key = private_key.public_key()
    else:
        private_key, public_key = crypt.generate_keys()
        with open(module_key_file, "wb") as f:
            f.write(crypt.serialize_keys(private_key, public_key)[0])

    return private_key, public_key

@cache
def init_keyring(target_keyring = None):
    from keyring.backend import KeyringBackend
    if target_keyring is None:
        target_keyring = getTargetKeyring()
    target_keyring : KeyringBackend

    if (private_bytes:= target_keyring.get_password("Py_SimpleFileCache", "__PRIVATE_KEY__")) is None:
        private_key, public_key = crypt.generate_keys()
        private_bytes, public_bytes = crypt.serialize_keys(private_key, public_key)

        target_keyring.set_password(
            "Py_SimpleFileCache", "__PRIVATE_KEY__", private_bytes.decode("utf-8")
        )
    else:
        private_key = crypt.deserialize_keys(private_bytes.encode("utf-8"))
        public_key = private_key.public_key()

    return private_key, public_key

class CacheIndexEntry(TypedDict, total = False):
    checksum : str
    type : available_literal
    
    # only for updatable item
    updatableInterval : int
    
    lastPulled : str
    lastCommitted : str

class CacheIndexDict(SioWrapper):
    def __init__(
        self, 
        path: str, 
        *args, 
        privateKey : typing.Union[typing.Literal["moduleFile", "keyring"], str, bytes] = "keyring", 
        **kwargs
    ):
        if privateKey == "moduleFile":
            self.privateKey, self.publicKey = init_moduleFile()
        elif privateKey == "keyring":
            self.privateKey, self.publicKey = init_keyring()
        else:
            self.privateKey, self.publicKey = init_directInput(privateKey)
        self.clearMethod = self._clear
        self.saveMethod = self.save
        self.loadMethod = self.load
        super().__init__(path, *args, **kwargs)
        

    @staticmethod
    def _clear(path : str):
        with open(path, "w") as f:
            f.write("{}")

    def save(self, d, path : str):
        crypt.sign_data_with_timestamp(path, d, self.privateKey)
    
        
    def load(self, path):
        if not os.path.exists(path):
            return
        
        with open(path, "rb") as f:
            if f.read() == b"{}":
                return

        if not crypt.verify_signed_data(path, self.publicKey):
            raise RuntimeError(f"Index {path} is tampered")
        
        self.clear()
        self.update(crypt.verify_signed_data.get_last())
        
def newEntry( 
    d : CacheIndexDict,
    key : str, 
    checksum : str,
    type : available_literal,
    
    # only for updatable item
    updatableInterval : int = None,
    
    lastPulled : str = None,
    lastCommitted : str = None
):
    entry = CacheIndexEntry(
        checksum = checksum, 
        type = type, 
        updatableInterval = updatableInterval, 
        lastPulled = lastPulled, 
        lastCommitted = lastCommitted
    )
    entry = {k : v for k, v in entry.items() if v is not None}
    d[key] = entry