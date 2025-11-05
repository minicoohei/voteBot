# TIF Streaming 自動会員登録テストスクリプト

捨てメアドサービス（kuku.lu）を利用したTIF Streamingサイトの会員登録プロセスを自動化するテストスクリプトです。

## 機能

- 期限つきの使い捨てメールアドレスの自動作成
- TIF Streamingサイトでの会員登録の自動化
- リアルな日本のテストデータ生成（名前、住所、電話番号など）
- クリップボード共有サイトへの登録情報保存

## セットアップ

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. Playwrightブラウザのインストール

```bash
uv run playwright install chromium
```

### 3. 環境変数の設定

`.env`ファイルを作成し、以下の設定を行います：

```env
HEADLESS=false
TIMEOUT=30000
RETRY_COUNT=3
CLIPBOARD_PASSWORD=hogehoge1234
TEST_USER_PASSWORD=TestPass123!
LOG_LEVEL=INFO
SCREENSHOT_ON_ERROR=true
```

## 使用方法

### 基本的な実行

```bash
uv run python src/main.py
```

### ヘッドレスモードで実行

```bash
HEADLESS=true uv run python src/main.py
```

### テスト実行

```bash
uv run pytest tests/
```

## プロジェクト構成

```
voteBot/
├── pyproject.toml          # uvプロジェクト設定
├── .env                   # 環境設定（要作成）
├── src/
│   ├── __init__.py
│   ├── main.py            # メインスクリプト
│   ├── config.py          # 設定管理
│   ├── test_data_generator.py  # テストデータ生成
│   ├── temp_mail.py       # 捨てメアド操作
│   ├── registration.py    # TIF登録処理
│   └── clipboard_share.py # クリップボード共有
└── tests/
    └── test_integration.py # 統合テスト
```

## テストデータ生成

スクリプトは以下のデータを自動生成します：

- **名前**: 日本の一般的な姓・名（20種類の姓、15種類の名）
- **ニックネーム**: 100種類以上（かわいい系、カジュアル系、英語風など）
- **住所**: 実際の郵便番号と住所の対応（東京、大阪、神奈川など）
- **電話番号**: 地域別市外局番または携帯電話番号
- **生年月日**: 1960-2005年のランダム生成
- **性別**: 確率分布に従った選択

## 注意事項

- このスクリプトはテスト目的で使用してください
- 実際のサービスに負荷をかけないよう、適切な間隔で実行してください
- 生成されるデータはテスト用のダミーデータです

## ライセンス

このプロジェクトはテスト目的で作成されています。
