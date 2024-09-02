import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class AESCipher:
    DEFAULT_KEY = b'This is a key123This is a key123'  # 32 bytes (256-bit)

    def __init__(self, key=None):
        self.key = key or self.DEFAULT_KEY

    def encrypt(self, plaintext, key=None):
        key = key or self.key
        iv = os.urandom(16)  # 128-bit IV
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext

    def decrypt(self, ciphertext, key=None):
        key = key or self.key
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext.decode()

# 测试代码
if __name__ == "__main__":
    cipher = AESCipher()

    # 使用默认密钥
    plaintext = "Hello, World!"
    print("原始明文:", plaintext)
    print("使用默认密钥加密，密钥是:", cipher.key)
    ciphertext = cipher.encrypt(plaintext)
    print("密文:", ciphertext)

    decrypted_text = cipher.decrypt(ciphertext)
    print("解密后的明文:", decrypted_text)
    assert decrypted_text == plaintext, "默认密钥解密失败"

    # 使用自定义密钥
    custom_key = os.urandom(32)  # 256-bit key
    print("\n原始明文:", plaintext)
    print("使用自定义密钥加密，密钥是:", custom_key)
    ciphertext_custom = cipher.encrypt(plaintext, key=custom_key)
    print("密文:", ciphertext_custom)

    decrypted_text_custom = cipher.decrypt(ciphertext_custom, key=custom_key)
    print("解密后的明文:", decrypted_text_custom)
    assert decrypted_text_custom == plaintext, "自定义密钥解密失败"

    print("\n所有测试通过！")