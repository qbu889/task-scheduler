"""
加密工具单元测试
"""
import pytest
from app.utils.crypto import encrypt, decrypt


class TestCrypto:
    """加密解密工具测试类"""
    
    def test_encrypt_decrypt_normal(self):
        """测试正常的加密解密流程"""
        password = '12345678'
        encrypted = encrypt(password)
        decrypted = decrypt(encrypted)
        
        assert decrypted == password
        assert encrypted != password  # 加密后应该不同
    
    def test_encrypt_empty_string(self):
        """测试空字符串加密"""
        result = encrypt('')
        assert result == ''
    
    def test_decrypt_empty_string(self):
        """测试空字符串解密"""
        result = decrypt('')
        assert result == ''
    
    def test_encrypt_none(self):
        """测试None值加密"""
        result = encrypt(None)
        assert result == ''
    
    def test_decrypt_none(self):
        """测试None值解密"""
        result = decrypt(None)
        assert result == ''
    
    def test_encrypt_special_characters(self):
        """测试特殊字符加密"""
        password = 'p@ssw0rd!#$%^&*()'
        encrypted = encrypt(password)
        decrypted = decrypt(encrypted)
        
        assert decrypted == password
    
    def test_encrypt_chinese_characters(self):
        """测试中文字符加密"""
        password = '密码测试123'
        encrypted = encrypt(password)
        decrypted = decrypt(encrypted)
        
        assert decrypted == password
    
    def test_encrypt_long_string(self):
        """测试长字符串加密"""
        password = 'a' * 1000
        encrypted = encrypt(password)
        decrypted = decrypt(encrypted)
        
        assert decrypted == password
    
    def test_same_input_different_output(self):
        """测试相同输入产生不同密文（Fernet特性）"""
        password = 'test_password'
        encrypted1 = encrypt(password)
        encrypted2 = encrypt(password)
        
        # 两次加密结果应该不同（因为使用了随机IV）
        assert encrypted1 != encrypted2
        
        # 但解密后应该相同
        assert decrypt(encrypted1) == password
        assert decrypt(encrypted2) == password
    
    def test_invalid_ciphertext(self):
        """测试无效密文解密"""
        with pytest.raises(Exception):
            decrypt('invalid_ciphertext_12345')
