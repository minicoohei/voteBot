"""設定管理モジュール"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

class Config:
    """アプリケーション設定"""
    
    # ブラウザ設定
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30000"))
    
    # 再試行設定
    RETRY_COUNT: int = int(os.getenv("RETRY_COUNT", "3"))
    
    # クリップボード共有設定
    CLIPBOARD_PASSWORD: str = os.getenv("CLIPBOARD_PASSWORD", "hogehoge1234")
    
    # テストユーザー設定（半角英数字の組み合わせ8〜15文字）
    TEST_USER_PASSWORD: str = os.getenv("TEST_USER_PASSWORD", "TestPass123")
    
    # ログ設定
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SCREENSHOT_ON_ERROR: bool = os.getenv("SCREENSHOT_ON_ERROR", "true").lower() == "true"
    
    # URL設定
    TEMP_MAIL_URL = "https://m.kuku.lu/ja.php"
    TEMP_MAIL_RECV_URL = "https://m.kuku.lu/recv.php"
    TIF_REGISTRATION_URL = "https://official.idolfes.com/s/tifst/member/add?ima=0000"
    CLIPBOARD_SHARE_URL = "https://clipboard-6wc.pages.dev/"

