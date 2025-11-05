"""統合テスト"""
import pytest
from src.test_data_generator import TestDataGenerator


def test_data_generation():
    """テストデータ生成のテスト"""
    data = TestDataGenerator.generate()
    
    assert data.nickname
    assert data.lastName
    assert data.firstName
    assert data.lastNameKana
    assert data.firstNameKana
    assert data.postalCode
    assert data.prefecture
    assert data.city
    assert data.phone
    assert 1960 <= data.birthYear <= 2005
    assert 1 <= data.birthMonth <= 12
    assert 1 <= data.birthDay <= 28
    assert data.gender in ['回答したくない', '男性', '女性', 'その他']
    
    # 旧漢字・ローマ数字・特殊記号が含まれていないことを確認
    assert 'Ⅰ' not in data.lastName
    assert 'Ⅱ' not in data.lastName
    assert '①' not in data.lastName
    assert 'Ⅰ' not in data.firstName
    assert 'Ⅱ' not in data.firstName
    assert '①' not in data.firstName


def test_data_format():
    """テストデータのフォーマット確認"""
    data = TestDataGenerator.generate()
    
    # 郵便番号の形式確認
    assert len(data.postalCode1) == 3
    assert len(data.postalCode2) == 4
    assert data.postalCode == f"{data.postalCode1}-{data.postalCode2}"
    
    # 電話番号の形式確認
    assert len(data.phone1) >= 2
    assert len(data.phone2) >= 2
    assert len(data.phone3) == 4
    assert data.phone == f"{data.phone1}-{data.phone2}-{data.phone3}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

