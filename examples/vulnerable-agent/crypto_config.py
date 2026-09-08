import ssl

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
minimum_version = ssl.TLSVersion.TLSv1_2
key_exchange = X25519PrivateKey.generate()
