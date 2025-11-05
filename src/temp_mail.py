"""捨てメアド操作モジュール"""
import asyncio
import logging
import random
from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class TempMailService:
    """捨てメアドサービスの操作を管理するクラス"""
    
    def __init__(self, page: Page, context: BrowserContext = None):
        self.page = page
        self.context = context or page.context
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=5, max=20))
    async def create_temporary_address(self) -> str:
        """期限つきの使い捨てアドレスを作成する"""
        logger.info("捨てメアドサイトにアクセス中...")
        
        await self.page.goto("https://m.kuku.lu/ja.php", wait_until="domcontentloaded", timeout=60000)
        
        # 人間らしい動作（マウス移動、スクロール）
        await self._human_like_behavior()
        
        # Cloudflareのチャレンジを待つ
        await self._wait_for_cloudflare_challenge()
        
        # ページが完全に読み込まれるまで待つ（エラーハンドリング付き）
        try:
            await asyncio.sleep(2)
            await self.page.wait_for_load_state("domcontentloaded", timeout=20000)
        except Exception as e:
            logger.warning(f"ページ読み込み待機中にエラー: {e}。続行します...")
        
        logger.info("期限つきの使い捨てアドレスを追加ボタンをクリック...")
        await self.page.get_by_role("button", name="期限つきの使い捨てアドレスを追加").click()
        
        # 利用規約同意ダイアログを待つ
        await asyncio.sleep(1)
        
        logger.info("利用規約に同意...")
        await self.page.get_by_role("button", name="はい").click()
        
        # アドレス作成を待つ
        await asyncio.sleep(2)
        
        logger.info("アドレスをコピー...")
        await self.page.get_by_role("button", name="アドレスをコピー").click()
        
        # アドレスを取得（クリップボードから読み取るか、ページから取得）
        await asyncio.sleep(1)
        
        # モーダル内のアドレスを取得
        email_address = await self.page.evaluate("""
            () => {
                const container = document.querySelector('#area-newaddress');
                if (!container) return null;
                const emailText = container.textContent;
                const match = emailText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/);
                return match ? match[0] : null;
            }
        """)
        
        if not email_address:
            # フォールバック: モーダルを閉じてから再度試行
            await self.page.get_by_role("button", name="閉じる").click()
            await asyncio.sleep(1)
            # リストから最新のアドレスを取得
            email_address = await self.page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    for (const btn of buttons) {
                        const text = btn.textContent || '';
                        if (text.includes('@') && text.includes('.')) {
                            const match = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/);
                            if (match) return match[0];
                        }
                    }
                    return null;
                }
            """)
        
        if not email_address:
            raise ValueError("メールアドレスの取得に失敗しました")
        
        logger.info(f"作成されたメールアドレス: {email_address}")
        return email_address
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def wait_for_verification_email(self, max_wait_seconds: int = 30) -> str:
        """検証メールを受信してURLを取得する"""
        logger.info("受信トレイにアクセス...")
        await self.page.goto("https://m.kuku.lu/recv.php", wait_until="networkidle")
        
        # メールが到着するまで待機
        wait_interval = 3
        elapsed = 0
        
        while elapsed < max_wait_seconds:
            logger.info(f"メール受信を確認中... ({elapsed}秒経過)")
            
            # 仮登録の本人確認メールを探す
            mail_button = self.page.get_by_role("button", name="仮登録の本人確認", exact=False)
            
            try:
                await mail_button.wait_for(state="visible", timeout=2000)
                logger.info("検証メールを発見しました")
                break
            except PlaywrightTimeoutError:
                await asyncio.sleep(wait_interval)
                elapsed += wait_interval
                # ページをリロード
                await self.page.reload(wait_until="networkidle")
        
        if elapsed >= max_wait_seconds:
            raise TimeoutError("検証メールの受信待ちがタイムアウトしました")
        
        # メールをクリック
        await mail_button.click()
        await asyncio.sleep(3)
        
        # メール本文からURLを抽出（複数の方法を試す）
        import re
        verification_url = None
        
        # 方法1: iframe内のリンクから取得（複数のリンクから/check/を含むものを選択）
        try:
            iframe = self.page.frame_locator('iframe[name*="area_maildata_iframe"]').first
            # すべてのリンクを取得してから、/check/を含むものをフィルタリング
            links = await iframe.locator('a[href*="official.idolfes.com"]').all()
            for link_element in links:
                href = await link_element.get_attribute("href")
                if href and "/check/" in href:
                    verification_url = href
                    logger.debug(f"iframe内のリンクから取得: {verification_url}")
                    break
        except Exception as e:
            logger.debug(f"iframe内のリンク取得に失敗: {e}")
        
        # 方法2: iframe内のテキストから正規表現で抽出
        if not verification_url:
            try:
                iframe_content = await self.page.evaluate("""
                    () => {
                        const iframes = document.querySelectorAll('iframe[name*="area_maildata_iframe"]');
                        for (const iframe of iframes) {
                            try {
                                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                                return iframeDoc.body?.innerText || iframeDoc.body?.textContent || '';
                            } catch (e) {
                                continue;
                            }
                        }
                        return '';
                    }
                """)
                
                if iframe_content:
                    # 正規表現でURLを抽出
                    url_pattern = r'https://official\.idolfes\.com/s/tifst/check/[a-f0-9]+'
                    match = re.search(url_pattern, iframe_content)
                    if match:
                        verification_url = match.group(0)
                        logger.debug(f"メール本文から正規表現で取得: {verification_url}")
            except Exception as e:
                logger.debug(f"メール本文からの抽出に失敗: {e}")
        
        # 方法3: ページ全体のテキストから抽出
        if not verification_url:
            try:
                page_text = await self.page.evaluate("() => document.body.innerText || document.body.textContent || ''")
                url_pattern = r'https://official\.idolfes\.com/s/tifst/check/[a-f0-9]+'
                match = re.search(url_pattern, page_text)
                if match:
                    verification_url = match.group(0)
                    logger.debug(f"ページ全体から正規表現で取得: {verification_url}")
            except Exception as e:
                logger.debug(f"ページ全体からの抽出に失敗: {e}")
        
        # 方法4: リンク要素から直接取得
        if not verification_url:
            try:
                links = await self.page.locator('a[href*="official.idolfes.com/s/tifst/check/"]').all()
                for link in links:
                    href = await link.get_attribute("href")
                    if href and "/check/" in href:
                        verification_url = href
                        logger.debug(f"リンク要素から取得: {verification_url}")
                        break
            except Exception as e:
                logger.debug(f"リンク要素からの取得に失敗: {e}")
        
        if not verification_url:
            raise ValueError("検証URLの取得に失敗しました")
        
        # gateway.exwa.orgのリダイレクトを解決
        if verification_url and "gateway.exwa.org" in verification_url:
            logger.info("リダイレクトURLを解決中...")
            
            # 方法1: URLパラメータをデコードして直接URLを抽出
            try:
                from urllib.parse import unquote
                # リダイレクトURLから実際のURLをデコード
                decoded_url = unquote(verification_url)
                logger.debug(f"デコードされたURL: {decoded_url}")
                
                # official.idolfes.com/s/tifst/check/のパターンを探す
                url_pattern = r'(https://official\.idolfes\.com/s/tifst/check/[a-f0-9]+)'
                match = re.search(url_pattern, decoded_url)
                if match:
                    verification_url = match.group(1)
                    logger.info(f"リダイレクトURLから抽出: {verification_url}")
                else:
                    logger.warning("リダイレクトURLから検証URLを抽出できませんでした")
                    # フォールバック: check/の後のハッシュを探す
                    match = re.search(r'/check/([a-f0-9]+)', verification_url)
                    if match:
                        verification_url = f"https://official.idolfes.com/s/tifst/check/{match.group(1)}"
                        logger.info(f"ハッシュから検証URLを構築: {verification_url}")
            except Exception as e:
                logger.warning(f"リダイレクトURLの解決に失敗: {e}")
                # エラーの場合でも、元のURLを使用して試行
                pass
        
        logger.info(f"検証URL: {verification_url}")
        return verification_url
    
    async def _wait_for_cloudflare_challenge(self, max_wait: int = 60) -> None:
        """Cloudflareのチャレンジが完了するまで待つ"""
        for i in range(max_wait // 2):  # 2秒間隔なのでmax_waitを2で割る
            try:
                # Cloudflareのチャレンジページをチェック
                page_title = await self.page.title()
                page_url = self.page.url
                
                # Cloudflareのチャレンジが検出された場合
                if "Just a moment" in page_title or "checking your browser" in page_title.lower() or "challenge" in page_url.lower():
                    logger.info(f"Cloudflareチャレンジを検出しました。待機中... ({(i+1)*2}秒)")
                    await asyncio.sleep(2)
                    continue
                
                # チャレンジが完了したと判断
                if i > 0:
                    logger.info("Cloudflareチャレンジが完了しました")
                break
            except Exception as e:
                logger.debug(f"チャレンジ確認中にエラー: {e}")
                # エラーが発生してもチャレンジが完了している可能性があるので続行
                break
    
    async def _human_like_behavior(self) -> None:
        """人間らしい動作をシミュレート（マウス移動、スクロールなど）"""
        try:
            # 少し待機
            await asyncio.sleep(random.uniform(1, 2))
            
            # マウスを少し動かす
            await self.page.mouse.move(100, 100)
            await asyncio.sleep(random.uniform(0.3, 0.7))
            
            # スクロール
            await self.page.evaluate("window.scrollTo(0, 200)")
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # 元に戻す
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(random.uniform(0.3, 0.7))
        except Exception as e:
            logger.debug(f"人間らしい動作シミュレーション中にエラー: {e}")

