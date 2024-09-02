import hashlib
import os

def md5_encrypt(text, salt=None):
    """
    使用MD5算法对输入的文本进行加密，可选择添加盐。

    :param text: 需要加密的文本
    :param salt: 可选的盐值，如果不提供则随机生成
    :return: 元组 (加密后的MD5字符串, 使用的盐值)
    """
    if salt is None:
        salt = os.urandom(16)  # 生成16字节的随机盐
    elif isinstance(salt, str):
        salt = salt.encode('utf-8')

    # 将盐和文本组合
    salted_text = salt + text.encode('utf-8')
    
    md5_hash = hashlib.md5()
    md5_hash.update(salted_text)
    return md5_hash.hexdigest(), salt

def verify_md5(text, hashed_text, salt):
    """
    验证文本是否匹配给定的哈希值。

    :param text: 待验证的文本
    :param hashed_text: 存储的哈希值
    :param salt: 使用的盐值
    :return: 布尔值，表示验证是否成功
    """
    new_hash, _ = md5_encrypt(text, salt)
    return new_hash == hashed_text

if __name__ == "__main__":
    sample_text = "Hello, World!"
    hashed_text, salt = md5_encrypt(sample_text)
    print(f"原始文本: {sample_text}")
    print(f"加密后的MD5: {hashed_text}")
    print(f"使用的盐: {salt.hex()}")

    # 验证
    is_valid = verify_md5(sample_text, hashed_text, salt)
    print(f"验证结果: {'成功' if is_valid else '失败'}")

    # 尝试验证错误的文本
    wrong_text = "Hello, World"
    is_valid = verify_md5(wrong_text, hashed_text, salt)
    print(f"错误文本验证结果: {'成功' if is_valid else '失败'}")
