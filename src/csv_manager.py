"""CSV管理モジュール"""
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .test_data_generator import TestData

logger = logging.getLogger(__name__)


class CSVManager:
    """アカウント情報をCSVファイルに保存するクラス"""
    
    def __init__(self, csv_path: str = "accounts.csv"):
        self.csv_path = Path(csv_path)
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """CSVファイルが存在しない場合はヘッダーを作成"""
        if not self.csv_path.exists():
            logger.info(f"CSVファイルを作成します: {self.csv_path}")
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    '登録日時',
                    'メールアドレス',
                    'パスワード',
                    'ニックネーム',
                    '姓',
                    '名',
                    'セイ',
                    'メイ',
                    '郵便番号',
                    '都道府県',
                    '市区町村',
                    '番地',
                    '建物名',
                    '電話番号',
                    '生年月日',
                    '性別'
                ])
    
    def save_account(
        self,
        email: str,
        password: str,
        test_data: TestData
    ) -> None:
        """アカウント情報をCSVに保存"""
        logger.info(f"アカウント情報をCSVに保存中: {email}")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                email,
                password,
                test_data.nickname,
                test_data.lastName,
                test_data.firstName,
                test_data.lastNameKana,
                test_data.firstNameKana,
                test_data.postalCode,
                test_data.prefecture,
                test_data.city,
                test_data.address1,
                test_data.address2,
                test_data.phone,
                test_data.birthDate,
                test_data.gender
            ])
        
        logger.info(f"CSVファイルに保存しました: {self.csv_path}")

