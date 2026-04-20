"""
加密解密工具
使用Fernet对称加密算法
"""
from cryptography.fernet import Fernet
import base64
import os
import logging

logger = logging.getLogger(__name__)


def _get_key():
    """
    获取加密密钥
    
    Returns:
        bytes: 32字节的加密密钥
    """
    # 从环境变量获取密钥，如果没有则使用默认值（生产环境必须设置）
    key_str = os.getenv('ENCRYPTION_KEY', 'default-encryption-key-change-in-production')
    
    # 确保密钥长度为32字节
    if len(key_str) < 32:
        key_str = key_str.ljust(32, '0')
    elif len(key_str) > 32:
        key_str = key_str[:32]
    
    # 转换为base64编码的Fernet密钥
    return base64.urlsafe_b64encode(key_str.encode())


def encrypt(plaintext):
    """
    加密字符串
    
    Args:
        plaintext (str): 明文
        
    Returns:
        str: 密文（base64编码）
    """
    if not plaintext:
        return ''
    
    try:
        logger.debug("Encrypting sensitive data")
        fernet = Fernet(_get_key())
        encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
        result = base64.b64encode(encrypted_bytes).decode('utf-8')
        logger.debug("Encryption completed successfully")
        return result
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}", exc_info=True)
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt(ciphertext):
    """
    解密字符串
    
    Args:
        ciphertext (str): 密文（base64编码）
        
    Returns:
        str: 明文
    """
    if not ciphertext:
        return ''
    
    try:
        logger.debug("Decrypting sensitive data")
        fernet = Fernet(_get_key())
        encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'))
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        result = decrypted_bytes.decode('utf-8')
        logger.debug("Decryption completed successfully")
        return result
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}", exc_info=True)
        raise ValueError(f"Decryption failed: {str(e)}")
