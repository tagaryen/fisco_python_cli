"""
Functions lifted from https://github.com/vbuterin/pybitcointools
"""
import hashlib
import hmac

from error.Error import exitError

from .Jacobian import (
    inv,
    fast_multiply,
    fast_add,
    jacobian_add,
    jacobian_multiply,
    from_jacobian
)

P = 115792089237316195423570985008687907853269984665640564039457584007908834671663  # type: int
N = 115792089237316195423570985008687907852837564279074904382605163141518161494337  # type: int  # noqa: E501
A = 0  # type: int  # noqa: E501
B = 7  # type: int  # noqa: E501
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240  # type: int  # noqa: E501
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424  # type: int  # noqa: E501
G = (Gx, Gy)  # type: Tuple[int, int]


def pad32(value: bytes) -> bytes:
    return value.rjust(32, b'\x00')

def int_to_big_endian(value: int) -> bytes:
    return value.to_bytes((value.bit_length() + 7) // 8 or 1, "big")

def big_endian_to_int(value: bytes) -> int:
    return int.from_bytes(value, "big")


def decode_public_key(public_key_bytes: bytes):
    left = big_endian_to_int(public_key_bytes[0:32])
    right = big_endian_to_int(public_key_bytes[32:64])
    return left, right


def encode_raw_public_key(left, right) -> bytes:
    return b''.join((
        pad32(int_to_big_endian(left)),
        pad32(int_to_big_endian(right)),
    ))


def private_key_to_public_key(private_key_bytes: bytes) -> bytes:
    private_key_as_num = big_endian_to_int(private_key_bytes)

    if private_key_as_num >= N:
        raise Exception("Invalid privkey")

    x,y = fast_multiply(G, private_key_as_num)
    public_key_bytes = encode_raw_public_key(x,y)
    return public_key_bytes


def compress_public_key(uncompressed_public_key_bytes: bytes) -> bytes:
    x, y = decode_public_key(uncompressed_public_key_bytes)
    if y % 2 == 0:
        prefix = b"\x02"
    else:
        prefix = b"\x03"
    return prefix + pad32(int_to_big_endian(x))


def decompress_public_key(compressed_public_key_bytes: bytes) -> bytes:
    if len(compressed_public_key_bytes) != 33:
        raise ValueError("Invalid compressed public key")

    prefix = compressed_public_key_bytes[0]
    if prefix not in (2, 3):
        raise ValueError("Invalid compressed public key")

    x = big_endian_to_int(compressed_public_key_bytes[1:])
    y_squared = (x**3 + A * x + B) % P
    y_abs = pow(y_squared, ((P + 1) // 4), P)

    if (prefix == 2 and y_abs & 1 == 1) or (prefix == 3 and y_abs & 1 == 0):
        y = (-y_abs) % P
    else:
        y = y_abs

    return encode_raw_public_key(x, y)


def deterministic_generate_k(msg_hash: bytes,
                             private_key_bytes: bytes,
                             digest_fn = hashlib.sha256) -> int:
    v_0 = b'\x01' * 32
    k_0 = b'\x00' * 32

    k_1 = hmac.new(k_0, v_0 + b'\x00' + private_key_bytes + msg_hash, digest_fn).digest()
    v_1 = hmac.new(k_1, v_0, digest_fn).digest()
    k_2 = hmac.new(k_1, v_1 + b'\x01' + private_key_bytes + msg_hash, digest_fn).digest()
    v_2 = hmac.new(k_2, v_1, digest_fn).digest()

    kb = hmac.new(k_2, v_2, digest_fn).digest()
    k = int.from_bytes(kb,"big")
    return k


def ecdsa_raw_sign(msg_hash: bytes,
                   private_key_bytes: bytes):
    z = int.from_bytes(msg_hash, "big")
    k = deterministic_generate_k(msg_hash, private_key_bytes)

    r, y = fast_multiply(G, k)
    s_raw = inv(k, N) * (z + r * big_endian_to_int(private_key_bytes)) % N

    v = 27 + ((y % 2) ^ (0 if s_raw * 2 < N else 1))
    s = s_raw if s_raw * 2 < N else N - s_raw

    return v - 27, r, s


def ecdsa_raw_verify(msg_hash: bytes,
                     r,
                     s,
                     public_key_bytes: bytes) -> bool:
    raw_public_key = decode_public_key(public_key_bytes)
    w = inv(s, N)
    z = int.from_bytes(msg_hash, "big")

    u1, u2 = z * w % N, r * w % N
    x, y = fast_add(
        fast_multiply(G, u1),
        fast_multiply(raw_public_key, u2),
    )
    return bool(r == x and (r % N) and (s % N))


def ecdsa_raw_recover(msg_hash: bytes,
                      v, r, s) -> bytes:
    v += 27

    if not (27 <= v <= 34):
        exitError("%d must in range 27-31" % v)

    x = r

    xcubedaxb = (x * x * x + A * x + B) % P
    beta = pow(xcubedaxb, (P + 1) // 4, P)
    y = beta if v % 2 ^ beta % 2 else (P - beta)
    # If xcubedaxb is not a quadratic residue, then r cannot be the x coord
    # for a point on the curve, and so the sig is invalid
    if (xcubedaxb - y * y) % P != 0 or not (r % N) or not (s % N):
        exitError("Invalid signature")
    z = big_endian_to_int(msg_hash)
    Gz = jacobian_multiply((Gx, Gy, 1), (N - z) % N)
    XY = jacobian_multiply((x, y, 1), s)
    Qr = jacobian_add(Gz, XY)
    Q = jacobian_multiply(Qr, inv(r, N))
    x,y = from_jacobian(Q)

    return encode_raw_public_key(x,y)
