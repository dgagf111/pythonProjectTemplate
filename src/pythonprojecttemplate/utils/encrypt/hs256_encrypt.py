import hmac
import hashlib
import os

def hs256_encrypt(text, secret_key=None):
    """
    使用HS256 (HMAC-SHA256) 算法对输入的文本进行加密。

    :param text: 需要加密的文本
    :param secret_key: 可选的密钥，如果不提供则随机生成
    :return: 元组 (加密后的HS256字符串, 使用的密钥)
    """
    if secret_key is None:
        secret_key = os.urandom(32)  # 生成32字节的随机密钥
    elif isinstance(secret_key, str):
        secret_key = secret_key.encode('utf-8')

    # 使用HMAC-SHA256进行加密
    hmac_obj = hmac.new(secret_key, text.encode('utf-8'), hashlib.sha256)
    return hmac_obj.hexdigest(), secret_key

def verify_hs256(text, hashed_text, secret_key):
    """
    验证文本是否匹配给定的哈希值。

    :param text: 待验证的文本
    :param hashed_text: 存储的哈希值
    :param secret_key: 使用的密钥
    :return: 布尔值，表示验证是否成功
    """
    new_hash, _ = hs256_encrypt(text, secret_key)
    return new_hash == hashed_text

if __name__ == "__main__":
    sample_text = "Hello, World!"
    hashed_text, secret_key = hs256_encrypt(sample_text)
    print(f"原始文本: {sample_text}")
    print(f"加密后的HS256: {hashed_text}")
    print(f"使用的密钥: {secret_key.hex()}")

    # 验证
    is_valid = verify_hs256(sample_text, hashed_text, secret_key)
    print(f"验证结果: {'成功' if is_valid else '失败'}")

    # 尝试验证错误的文本
    wrong_text = "Hello, World"
    is_valid = verify_hs256(wrong_text, hashed_text, secret_key)
    print(f"错误文本验证结果: {'成功' if is_valid else '失败'}")
