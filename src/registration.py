"""TIF Streaming登録処理モジュール"""
import asyncio
import logging
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential

from .test_data_generator import TestData
from .config import Config

logger = logging.getLogger(__name__)


class TIFRegistrationService:
    """TIF Streaming会員登録処理を管理するクラス"""
    
    def __init__(self, page: Page):
        self.page = page
        self.config = Config()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def submit_email_address(self, email: str) -> None:
        """メールアドレスを送信する（第一段階）"""
        logger.info("TIF Streaming登録ページにアクセス...")
        
        # 現在のURLを確認
        current_url = self.page.url
        logger.info(f"現在のURL: {current_url}")
        
        # TIF Streamingサイトに遷移
        target_url = "https://official.idolfes.com/s/tifst/member/add?ima=0000"
        logger.info(f"TIF Streamingサイトに遷移します: {target_url}")
        
        try:
            await self.page.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=60000
            )
        except Exception as e:
            logger.error(f"ページ遷移に失敗しました: {e}")
            logger.info("ページ遷移を再試行します...")
            await asyncio.sleep(2)
            await self.page.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=60000
            )
        
        # 遷移後のURLを確認
        final_url = self.page.url
        logger.debug(f"遷移後のURL: {final_url}")
        
        if "official.idolfes.com" not in final_url:
            logger.warning(f"想定外のURLに遷移しました: {final_url}")
            raise ValueError(f"TIF Streamingサイトへの遷移に失敗しました。現在のURL: {final_url}")
        
        # Cloudflareのチャレンジを待つ
        await self._wait_for_cloudflare_challenge()
        
        # ページが完全に読み込まれるまで待つ（エラーハンドリング付き）
        try:
            await asyncio.sleep(3)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception as e:
            logger.warning(f"networkidle待機中にエラー: {e}。domcontentloadedを確認します...")
            try:
                await self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                logger.warning("ページ読み込み待機をスキップします...")
        
        logger.info("メールアドレスを入力...")
        # メールアドレス入力フィールドを探す（複数の方法を試す）
        email_input = self.page.locator('input[type="email"]').first
        if await email_input.count() == 0:
            email_input = self.page.locator('input[name="email"]').first
        if await email_input.count() == 0:
            email_input = self.page.get_by_role("textbox", name="メールアドレス")
        await email_input.fill(email)
        
        logger.info("利用規約に同意...")
        # label要素を直接クリックする方法を優先
        checkbox_label = self.page.locator('label.CpCheckBoxList__label').first
        if await checkbox_label.count() > 0:
            logger.debug("label要素をクリックします...")
            await checkbox_label.click()
            await asyncio.sleep(0.5)
        else:
            # フォールバック: チェックボックスを直接操作
            checkbox = self.page.locator('input[name="terms_agree"]').first
            if await checkbox.count() > 0:
                logger.debug("チェックボックスを直接クリックします...")
                await checkbox.click()
                await asyncio.sleep(0.5)
            else:
                # 最後の手段: テキストでlabelを探す
                logger.warning("label要素が見つかりません。テキストで検索します...")
                checkbox_label = self.page.get_by_text("利用規約、プライバシーポリシーに同意する", exact=False)
                await checkbox_label.click()
                await asyncio.sleep(0.5)
        
        # チェックされたことを確認
        checkbox = self.page.locator('input[name="terms_agree"]').first
        if await checkbox.count() > 0:
            await asyncio.sleep(0.5)
            is_checked = await checkbox.is_checked()
            if not is_checked:
                logger.warning("チェックボックスがチェックされていません。再度試行します...")
                # label要素を再度クリック
                checkbox_label = self.page.locator('label.CpCheckBoxList__label').first
                if await checkbox_label.count() > 0:
                    await checkbox_label.click()
                    await asyncio.sleep(0.5)
                    is_checked = await checkbox.is_checked()
                    if not is_checked:
                        logger.error("チェックボックスのクリックに失敗しました")
                        raise ValueError("利用規約のチェックボックスをクリックできませんでした")
        
        # 送信ボタンが有効になるまで待つ（最大10秒）
        submit_button = self.page.get_by_role("button", name="メールアドレスを送信")
        try:
            await submit_button.wait_for(state="attached", timeout=2000)
            # ボタンがdisabledでなくなるまで待つ
            for i in range(20):  # 最大2秒待つ
                is_disabled = await submit_button.is_disabled()
                if not is_disabled:
                    logger.info("送信ボタンが有効になりました")
                    break
                await asyncio.sleep(0.1)
            else:
                logger.warning("送信ボタンが有効にならない可能性があります")
        except Exception as e:
            logger.warning(f"送信ボタンの状態確認中にエラーが発生しました: {e}")
        
        logger.info("メールアドレスを送信...")
        submit_button = self.page.get_by_role("button", name="メールアドレスを送信")
        await submit_button.click()
        
        # 送信完了を待つ（複数の方法を試す）
        try:
            # 方法1: URL変化を待つ
            await self.page.wait_for_url("**/member/add", timeout=10000)
            logger.info("メールアドレスの送信が完了しました（URL変化を検出）")
        except PlaywrightTimeoutError:
            # 方法2: 成功メッセージの表示を待つ
            try:
                success_message = self.page.locator('text="送信しました"').first
                await success_message.wait_for(state="visible", timeout=5000)
                logger.info("メールアドレスの送信が完了しました（成功メッセージを検出）")
            except PlaywrightTimeoutError:
                # 方法3: ネットワークアイドルを待つ
                await asyncio.sleep(2)
                logger.info("メールアドレスの送信が完了しました（待機時間経過）")
    
    async def _wait_for_cloudflare_challenge(self, max_wait: int = 60) -> None:
        """Cloudflareのチャレンジが完了するまで待つ"""
        try:
            for i in range(max_wait):
                try:
                    # Cloudflareのチャレンジページをチェック
                    page_title = await self.page.title()
                    page_url = self.page.url
                    
                    # Cloudflareのチャレンジが検出された場合
                    if "Just a moment" in page_title or "checking your browser" in page_title.lower() or "challenge" in page_url.lower():
                        logger.info(f"Cloudflareチャレンジを検出しました。待機中... ({i+1}秒)")
                        await asyncio.sleep(2)
                        continue
                    
                    # チャレンジが完了したと判断
                    if i > 0:
                        logger.info("Cloudflareチャレンジが完了しました")
                    break
                except Exception as e:
                    logger.warning(f"チャレンジ確認中にエラー: {e}")
                    await asyncio.sleep(1)
                    continue
        except Exception as e:
            logger.warning(f"Cloudflareチャレンジ待機中にエラーが発生しました: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fill_registration_form(self, test_data: TestData, password: str) -> None:
        """会員情報入力フォームにデータを入力する（第二段階）"""
        logger.info("会員情報入力フォームに入力中...")
        
        # パスワード
        logger.debug("パスワードを入力...")
        password_input = self.page.locator('input[name="pass"]')
        await password_input.fill(password)
        
        # ニックネーム
        logger.debug("ニックネームを入力...")
        nickname_input = self.page.locator('input[name="1"]')
        await nickname_input.fill(test_data.nickname)
        
        # 姓
        logger.debug("姓を入力...")
        last_name_input = self.page.locator('input[name="2"]')
        await last_name_input.fill(test_data.lastName)
        
        # 名
        logger.debug("名を入力...")
        first_name_input = self.page.locator('input[name="3"]')
        await first_name_input.fill(test_data.firstName)
        
        # セイ（カタカナ）
        logger.debug("セイ（カタカナ）を入力...")
        last_name_kana_input = self.page.locator('input[name="4"]')
        await last_name_kana_input.fill(test_data.lastNameKana)
        
        # メイ（カタカナ）
        logger.debug("メイ（カタカナ）を入力...")
        first_name_kana_input = self.page.locator('input[name="5"]')
        await first_name_kana_input.fill(test_data.firstNameKana)
        
        # 郵便番号
        logger.debug("郵便番号を入力...")
        postal1_input = self.page.locator('input[name="6[1]"]')
        await postal1_input.fill(test_data.postalCode1)
        postal2_input = self.page.locator('input[name="6[2]"]')
        await postal2_input.fill(test_data.postalCode2)
        
        # 郵便番号で住所を自動入力（ボタンが存在する場合）
        try:
            auto_input_btn = self.page.get_by_role("button", name="郵便番号で", exact=False)
            await auto_input_btn.click()
            await asyncio.sleep(1)  # 住所入力の完了を待つ
        except PlaywrightTimeoutError:
            logger.warning("郵便番号自動入力ボタンが見つかりませんでした")
        
        # 都道府県
        logger.debug("都道府県を選択...")
        prefecture_select = self.page.locator('select[name="7"]')
        await prefecture_select.select_option(label=test_data.prefecture)
        
        # 市区町村
        logger.debug("市区町村を入力...")
        city_input = self.page.locator('input[name="8"]')
        await city_input.fill(test_data.city)
        
        # 以降の住所
        logger.debug("以降の住所を入力...")
        address1_input = self.page.locator('input[name="9"]')
        await address1_input.fill(test_data.address1)
        
        # マンション・ビル名（空でない場合のみ）
        if test_data.address2:
            logger.debug("マンション・ビル名を入力...")
            address2_input = self.page.locator('input[name="10"]')
            await address2_input.fill(test_data.address2)
        
        # 電話番号
        logger.debug("電話番号を入力...")
        phone1_input = self.page.locator('input[name="11[1]"]')
        await phone1_input.fill(test_data.phone1)
        phone2_input = self.page.locator('input[name="11[2]"]')
        await phone2_input.fill(test_data.phone2)
        phone3_input = self.page.locator('input[name="11[3]"]')
        await phone3_input.fill(test_data.phone3)
        
        # 生年月日
        logger.debug("生年月日を選択...")
        year_select = self.page.locator('select[name="12[1]"]')
        await year_select.select_option(value=str(test_data.birthYear))
        month_select = self.page.locator('select[name="12[2]"]')
        await month_select.select_option(value=str(test_data.birthMonth))
        day_select = self.page.locator('select[name="12[3]"]')
        await day_select.select_option(value=str(test_data.birthDay))
        
        # 性別（label要素をクリックする方式に変更）
        logger.debug("性別を選択...")
        if test_data.gender == "回答したくない":
            gender_value = "0"
        elif test_data.gender == "男性":
            gender_value = "1"
        elif test_data.gender == "女性":
            gender_value = "2"
        else:  # その他
            gender_value = "3"
        
        # ラジオボタンのlabel要素を探してクリック
        gender_label = self.page.locator(f'label[for="CpRadioBtns_13_{gender_value}"]').first
        if await gender_label.count() > 0:
            logger.debug(f"性別のlabel要素をクリック: gender_value={gender_value}")
            await gender_label.click()
        else:
            # フォールバック: input要素を直接操作（force=Trueで強制的にクリック）
            logger.debug(f"性別のinput要素を強制クリック: gender_value={gender_value}")
            gender_radio = self.page.locator(f'input[name="13"][value="{gender_value}"]')
            await gender_radio.check(force=True)
        
        # フォーム送信ボタンが有効になるまで待つ
        await asyncio.sleep(2)
        
        # 送信ボタンの状態を確認
        submit_button = self.page.get_by_role("button", name="送信する")
        is_disabled = await submit_button.is_disabled()
        
        if is_disabled:
            logger.warning("送信ボタンが無効です。入力内容を確認してください")
            # スクリーンショットを保存
            await self.page.screenshot(path="form_error.png", full_page=True)
            raise ValueError("フォームの入力に問題があります")
        
        logger.info("送信ボタンをクリック...")
        await submit_button.click()
        
        # 確認画面への遷移を待つ
        await asyncio.sleep(3)
        logger.info("確認画面に遷移しました")
        
        # 確認画面で「登録する」ボタンをクリック
        logger.info("確認画面で「登録する」ボタンをクリック...")
        confirm_button = self.page.get_by_role("button", name="登録する")
        await confirm_button.click()
        
        # 登録完了を待つ
        await asyncio.sleep(3)
        logger.info("会員登録が完了しました")

