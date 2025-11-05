"""テストデータ生成モジュール"""
import random
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class TestData:
    """生成されたテストデータを保持するクラス"""
    nickname: str
    lastName: str
    firstName: str
    lastNameKana: str
    firstNameKana: str
    postalCode1: str
    postalCode2: str
    postalCode: str
    prefecture: str
    city: str
    address1: str
    address2: str
    phone1: str
    phone2: str
    phone3: str
    phone: str
    birthYear: int
    birthMonth: int
    birthDay: int
    birthDate: str
    gender: str


class TestDataGenerator:
    """テストデータを生成するクラス"""
    
    # データプール
    LAST_NAMES = ['田中', '山田', '佐藤', '鈴木', '高橋', '渡辺', '伊藤', '山本', '中村', '小林', 
                  '加藤', '吉田', '山口', '松本', '井上', '木村', '林', '清水', '岡田', '前田']
    
    FIRST_NAMES_MALE = ['太郎', '一郎', '健太', '大輔', '翔太', '拓也', '健二', '浩二', '隆', '誠', 
                        '直樹', '和也', '達也', '雄大', '翔']
    
    FIRST_NAMES_FEMALE = ['花子', '美咲', '愛', '優子', '真由美', '恵子', '陽子', '智子', '裕子', 
                          '明美', 'さくら', '綾', '舞', '葵', '結衣']
    
    LAST_NAMES_KANA = ['タナカ', 'ヤマダ', 'サトウ', 'スズキ', 'タカハシ', 'ワタナベ', 'イトウ', 
                       'ヤマモト', 'ナカムラ', 'コバヤシ', 'カトウ', 'ヨシダ', 'ヤマグチ', 'マツモト', 
                       'イノウエ', 'キムラ', 'ハヤシ', 'シミズ', 'オカダ', 'マエダ']
    
    FIRST_NAMES_KANA_MALE = ['タロウ', 'イチロウ', 'ケンタ', 'ダイスケ', 'ショウタ', 'タクヤ', 'ケンジ', 
                                'コウジ', 'タカシ', 'マコト', 'ナオキ', 'カズヤ', 'タツヤ', 'ユウダイ', 'ショウ']
    
    FIRST_NAMES_KANA_FEMALE = ['ハナコ', 'ミサキ', 'アイ', 'ユウコ', 'マユミ', 'ケイコ', 'ヨウコ', 
                               'トモコ', 'ユウコ', 'アケミ', 'サクラ', 'アヤ', 'マイ', 'アオイ', 'ユイ']
    
    NICKNAMES = [
        # かわいい系
        'ゆうちゃん', 'たかちゃん', 'まーくん', 'りょう', 'けんけん', 'みっちー', 'なおちゃん', 
        'しょうちゃん', 'まこっちゃん', 'だいちゃん', 'ゆきちゃん', 'あやちゃん', 'みーちゃん', 
        'さっちゃん', 'れいちゃん', 'ひろちゃん', 'かずちゃん', 'あっちゃん', 'のんちゃん', 
        'りんちゃん', 'ももちゃん', 'はるちゃん',
        # カジュアル系
        'ユウ', 'タカ', 'リョウ', 'ケン', 'ナオ', 'ショウ', 'マコト', 'ダイ', 'ユキ', 'アヤ', 
        'ミサ', 'レイ', 'ヒロ', 'カズ', 'アキ', 'ノゾミ', 'リン', 'モモ', 'ハル', 'ソラ', 'レン', 
        'カイ', 'ユイ', 'メイ',
        # 英語風
        'Ken', 'Taka', 'Yuki', 'Masa', 'Hiro', 'Kazu', 'Ryo', 'Shin', 'Jun', 'Dai', 'Rei', 'Mai', 
        'Aya', 'Mika', 'Tom', 'Mike', 'John', 'Kate', 'Emma', 'Lisa', 'Anna', 'Sara', 'Alex', 
        'Sam', 'Max', 'Leo', 'Luna',
        # 動物系
        'くま', 'うさぎ', 'ねこ', 'いぬ', 'とら', 'らいおん', 'ぱんだ', 'ひつじ', 'りす', 'ペンギン',
        # 食べ物系
        'もち', 'プリン', 'まめ', 'いちご', 'メロン', 'チョコ', 'クッキー', 'マカロン', 'だんご',
        # ゲーム風
        'ゲーマー太郎', 'プロゲーマー', '初心者です', 'エンジョイ勢', 'ガチ勢', 'のんびり', 'まったり',
        'ドラゴン', 'フェニックス', 'ナイト', 'ウィザード', 'ヒーラー', 'タンク', 'アサシン',
        # 一般的な名前系
        '太郎', '花子', '一郎', '次郎', '三郎', '桃太郎', '金太郎', '浦島太郎',
        '山田', '田中', '佐藤', '鈴木', '高橋', '渡辺', '伊藤', '山本',
        # 季節・自然系
        '春風', '夏海', '秋空', '冬雪', '桜', '紅葉', '青空', '星空', '月光', '太陽', '虹', '雲', '風',
        # 数字・記号系
        'user123', 'test456', 'guest789', 'player001', 'member999', 'No.1', 'No.99',
        # その他個性的
        '名無し', '通りすがり', '暇人', '見習い', '新人', 'ベテラン', '師匠', '弟子', '旅人', '冒険者',
        'ラッキー', 'ハッピー', 'スマイル', 'エンジェル', 'ドリーム', 'ミラクル', 'ワンダー'
    ]
    
    BUILDING_NAMES = ['グリーンハイツ', 'サンライズ', 'フローラル', 'メゾン青山', 'パークサイド', 
                      'リバーサイド', 'ハイツ桜', 'コーポ富士', 'ビューハイツ', 'シティハイム', 
                      'グランドール', 'エクセル', 'ロイヤル', 'パレス', 'レジデンス']
    
    # 住所データ（郵便番号、都道府県、市区町村）
    ADDRESS_DATA = [
        # 東京都
        {'postalCode': '100-0001', 'prefecture': '東京都', 'city': '千代田区千代田'},
        {'postalCode': '100-0005', 'prefecture': '東京都', 'city': '千代田区丸の内'},
        {'postalCode': '102-0072', 'prefecture': '東京都', 'city': '千代田区飯田橋'},
        {'postalCode': '150-0002', 'prefecture': '東京都', 'city': '渋谷区渋谷'},
        {'postalCode': '150-0001', 'prefecture': '東京都', 'city': '渋谷区神宮前'},
        {'postalCode': '151-0053', 'prefecture': '東京都', 'city': '渋谷区代々木'},
        {'postalCode': '160-0022', 'prefecture': '東京都', 'city': '新宿区新宿'},
        {'postalCode': '160-0023', 'prefecture': '東京都', 'city': '新宿区西新宿'},
        {'postalCode': '106-0032', 'prefecture': '東京都', 'city': '港区六本木'},
        {'postalCode': '107-0062', 'prefecture': '東京都', 'city': '港区南青山'},
        {'postalCode': '108-0014', 'prefecture': '東京都', 'city': '港区芝'},
        {'postalCode': '140-0001', 'prefecture': '東京都', 'city': '品川区北品川'},
        {'postalCode': '141-0031', 'prefecture': '東京都', 'city': '品川区西五反田'},
        {'postalCode': '153-0064', 'prefecture': '東京都', 'city': '目黒区下目黒'},
        {'postalCode': '154-0012', 'prefecture': '東京都', 'city': '世田谷区駒沢'},
        {'postalCode': '158-0094', 'prefecture': '東京都', 'city': '世田谷区玉川'},
        # 大阪府
        {'postalCode': '530-0001', 'prefecture': '大阪府', 'city': '大阪市北区梅田'},
        {'postalCode': '531-0072', 'prefecture': '大阪府', 'city': '大阪市北区豊崎'},
        {'postalCode': '540-0001', 'prefecture': '大阪府', 'city': '大阪市中央区城見'},
        {'postalCode': '541-0041', 'prefecture': '大阪府', 'city': '大阪市中央区北浜'},
        {'postalCode': '542-0081', 'prefecture': '大阪府', 'city': '大阪市中央区南船場'},
        {'postalCode': '550-0002', 'prefecture': '大阪府', 'city': '大阪市西区江戸堀'},
        {'postalCode': '556-0011', 'prefecture': '大阪府', 'city': '大阪市浪速区難波中'},
        {'postalCode': '590-0075', 'prefecture': '大阪府', 'city': '堺市堺区南花田口町'},
        {'postalCode': '560-0021', 'prefecture': '大阪府', 'city': '豊中市本町'},
        {'postalCode': '564-0051', 'prefecture': '大阪府', 'city': '吹田市豊津町'},
        # 神奈川県
        {'postalCode': '220-0011', 'prefecture': '神奈川県', 'city': '横浜市西区高島'},
        {'postalCode': '231-0062', 'prefecture': '神奈川県', 'city': '横浜市中区桜木町'},
        {'postalCode': '210-0007', 'prefecture': '神奈川県', 'city': '川崎市川崎区駅前本町'},
        {'postalCode': '211-0063', 'prefecture': '神奈川県', 'city': '川崎市中原区小杉町'},
        {'postalCode': '252-0236', 'prefecture': '神奈川県', 'city': '相模原市中央区富士見'},
        {'postalCode': '251-0052', 'prefecture': '神奈川県', 'city': '藤沢市藤沢'},
        {'postalCode': '248-0006', 'prefecture': '神奈川県', 'city': '鎌倉市小町'},
        # 愛知県
        {'postalCode': '450-0002', 'prefecture': '愛知県', 'city': '名古屋市中村区名駅'},
        {'postalCode': '460-0008', 'prefecture': '愛知県', 'city': '名古屋市中区栄'},
        {'postalCode': '461-0001', 'prefecture': '愛知県', 'city': '名古屋市東区泉'},
        {'postalCode': '464-0850', 'prefecture': '愛知県', 'city': '名古屋市千種区今池'},
        {'postalCode': '471-0027', 'prefecture': '愛知県', 'city': '豊田市喜多町'},
        # 福岡県
        {'postalCode': '810-0001', 'prefecture': '福岡県', 'city': '福岡市中央区天神'},
        {'postalCode': '812-0011', 'prefecture': '福岡県', 'city': '福岡市博多区博多駅前'},
        {'postalCode': '814-0001', 'prefecture': '福岡県', 'city': '福岡市早良区百道浜'},
        {'postalCode': '802-0001', 'prefecture': '福岡県', 'city': '北九州市小倉北区浅野'},
        # 北海道
        {'postalCode': '060-0001', 'prefecture': '北海道', 'city': '札幌市中央区北一条西'},
        {'postalCode': '060-0806', 'prefecture': '北海道', 'city': '札幌市北区北六条西'},
        {'postalCode': '040-0054', 'prefecture': '北海道', 'city': '函館市元町'},
        # 宮城県
        {'postalCode': '980-0021', 'prefecture': '宮城県', 'city': '仙台市青葉区中央'},
        {'postalCode': '980-0811', 'prefecture': '宮城県', 'city': '仙台市青葉区一番町'},
        # 京都府
        {'postalCode': '604-8005', 'prefecture': '京都府', 'city': '京都市中京区河原町通'},
        {'postalCode': '600-8216', 'prefecture': '京都府', 'city': '京都市下京区烏丸通'},
        # 群馬県
        {'postalCode': '371-0026', 'prefecture': '群馬県', 'city': '前橋市大手町'},
        {'postalCode': '371-0023', 'prefecture': '群馬県', 'city': '前橋市本町'},
        {'postalCode': '370-0849', 'prefecture': '群馬県', 'city': '高崎市八島町'},
        {'postalCode': '370-0829', 'prefecture': '群馬県', 'city': '高崎市高松町'},
        {'postalCode': '373-0851', 'prefecture': '群馬県', 'city': '太田市飯田町'},
        {'postalCode': '376-0011', 'prefecture': '群馬県', 'city': '桐生市相生町'},
        {'postalCode': '372-0812', 'prefecture': '群馬県', 'city': '伊勢崎市連取町'},
        # 栃木県
        {'postalCode': '320-0027', 'prefecture': '栃木県', 'city': '宇都宮市塙田'},
        {'postalCode': '320-0026', 'prefecture': '栃木県', 'city': '宇都宮市馬場通り'},
        {'postalCode': '320-0802', 'prefecture': '栃木県', 'city': '宇都宮市江野町'},
        {'postalCode': '321-0964', 'prefecture': '栃木県', 'city': '宇都宮市駅前通り'},
        {'postalCode': '324-0047', 'prefecture': '栃木県', 'city': '大田原市美原'},
        {'postalCode': '323-0023', 'prefecture': '栃木県', 'city': '小山市中央町'},
        {'postalCode': '328-0037', 'prefecture': '栃木県', 'city': '栃木市倭町'},
        {'postalCode': '326-0814', 'prefecture': '栃木県', 'city': '足利市通'},
        {'postalCode': '327-0842', 'prefecture': '栃木県', 'city': '佐野市奈良渕町'},
        # 静岡県
        {'postalCode': '420-0851', 'prefecture': '静岡県', 'city': '静岡市葵区黒金町'},
        {'postalCode': '420-0031', 'prefecture': '静岡県', 'city': '静岡市葵区呉服町'},
        {'postalCode': '420-0852', 'prefecture': '静岡県', 'city': '静岡市葵区紺屋町'},
        {'postalCode': '422-8067', 'prefecture': '静岡県', 'city': '静岡市駿河区南町'},
        {'postalCode': '424-0886', 'prefecture': '静岡県', 'city': '静岡市清水区草薙'},
        {'postalCode': '430-0926', 'prefecture': '静岡県', 'city': '浜松市中区砂山町'},
        {'postalCode': '430-0928', 'prefecture': '静岡県', 'city': '浜松市中区板屋町'},
        {'postalCode': '432-8002', 'prefecture': '静岡県', 'city': '浜松市中区富塚町'},
        {'postalCode': '410-0801', 'prefecture': '静岡県', 'city': '沼津市大手町'},
        {'postalCode': '411-0855', 'prefecture': '静岡県', 'city': '三島市本町'},
        {'postalCode': '417-0055', 'prefecture': '静岡県', 'city': '富士市永田町'},
        # 茨城県
        {'postalCode': '310-0011', 'prefecture': '茨城県', 'city': '水戸市三の丸'},
        {'postalCode': '310-0021', 'prefecture': '茨城県', 'city': '水戸市南町'},
        {'postalCode': '310-0026', 'prefecture': '茨城県', 'city': '水戸市泉町'},
        {'postalCode': '310-0061', 'prefecture': '茨城県', 'city': '水戸市北見町'},
        {'postalCode': '305-0031', 'prefecture': '茨城県', 'city': 'つくば市吾妻'},
        {'postalCode': '305-0032', 'prefecture': '茨城県', 'city': 'つくば市竹園'},
        {'postalCode': '305-0005', 'prefecture': '茨城県', 'city': 'つくば市天久保'},
        {'postalCode': '300-0036', 'prefecture': '茨城県', 'city': '土浦市大和町'},
        {'postalCode': '300-0043', 'prefecture': '茨城県', 'city': '土浦市中央'},
        {'postalCode': '317-0073', 'prefecture': '茨城県', 'city': '日立市幸町'},
        {'postalCode': '306-0023', 'prefecture': '茨城県', 'city': '古河市本町'},
        {'postalCode': '307-0001', 'prefecture': '茨城県', 'city': '結城市結城'}
    ]
    
    # 電話番号の市外局番（地域別）
    PHONE_AREA_CODES = {
        '東京都': ['03', '042', '0422', '0428'],
        '大阪府': ['06', '072', '0725', '0721'],
        '神奈川県': ['045', '044', '046', '0467'],
        '愛知県': ['052', '0561', '0565', '0586'],
        '福岡県': ['092', '093', '0940', '0942'],
        '北海道': ['011', '0138', '0166', '0154'],
        '宮城県': ['022', '0229', '0220', '0224'],
        '京都府': ['075', '0774', '0771', '0773'],
        '埼玉県': ['048', '049', '0480', '0495'],
        '千葉県': ['043', '047', '0470', '0476'],
        '兵庫県': ['078', '079', '0795', '0796'],
        '広島県': ['082', '084', '0823', '0829'],
        '群馬県': ['027', '0270', '0276', '0277'],
        '栃木県': ['028', '0282', '0283', '0284'],
        '静岡県': ['054', '053', '055', '0544'],
        '茨城県': ['029', '0296', '0297', '0299']
    }
    
    @classmethod
    def generate(cls) -> TestData:
        """テストデータを生成する"""
        # 性別を確率分布に従って選択
        gender_choice = random.random()
        if gender_choice < 0.05:
            gender = '回答したくない'
            is_male = random.random() > 0.5
        elif gender_choice < 0.5:
            gender = '男性'
            is_male = True
        elif gender_choice < 0.95:
            gender = '女性'
            is_male = False
        else:
            gender = 'その他'
            is_male = random.random() > 0.5
        
        # 名前を選択
        last_name = random.choice(cls.LAST_NAMES)
        last_name_index = cls.LAST_NAMES.index(last_name)
        last_name_kana = cls.LAST_NAMES_KANA[last_name_index] if last_name_index < len(cls.LAST_NAMES_KANA) else cls.LAST_NAMES_KANA[0]
        
        if is_male:
            first_name = random.choice(cls.FIRST_NAMES_MALE)
            first_name_kana = random.choice(cls.FIRST_NAMES_KANA_MALE)
        else:
            first_name = random.choice(cls.FIRST_NAMES_FEMALE)
            first_name_kana = random.choice(cls.FIRST_NAMES_KANA_FEMALE)
        
        # 生年月日を生成（1960-2005年）
        year = 1960 + random.randint(0, 45)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 28日までに制限
        
        # 住所を選択
        address_info = random.choice(cls.ADDRESS_DATA)
        postal_parts = address_info['postalCode'].split('-')
        postal_code1 = postal_parts[0]
        postal_code2 = postal_parts[1]
        prefecture = address_info['prefecture']
        city = address_info['city']
        
        # 電話番号を生成（70%が携帯、30%が固定）
        if random.random() < 0.7:
            # 携帯電話
            phone1 = random.choice(['070', '080', '090'])
            phone2 = str(random.randint(1000, 9999))
            phone3 = str(random.randint(1000, 9999))
        else:
            # 固定電話
            area_codes = cls.PHONE_AREA_CODES.get(prefecture, ['03'])
            phone1 = random.choice(area_codes)
            
            if len(phone1) == 2:  # 2桁の市外局番（例: 03）
                phone2 = str(random.randint(1000, 9999))
                phone3 = str(random.randint(1000, 9999))
            elif len(phone1) == 3:  # 3桁の市外局番
                phone2 = str(random.randint(100, 999))
                phone3 = str(random.randint(1000, 9999))
            else:  # 4桁の市外局番
                phone2 = str(random.randint(10, 99))
                phone3 = str(random.randint(1000, 9999))
        
        # 番地を生成
        address1 = f"{random.randint(1, 6)}-{random.randint(1, 20)}-{random.randint(1, 30)}"
        
        # 建物名を生成（30%の確率で追加）
        address2 = ''
        if random.random() > 0.3:
            building_name = random.choice(cls.BUILDING_NAMES)
            floor = random.randint(1, 12)
            room = str(random.randint(1, 8)).zfill(2)
            room_number = f"{floor}{room}"
            address2 = f"{building_name} {room_number}号室"
        
        # ニックネームを選択
        nickname = random.choice(cls.NICKNAMES)
        
        return TestData(
            nickname=nickname,
            lastName=last_name,
            firstName=first_name,
            lastNameKana=last_name_kana,
            firstNameKana=first_name_kana,
            postalCode1=postal_code1,
            postalCode2=postal_code2,
            postalCode=f"{postal_code1}-{postal_code2}",
            prefecture=prefecture,
            city=city,
            address1=address1,
            address2=address2,
            phone1=phone1,
            phone2=phone2,
            phone3=phone3,
            phone=f"{phone1}-{phone2}-{phone3}",
            birthYear=year,
            birthMonth=month,
            birthDay=day,
            birthDate=f"{year}年{month}月{day}日",
            gender=gender
        )

