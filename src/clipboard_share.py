"""クリップボード共有モジュール"""
import asyncio
import logging
from playwright.async_api import Page
from tenacity import retry, stop_after_attempt, wait_exponential

from .test_data_generator import TestData
from .config import Config

logger = logging.getLogger(__name__)


class ClipboardShareService:
    """クリップボード共有サイトへの情報保存を管理するクラス"""
    
    def __init__(self, page: Page):
        self.page = page
        self.config = Config()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def save_registration_data(
        self,
        email: str,
        password: str,
        test_data: TestData
    ) -> None:
        """登録情報をクリップボード共有サイトに保存する"""
        logger.info("クリップボード共有サイトにアクセス...")
        await self.page.goto(
            "https://clipboard-6wc.pages.dev/",
            wait_until="networkidle"
        )
        
        # パスワード入力フィールドを探す
        password_input = self.page.locator('input[type="password"]').first
        if await password_input.count() > 0:
            logger.info("パスワードを入力...")
            await password_input.fill(self.config.CLIPBOARD_PASSWORD)
        
        # テキストエリアまたは入力フィールドにデータを入力
        formatted_data = self._format_registration_data(email, password, test_data)
        
        # テキストエリアを探す
        textarea = self.page.locator('textarea').first
        if await textarea.count() > 0:
            logger.info("登録情報を入力...")
            await textarea.fill(formatted_data)
        else:
            # テキストエリアがない場合は、inputフィールドを探す
            text_input = self.page.locator('input[type="text"]').first
            if await text_input.count() > 0:
                logger.info("登録情報を入力...")
                await text_input.fill(formatted_data)
            else:
                # コンテンツ編集可能な要素を探す
                editable = self.page.locator('[contenteditable="true"]').first
                if await editable.count() > 0:
                    logger.info("登録情報を入力...")
                    await editable.fill(formatted_data)
                else:
                    logger.warning("入力フィールドが見つかりませんでした")
        
        # 保存ボタンをクリック（存在する場合）
        save_button = self.page.get_by_role("button", name="保存", exact=False).first
        if await save_button.count() > 0:
            await save_button.click()
            await asyncio.sleep(1)
        
        logger.info("登録情報の保存が完了しました")
    
    def _format_registration_data(
        self,
        email: str,
        password: str,
        test_data: TestData
    ) -> str:
        """登録情報をフォーマットする"""
        return f"""メールアドレス: {email}
パスワード: {password}
ニックネーム: {test_data.nickname}
姓名: {test_data.lastName} {test_data.firstName}
カタカナ: {test_data.lastNameKana} {test_data.firstNameKana}
郵便番号: {test_data.postalCode}
住所: {test_data.prefecture}{test_data.city}{test_data.address1}{' ' + test_data.address2 if test_data.address2 else ''}
電話番号: {test_data.phone}
生年月日: {test_data.birthDate}
性別: {test_data.gender}
"""

