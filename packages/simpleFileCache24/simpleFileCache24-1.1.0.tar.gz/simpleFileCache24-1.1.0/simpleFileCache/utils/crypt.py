import base64
import datetime
import os
import orjson
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    return private_key, public_key

def serialize_keys(private_key : rsa.RSAPrivateKey, public_key : rsa.RSAPublicKey = None):
    if public_key is None:
        public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b'SimpleFileCache')
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_bytes, public_bytes

def deserialize_keys(private_bytes, password=b'SimpleFileCache') -> rsa.RSAPrivateKey:
    """
    Deserializes PEM-encoded private key bytes to a private key object.

    :param private_bytes: The PEM-encoded private key bytes.
    :param password: The password used for decrypting the private key, if it is encrypted. None if the key is not encrypted.
    :return: A private key object.
    """
    # Load the private key. Assumes the key is in PEM format.
    private_key = load_pem_private_key(
        private_bytes, password=password, backend=default_backend()
    )
    
    return private_key

def sign_data_with_timestamp(jsonPath : str, data : dict, private_key : rsa.RSAPrivateKey):
    
    grouped_data = {
        'data' : data,
        'timestamp' : (int(datetime.datetime.now().timestamp()) // 10) * 10
    }
    
    hash_data = orjson.dumps(grouped_data)
    
    # Sign the data with the private key
    signature = private_key.sign(
        hash_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    signature = base64.b64encode(signature).decode('utf-8')
    
    savedata = {
        'data' : data,
        'signature' : signature
    }
    
    save_data = orjson.dumps(savedata)
    
    with open(jsonPath, 'wb') as f:
        # clear file
        f.truncate()
        f.write(save_data)

_verify_signed_last_data = None

def get_last():
    return _verify_signed_last_data

def verify_signed_data(filepath: str, public_key_pem: bytes):
    # Load the public key
    if not isinstance(public_key_pem, rsa.RSAPublicKey):
        public_key = load_pem_public_key(public_key_pem)
    else:
        public_key = public_key_pem
        
    # Read the saved data from the file
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Extract the signature and data (assuming signature and data are stored together as JSON)
    saved_data = orjson.loads(content)
    signature = base64.b64decode(saved_data['signature'].encode('utf-8'))

    # Use the file's last modified time as the timestamp
    file_mod_time = os.path.getmtime(filepath)
    rounded_mod_time = (int(file_mod_time) // 10) * 10

    # Reconstruct the data object with the timestamp for verification
    verification_data = {
        'data': saved_data['data'],
        'timestamp': rounded_mod_time
    }
    global _verify_signed_last_data
    _verify_signed_last_data = saved_data['data']

    # Serialize the data for verification
    data_to_verify = orjson.dumps(verification_data)

    # Attempt to verify the signature
    try:
        public_key.verify(
            signature,
            data_to_verify,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Verification successful: The data is intact and authentic.")
        return True
    except Exception:
        return False
    
verify_signed_data.get_last = get_last

def equal(k : rsa.RSAPrivateKey, dk : rsa.RSAPrivateKey) -> bool:
    # Extract public components from both the original and deserialized keys
    original_public_numbers = k.public_key().public_numbers()
    deserialized_public_numbers = dk.public_key().public_numbers()

    # Compare the public components
    assert original_public_numbers.n == deserialized_public_numbers.n, "Modulus mismatch"
    assert original_public_numbers.e == deserialized_public_numbers.e, "Public exponent mismatch"

    # If the keys include private components, compare those too
    if isinstance(k, rsa.RSAPrivateKey) and isinstance(dk, rsa.RSAPrivateKey):
        assert k.private_numbers().d == dk.private_numbers().d, "Private exponent mismatch"
        assert k.private_numbers().p == dk.private_numbers().p, "Prime 1 mismatch"
        assert k.private_numbers().q == dk.private_numbers().q, "Prime 2 mismatch"

