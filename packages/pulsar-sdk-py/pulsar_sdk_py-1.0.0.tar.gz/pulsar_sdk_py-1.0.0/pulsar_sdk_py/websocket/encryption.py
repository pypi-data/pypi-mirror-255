import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA2ykDfyQtt4vQAJg7td4K
2KPqa5TkpQ1Xtk4/egymDjQsnicm1kZfeFVsrgDB60fdW0amR+O4fMj+2gcH1eRD
o09fjuIx5qhFVcz4q2ZWIbERUp//7vjG2vaSBg9YxwLh/sQaqiWTW639UIEyT6BX
Q/A8Nv+951u1Nu5Tme5xiB92pJDh0FYU55gkjI3a58ObUG2KLNacyNhTC34vBPQi
JMaOrdjv7XoqlYVJJbNTKwRPmhnnkSQVK5YV7qmjgX81ZfKJjIoqRHorFTIzy+X3
PBsoIoam4+1665MNJ27TcEg+qITvDOfPfan8+WEyeXgWEalsWaQ/lFTC+ER3pgbE
eOH61+nTTIeaGNv24JQU2V/T9sS7np9Vlw7edEfYXTSGimTGBVK2Dk8Vj70lTR65
DRFro3mbzmtIjqxCapl9Mlz03bPOXNNJB8oar7wj4BaYqMHYj3VbBO3effURRivM
jlyQXAHu20TYhUYP4ZhKgvjKv0b/OB0LsM+uQAVguRpDA61qNjaXH8dSuNAIT1yu
4+en0xcXORyfMmOlZM+C+gD+lMDU5ZUc4xDQMKMjSyiK5lW3Mz7dYgfaJEh0thP0
dG4M6ZfaThj99W9eyAy2/oNOmvd9i96QKd25cW4ty3FJvN8GrjLN8N/nM+UaONZW
Gse4ls8k+SNowhPJ1YT6+IkCAwEAAQ==
-----END PUBLIC KEY-----
"""

PUBLIC_KEY = serialization.load_pem_public_key(
    PUBLIC_KEY_PEM.encode(),
    backend=default_backend(),
)


def encrypt_message(message: str) -> str:
    # Encode the message to bytes
    message_bytes = message.encode()
    # Encrypt the message bytes
    encrypted_message = PUBLIC_KEY.encrypt(
        message_bytes, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    # Encode the encrypted message in base64 and decode to get a string
    return base64.b64encode(encrypted_message).decode()
