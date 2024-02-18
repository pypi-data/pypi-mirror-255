from functools import cache
import typing

import platform

available_literal = typing.Literal["local", "gitraw", "url", "directInput"]

@cache
def getTargetKeyring():
    if platform.system() == "Windows":
        from keyring.backends.Windows import WinVaultKeyring
        target_keyring = WinVaultKeyring()
    elif platform.system() == "Linux":
        from keyring.backends.SecretService import SecretService
        target_keyring = SecretService()
    elif platform.system() == "Darwin":
        target_keyring = None
    else:
        import keyring
        target_keyring = keyring.get_keyring()

    if target_keyring is None:
        raise NotImplementedError("Platform not supported")
    
    return target_keyring