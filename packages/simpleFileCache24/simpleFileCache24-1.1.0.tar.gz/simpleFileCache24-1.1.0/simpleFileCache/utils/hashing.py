import hashlib
import os
import typing

def hash_file(filename, algorithm='sha256', chunk_size=4096):
    """Hash a file with the specified algorithm and chunk size."""
    hash_algo = hashlib.new(algorithm)
    with open(filename, 'rb') as file:
        chunk = file.read(chunk_size)
        while chunk:
            hash_algo.update(chunk)
            chunk = file.read(chunk_size)
    return hash_algo.hexdigest()


def hash_bytes(data : bytes, algorithm='sha256'):
    """Hash bytes with the specified algorithm."""
    hash_algo = hashlib.new(algorithm)
    hash_algo.update(data)
    return hash_algo.hexdigest()

def verify_file_hash(fileblob : typing.Union[bytes, str], target_hash, algorithm='sha256'):
    """Verify the file hash against a target hash."""
    if isinstance(fileblob, str):
        computed_hash = hash_file(fileblob, algorithm)
    else:
        computed_hash = hash_bytes(fileblob, algorithm)
    return computed_hash == target_hash

def consistent_hash_file(path : str):
    """
    filename is equal to its own hash
    """
    filename = os.path.basename(path)
    return verify_file_hash(filename, filename)
    