from Cryptodome.Hash import keccak
from error.Error import exitError


def keccak256Hash(msg):
    if not isinstance(msg, bytes):
        exitError("Invalid type for hash. required bytes but get {}".format(type(msg)))

    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(msg)
    return keccak_hash.hexdigest()