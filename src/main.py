"""メインスクリプト"""
import asyncio
import logging
import sys
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from .config import Config
    from .test_data_generator import TestDataGenerator
    from .temp_mail import TempMailService
    from .registration import TIFRegistrationService
    from .clipboard_share import ClipboardShareService
    from .csv_manager import CSVManager
except ImportError:
    # 直接実行時のためのフォールバック
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.config import Config
    from src.test_data_generator import TestDataGenerator
    from src.temp_mail import TempMailService
    from src.registration import TIFRegistrationService
    from src.clipboard_share import ClipboardShareService
    from src.csv_manager import CSVManager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('voteBot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class VoteBot:
    """自動会員登録Bot"""
    
    def __init__(self, config: Config):
        self.config = config
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
    
    async def initialize(self):
        """ブラウザを初期化する"""
        logger.info("ブラウザを起動中...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.config.HEADLESS,
            slow_mo=1000  # より人間らしい動作のため遅延を増やす
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ja-JP',
            timezone_id='Asia/Tokyo',
            permissions=['geolocation'],
            extra_http_headers={
                'Accept-Language': 'ja,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
        )
        self.page = await self.context.new_page()
        
        # Cloudflareのチャレンジを回避するための対策
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            window.navigator.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ja-JP', 'ja', 'en-US', 'en']
            });
        """)
        
        logger.info("ブラウザの初期化が完了しました")
    
    async def cleanup(self):
        """リソースをクリーンアップする"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("ブラウザを終了しました")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def run(self):
        """メイン処理を実行する"""
        try:
            # 1. テストデータ生成
            logger.info("=" * 60)
            logger.info("テストデータを生成中...")
            logger.info("=" * 60)
            test_data = TestDataGenerator.generate()
            logger.info(f"生成されたデータ:")
            logger.info(f"  ニックネーム: {test_data.nickname}")
            logger.info(f"  姓名: {test_data.lastName} {test_data.firstName}")
            logger.info(f"  郵便番号: {test_data.postalCode}")
            logger.info(f"  住所: {test_data.prefecture}{test_data.city}")
            
            # 2. 捨てメアドで期限つきアドレス作成（専用ページを使用）
            logger.info("=" * 60)
            logger.info("捨てメアドで期限つきアドレスを作成中...")
            logger.info("=" * 60)
            
            # 捨てメアド用の新しいページを作成
            temp_mail_page = await self.context.new_page()
            temp_mail_service = TempMailService(temp_mail_page, self.context)
            email_address = await temp_mail_service.create_temporary_address()
            logger.info(f"作成されたメールアドレス: {email_address}")
            
            # メールアドレス作成後、少し待機
            await asyncio.sleep(2)
            
            # 3. TIF Streamingサイトでメールアドレス登録
            logger.info("=" * 60)
            logger.info("TIF Streamingサイトでメールアドレスを登録中...")
            logger.info("=" * 60)
            registration_service = TIFRegistrationService(self.page)
            await registration_service.submit_email_address(email_address)
            
            # 4. メール受信待機（3-5秒）
            logger.info("=" * 60)
            logger.info("検証メールの受信を待機中...")
            logger.info("=" * 60)
            await asyncio.sleep(5)  # メール送信の完了を待つ
            
            # 5. 検証URLクリック（捨てメアドページで確認）
            verification_url = await temp_mail_service.wait_for_verification_email()
            logger.info(f"検証URL: {verification_url}")
            
            # 捨てメアドページを閉じる
            await temp_mail_page.close()
            
            # 検証ページに移動
            try:
                await self.page.goto(verification_url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                logger.warning(f"networkidle待機中にエラー: {e}。domcontentloadedで再試行...")
                await self.page.goto(verification_url, wait_until="domcontentloaded", timeout=30000)
            
            # ページが完全に読み込まれるまで少し待つ
            await asyncio.sleep(2)
            
            # 6. 生成されたテストデータで会員情報入力
            logger.info("=" * 60)
            logger.info("会員情報を入力中...")
            logger.info("=" * 60)
            password = self.config.TEST_USER_PASSWORD
            await registration_service.fill_registration_form(test_data, password)
            
            # 7. CSVファイルにアカウント情報を保存
            logger.info("=" * 60)
            logger.info("CSVファイルにアカウント情報を保存中...")
            logger.info("=" * 60)
            csv_manager = CSVManager()
            csv_manager.save_account(email_address, password, test_data)
            
            # 8. クリップボード共有サイトへ全情報保存
            logger.info("=" * 60)
            logger.info("クリップボード共有サイトに情報を保存中...")
            logger.info("=" * 60)
            clipboard_service = ClipboardShareService(self.page)
            await clipboard_service.save_registration_data(email_address, password, test_data)
            
            logger.info("=" * 60)
            logger.info("すべての処理が正常に完了しました！")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"エラーが発生しました: {e}", exc_info=True)
            
            # エラー時のスクリーンショット保存
            if self.config.SCREENSHOT_ON_ERROR and self.page:
                screenshot_path = Path("error_screenshot.png")
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                logger.info(f"エラー時のスクリーンショットを保存しました: {screenshot_path}")
            
            raise


async def main():
    """メイン関数"""
    config = Config()
    bot = VoteBot(config)
    
    try:
        await bot.initialize()
        await bot.run()
    except KeyboardInterrupt:
        logger.info("ユーザーによって中断されました")
    except Exception as e:
        logger.error(f"致命的なエラーが発生しました: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await bot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

