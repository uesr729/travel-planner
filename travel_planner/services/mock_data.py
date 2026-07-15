"""Mock data generation for fallback when external APIs are unavailable.

Contains built-in data for 20+ Chinese cities and detailed itinerary data
for 5 core cities (Beijing, Shanghai, Chengdu, Xi'an, Hangzhou).

IMPORTANT: The `generate_mock_itinerary()` function is updated to prioritise
real POI (Point of Interest) data from the Amap API when available.
"""
import random
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================
# 20+ Chinese city coordinates database
# ============================================================
CITY_COORDS = {
    "北京": {"lat": 39.9042, "lng": 116.4074},
    "上海": {"lat": 31.2304, "lng": 121.4737},
    "广州": {"lat": 23.1291, "lng": 113.2644},
    "深圳": {"lat": 22.5431, "lng": 114.0579},
    "成都": {"lat": 30.5728, "lng": 104.0668},
    "杭州": {"lat": 30.2741, "lng": 120.1551},
    "西安": {"lat": 34.3416, "lng": 108.9398},
    "重庆": {"lat": 29.4316, "lng": 106.9123},
    "武汉": {"lat": 30.5928, "lng": 114.3055},
    "南京": {"lat": 32.0603, "lng": 118.7969},
    "苏州": {"lat": 31.2990, "lng": 120.5853},
    "昆明": {"lat": 25.0389, "lng": 102.7183},
    "丽江": {"lat": 26.8721, "lng": 100.2299},
    "三亚": {"lat": 18.2528, "lng": 109.5120},
    "厦门": {"lat": 24.4798, "lng": 118.0894},
    "青岛": {"lat": 36.0671, "lng": 120.3826},
    "大连": {"lat": 38.9140, "lng": 121.6147},
    "长沙": {"lat": 28.2282, "lng": 112.9388},
    "哈尔滨": {"lat": 45.8038, "lng": 126.5350},
    "拉萨": {"lat": 29.6500, "lng": 91.1000},
    "桂林": {"lat": 25.2736, "lng": 110.2900},
    "敦煌": {"lat": 40.1421, "lng": 94.6619},
}

# ============================================================
# Detailed data for 5 core cities
# ============================================================
CITY_DATA = {
    "北京": {
        "spots": [
            {"name": "天安门广场", "lat": 39.9042, "lng": 116.3974, "cost": 0,
             "category": "景点", "description": "世界上最大的城市广场，观看升旗仪式"},
            {"name": "故宫博物院", "lat": 39.9163, "lng": 116.3972, "cost": 60,
             "category": "历史", "description": "明清两代的皇家宫殿，世界文化遗产"},
            {"name": "颐和园", "lat": 39.9999, "lng": 116.2755, "cost": 30,
             "category": "园林", "description": "中国古典园林的巅峰之作，昆明湖与万寿山"},
            {"name": "天坛公园", "lat": 39.8822, "lng": 116.4066, "cost": 15,
             "category": "历史", "description": "明清帝王祭天的场所，祈年殿是北京地标"},
            {"name": "八达岭长城", "lat": 40.3541, "lng": 116.0078, "cost": 40,
             "category": "古迹", "description": "世界文化遗产，万里长城的精华段"},
            {"name": "南锣鼓巷", "lat": 39.9380, "lng": 116.4047, "cost": 0,
             "category": "美食", "description": "北京最古老的街区之一，胡同文化代表"},
            {"name": "鸟巢/水立方", "lat": 39.9905, "lng": 116.3910, "cost": 50,
             "category": "现代", "description": "2008年奥运会主场馆，现代建筑地标"},
            {"name": "798艺术区", "lat": 39.9840, "lng": 116.4950, "cost": 0,
             "category": "艺术", "description": "由老工厂改造的艺术园区，极具文艺气息"},
            {"name": "恭王府", "lat": 39.9353, "lng": 116.3855, "cost": 40,
             "category": "历史", "description": "清代规模最大的一座王府，和珅的府邸"},
            {"name": "北海公园", "lat": 39.9255, "lng": 116.3893, "cost": 10,
             "category": "园林", "description": "中国现存最古老、最完整的皇家园林之一"},
        ],
        "restaurants": [
            {"name": "全聚德烤鸭", "cost": 150, "type": "晚餐",
             "recommendation": "北京烤鸭代表品牌，推荐烤鸭套餐"},
            {"name": "护国寺小吃", "cost": 30, "type": "早餐",
             "recommendation": "北京传统小吃集合，豆汁、焦圈、豌豆黄"},
            {"name": "炸酱面馆", "cost": 35, "type": "午餐",
             "recommendation": "正宗老北京炸酱面，面条劲道"},
            {"name": "东来顺涮肉", "cost": 120, "type": "晚餐",
             "recommendation": "百年老字号铜锅涮羊肉"},
            {"name": "簋街小龙虾", "cost": 100, "type": "晚餐",
             "recommendation": "北京最著名美食街，麻辣小龙虾"},
            {"name": "庆丰包子铺", "cost": 25, "type": "早餐",
             "recommendation": "北京老字号包子铺，猪肉大葱包子"},
            {"name": "大董烤鸭", "cost": 200, "type": "晚餐",
             "recommendation": "高端烤鸭体验，创意菜品丰富"},
        ],
        "accommodations": [
            {"name": "北京市中心酒店", "cost": 300, "note": "含早餐，近地铁"},
            {"name": "王府井附近民宿", "cost": 250, "note": "性价比高，交通便利"},
            {"name": "特色四合院酒店", "cost": 400, "note": "体验老北京胡同文化"},
        ],
    },
    "上海": {
        "spots": [
            {"name": "外滩", "lat": 31.2400, "lng": 121.4900, "cost": 0,
             "category": "景点", "description": "上海的城市名片，万国建筑博览群"},
            {"name": "东方明珠塔", "lat": 31.2397, "lng": 121.4997, "cost": 199,
             "category": "现代", "description": "上海地标建筑，登塔俯瞰黄浦江"},
            {"name": "豫园", "lat": 31.2272, "lng": 121.4903, "cost": 30,
             "category": "园林", "description": "明代江南园林，城隍庙商圈"},
            {"name": "迪士尼乐园", "lat": 31.1433, "lng": 121.6570, "cost": 475,
             "category": "亲子", "description": "中国大陆首座迪士尼主题乐园"},
            {"name": "南京路步行街", "lat": 31.2340, "lng": 121.4720, "cost": 0,
             "category": "购物", "description": "中国最著名的商业步行街"},
            {"name": "上海博物馆", "lat": 31.2303, "lng": 121.4730, "cost": 0,
             "category": "文化", "description": "中国古代艺术博物馆，馆藏丰富"},
            {"name": "田子坊", "lat": 31.2110, "lng": 121.4640, "cost": 0,
             "category": "艺术", "description": "上海弄堂文化代表，文艺小店聚集"},
            {"name": "武康大楼", "lat": 31.2140, "lng": 121.4350, "cost": 0,
             "category": "景点", "description": "上海经典历史建筑，网红打卡地"},
        ],
        "restaurants": [
            {"name": "南翔馒头店", "cost": 60, "type": "午餐",
             "recommendation": "豫园老字号，招牌蟹粉小笼包"},
            {"name": "老吉士酒家", "cost": 120, "type": "晚餐",
             "recommendation": "上海本帮菜代表，红烧肉必点"},
            {"name": "大壶春生煎", "cost": 25, "type": "早餐",
             "recommendation": "上海生煎老字号，底部酥脆"},
            {"name": "小杨生煎", "cost": 30, "type": "午餐",
             "recommendation": "连锁生煎品牌，皮薄馅大"},
            {"name": "福1088", "cost": 200, "type": "晚餐",
             "recommendation": "高端本帮菜，精致上海味道"},
        ],
        "accommodations": [
            {"name": "外滩附近酒店", "cost": 350, "note": "观黄浦江夜景，近地铁"},
            {"name": "南京路步行街酒店", "cost": 280, "note": "购物便利，位置中心"},
            {"name": "静安区精品民宿", "cost": 320, "note": "安静舒适，法租界风情"},
        ],
    },
    "成都": {
        "spots": [
            {"name": "大熊猫繁育研究基地", "lat": 30.7262, "lng": 104.1480, "cost": 55,
             "category": "亲子", "description": "近距离观赏大熊猫，全球最大熊猫繁育机构"},
            {"name": "宽窄巷子", "lat": 30.6700, "lng": 104.0580, "cost": 0,
             "category": "美食", "description": "成都历史街区，美食与文化体验"},
            {"name": "锦里古街", "lat": 30.6450, "lng": 104.0480, "cost": 0,
             "category": "美食", "description": "武侯祠旁的古街，成都小吃集合地"},
            {"name": "武侯祠", "lat": 30.6450, "lng": 104.0480, "cost": 50,
             "category": "历史", "description": "纪念诸葛亮的祠庙，三国文化核心"},
            {"name": "杜甫草堂", "lat": 30.6600, "lng": 104.0320, "cost": 50,
             "category": "文化", "description": "诗圣杜甫的故居，古典园林建筑"},
            {"name": "青城山", "lat": 30.8940, "lng": 103.5690, "cost": 90,
             "category": "自然", "description": "道教名山，青城天下幽"},
            {"name": "都江堰", "lat": 31.0070, "lng": 103.6190, "cost": 80,
             "category": "古迹", "description": "世界文化遗产，2000年历史水利工程"},
            {"name": "春熙路", "lat": 30.6600, "lng": 104.0820, "cost": 0,
             "category": "购物", "description": "成都最繁华的商业街，IFS熊猫打卡"},
        ],
        "restaurants": [
            {"name": "小龙坎老火锅", "cost": 120, "type": "晚餐",
             "recommendation": "成都火锅代表，麻辣鲜香"},
            {"name": "钟水饺", "cost": 20, "type": "早餐",
             "recommendation": "成都老字号，红油水饺一绝"},
            {"name": "陈麻婆豆腐", "cost": 45, "type": "午餐",
             "recommendation": "百年老店，正宗麻婆豆腐"},
            {"name": "夫妻肺片总店", "cost": 40, "type": "午餐",
             "recommendation": "四川名菜夫妻肺片起源店"},
            {"name": "龙抄手", "cost": 25, "type": "早餐",
             "recommendation": "成都经典抄手，皮薄馅嫩"},
            {"name": "蜀大侠火锅", "cost": 130, "type": "晚餐",
             "recommendation": "特色火锅，武侠主题风格"},
        ],
        "accommodations": [
            {"name": "春熙路附近酒店", "cost": 260, "note": "市中心，购物美食便利"},
            {"name": "宽窄巷子民宿", "cost": 300, "note": "老成都风格，体验慢生活"},
            {"name": "锦里附近客栈", "cost": 200, "note": "经济实惠，近景区"},
        ],
    },
    "西安": {
        "spots": [
            {"name": "兵马俑博物馆", "lat": 34.3853, "lng": 109.2740, "cost": 120,
             "category": "历史", "description": "世界第八大奇迹，秦始皇陵陪葬坑"},
            {"name": "大雁塔", "lat": 34.2183, "lng": 108.9581, "cost": 40,
             "category": "历史", "description": "唐代高僧玄奘收藏经书之地"},
            {"name": "钟楼", "lat": 34.2610, "lng": 108.9420, "cost": 30,
             "category": "历史", "description": "西安地标建筑，中国现存最大钟楼"},
            {"name": "西安城墙", "lat": 34.2650, "lng": 108.9510, "cost": 54,
             "category": "古迹", "description": "中国现存规模最大、保存最完整的古城墙"},
            {"name": "回民街", "lat": 34.2620, "lng": 108.9380, "cost": 0,
             "category": "美食", "description": "西安著名美食街，小吃种类繁多"},
            {"name": "陕西历史博物馆", "lat": 34.2240, "lng": 108.9530, "cost": 0,
             "category": "文化", "description": "华夏文明的宝库，馆藏丰富"},
            {"name": "华清宫", "lat": 34.3650, "lng": 109.2060, "cost": 120,
             "category": "历史", "description": "唐代皇家温泉宫殿，杨贵妃沐浴处"},
            {"name": "大唐不夜城", "lat": 34.2170, "lng": 108.9580, "cost": 0,
             "category": "景点", "description": "夜晚灯光秀，唐风文化步行街"},
        ],
        "restaurants": [
            {"name": "老孙家羊肉泡馍", "cost": 35, "type": "午餐",
             "recommendation": "西安名吃，百年老店"},
            {"name": "贾三灌汤包子", "cost": 30, "type": "早餐",
             "recommendation": "回民街名店，皮薄汤多"},
            {"name": "西安饭庄", "cost": 100, "type": "晚餐",
             "recommendation": "老字号陕菜馆，葫芦鸡必点"},
            {"name": "魏家凉皮", "cost": 15, "type": "午餐",
             "recommendation": "连锁品牌，秘制凉皮"},
            {"name": "同盛祥", "cost": 80, "type": "晚餐",
             "recommendation": "中华老字号，泡馍和陕菜"},
        ],
        "accommodations": [
            {"name": "钟楼附近酒店", "cost": 240, "note": "市中心，交通便利"},
            {"name": "大雁塔附近民宿", "cost": 200, "note": "安静，夜景优美"},
            {"name": "回民街客栈", "cost": 180, "note": "美食街旁，经济实惠"},
        ],
    },
    "杭州": {
        "spots": [
            {"name": "西湖", "lat": 30.2590, "lng": 120.1550, "cost": 0,
             "category": "自然", "description": "世界文化遗产，人间天堂的核心"},
            {"name": "断桥残雪", "lat": 30.2650, "lng": 120.1530, "cost": 0,
             "category": "景点", "description": "西湖十景之一，白蛇传传说地"},
            {"name": "雷峰塔", "lat": 30.2370, "lng": 120.1480, "cost": 40,
             "category": "历史", "description": "西湖标志性建筑，登塔俯瞰全景"},
            {"name": "灵隐寺", "lat": 30.2440, "lng": 120.0980, "cost": 75,
             "category": "文化", "description": "千年古刹，佛教禅宗名寺"},
            {"name": "龙井茶村", "lat": 30.2220, "lng": 120.1180, "cost": 0,
             "category": "自然", "description": "西湖龙井原产地，体验采茶制茶"},
            {"name": "宋城", "lat": 30.1800, "lng": 120.1300, "cost": 320,
             "category": "景点", "description": "大型宋文化主题公园，宋城千古情"},
            {"name": "西溪湿地", "lat": 30.2750, "lng": 120.0550, "cost": 80,
             "category": "自然", "description": "城市湿地公园，天然氧吧"},
            {"name": "河坊街", "lat": 30.2480, "lng": 120.1680, "cost": 0,
             "category": "美食", "description": "杭州历史街区，传统小吃聚集地"},
        ],
        "restaurants": [
            {"name": "楼外楼", "cost": 150, "type": "晚餐",
             "recommendation": "百年老店，西湖醋鱼创始人"},
            {"name": "知味观", "cost": 80, "type": "午餐",
             "recommendation": "杭州名小吃，小笼包和猫耳朵"},
            {"name": "奎元馆", "cost": 40, "type": "早餐",
             "recommendation": "百年面馆，虾爆鳝面"},
            {"name": "外婆家", "cost": 70, "type": "午餐",
             "recommendation": "杭州家常菜，性价比高"},
            {"name": "绿茶餐厅", "cost": 80, "type": "晚餐",
             "recommendation": "融合菜餐厅，环境雅致"},
        ],
        "accommodations": [
            {"name": "西湖边酒店", "cost": 350, "note": "湖景房，出门即西湖"},
            {"name": "龙井村民宿", "cost": 280, "note": "茶园环绕，远离喧嚣"},
            {"name": "河坊街客栈", "cost": 220, "note": "老城区，美食便利"},
        ],
    },
}

# Weather data for different cities (月平均数据)
WEATHER_MOCK = {
    "北京": [
        {"month": 1, "temp_high": 2, "temp_low": -8, "weather": "晴", "humidity": 40},
        {"month": 4, "temp_high": 20, "temp_low": 8, "weather": "晴", "humidity": 45},
        {"month": 7, "temp_high": 31, "temp_low": 22, "weather": "多云", "humidity": 70},
        {"month": 10, "temp_high": 19, "temp_low": 8, "weather": "晴", "humidity": 55},
    ],
    "上海": [
        {"month": 1, "temp_high": 8, "temp_low": 1, "weather": "多云", "humidity": 70},
        {"month": 4, "temp_high": 20, "temp_low": 12, "weather": "阴", "humidity": 75},
        {"month": 7, "temp_high": 33, "temp_low": 25, "weather": "多云", "humidity": 80},
        {"month": 10, "temp_high": 22, "temp_low": 15, "weather": "晴", "humidity": 70},
    ],
}

# Preference-based spots selection weights
PREFERENCE_KEYWORDS = {
    "美食": ["美食", "餐饮", "小吃"],
    "文化": ["文化", "博物馆", "历史"],
    "自然": ["自然", "园林", "公园"],
    "购物": ["购物"],
    "亲子": ["亲子"],
    "历史": ["历史", "古迹", "古建筑"],
    "艺术": ["艺术"],
}


def get_city_coords(city: str) -> Optional[dict]:
    """Get coordinates for a city."""
    return CITY_COORDS.get(city)


def _select_spots(city_data: dict, preferences: str, days: int) -> list:
    """Select appropriate spots based on preferences."""
    all_spots = city_data["spots"]
    pref_keywords = [p.strip() for p in preferences.split(",") if p.strip()]

    if pref_keywords:
        scored = []
        for spot in all_spots:
            score = 0
            for pref in pref_keywords:
                keywords = PREFERENCE_KEYWORDS.get(pref, [pref])
                if any(k in spot["description"] or k in spot["category"] for k in keywords):
                    score += 1
            scored.append((spot, score))

        scored.sort(key=lambda x: -x[1])
        selected = [s[0] for s in scored if s[1] > 0]
        remaining = [s[0] for s in scored if s[1] == 0]
        selected.extend(remaining)
    else:
        selected = all_spots.copy()

    # Allocate spots per day (2-3 per day)
    spots_per_day = max(2, min(3, len(selected) // days))
    return selected[: spots_per_day * days]


def _generate_daily_itinerary(
    city_data: dict, day_num: int, spots: list, city: str
) -> dict:
    """Generate a single day's itinerary."""
    time_slots = [
        ("上午", "08:00", "12:00"),
        ("下午", "13:00", "17:00"),
        ("晚上", "18:00", "21:00"),
    ]

    day_spots = []
    for i, spot in enumerate(spots[:3]):
        slot = time_slots[i] if i < len(time_slots) else time_slots[-1]
        day_spots.append(
            {
                "name": spot["name"],
                "time_slot": slot[0],
                "start_time": slot[1],
                "end_time": slot[2],
                "description": spot["description"],
                "cost": spot["cost"],
                "lat": spot["lat"],
                "lng": spot["lng"],
                "category": spot.get("category", "景点"),
                "duration_hours": 2.5,
            }
        )

    # Select meals
    restaurants = city_data.get("restaurants", [])
    breakfast = [r for r in restaurants if r["type"] == "早餐"]
    lunch = [r for r in restaurants if r["type"] == "午餐"]
    dinner = [r for r in restaurants if r["type"] == "晚餐"]
    other = [r for r in restaurants if r["type"] not in ("早餐", "午餐", "晚餐")]

    def pick(items):
        return random.choice(items) if items else None

    meals = []
    for meal in [pick(breakfast), pick(lunch), pick(dinner), pick(other)]:
        if meal:
            meals.append(
                {
                    "type": meal["type"],
                    "recommendation": meal["recommendation"],
                    "restaurant": meal["name"],
                    "cost": meal["cost"],
                }
            )

    # Select accommodation
    accommodations = city_data.get("accommodations", [])
    accommodation = random.choice(accommodations) if accommodations else None

    return {
        "day_number": day_num,
        "title": f"第{day_num}天 — {city}探索之旅",
        "spots": day_spots,
        "meals": meals,
        "accommodation": {
            "name": accommodation["name"] if accommodation else "市区酒店",
            "cost": accommodation["cost"] if accommodation else 200,
            "note": accommodation["note"] if accommodation else "经济实惠",
        }
        if accommodation
        else None,
    }


def _build_generic_city_data(city: str) -> dict:
    """Build reasonable generic city data for any city not in CITY_DATA.

    Generates spots, restaurants, and accommodations dynamically using the city name,
    so users can input any destination and get a meaningful itinerary.
    """
    # Try to get city-level coordinates for reasonable map display
    coords = get_city_coords(city)
    base_lat = coords["lat"] if coords else 30.0
    base_lng = coords["lng"] if coords else 110.0

    # Generate spots with small random offsets from city center for visual spread
    random.seed(city)  # deterministic per city
    offsets = [
        (random.uniform(-0.03, 0.03), random.uniform(-0.03, 0.03)) for _ in range(10)
    ]
    random.seed()  # reset seed

    # Generic spot templates that work for any city
    generic_spots = [
        {"name": f"{city}市中心广场", "lat": round(base_lat + offsets[0][0], 4),
         "lng": round(base_lng + offsets[0][1], 4), "cost": 0,
         "category": "景点", "description": f"{city}的城市中心，感受当地氛围"},
        {"name": f"{city}老街", "lat": round(base_lat + offsets[1][0], 4),
         "lng": round(base_lng + offsets[1][1], 4), "cost": 0,
         "category": "美食", "description": f"体验{city}传统风情，品尝地道小吃"},
        {"name": f"{city}博物馆", "lat": round(base_lat + offsets[2][0], 4),
         "lng": round(base_lng + offsets[2][1], 4), "cost": 30,
         "category": "文化", "description": f"了解{city}的历史文化与发展变迁"},
        {"name": f"{city}公园", "lat": round(base_lat + offsets[3][0], 4),
         "lng": round(base_lng + offsets[3][1], 4), "cost": 0,
         "category": "自然", "description": f"{city}最大的城市公园，休闲散步好去处"},
        {"name": f"{city}艺术中心", "lat": round(base_lat + offsets[4][0], 4),
         "lng": round(base_lng + offsets[4][1], 4), "cost": 20,
         "category": "艺术", "description": f"{city}的文艺地标，展览与演出不断"},
        {"name": f"{city}购物步行街", "lat": round(base_lat + offsets[5][0], 4),
         "lng": round(base_lng + offsets[5][1], 4), "cost": 0,
         "category": "购物", "description": f"{city}最繁华的商业街，时尚与美食汇聚"},
        {"name": f"{city}滨江/湖畔步道", "lat": round(base_lat + offsets[6][0], 4),
         "lng": round(base_lng + offsets[6][1], 4), "cost": 0,
         "category": "自然", "description": f"漫步{city}水岸，欣赏城市天际线"},
        {"name": f"{city}古寺/古塔", "lat": round(base_lat + offsets[7][0], 4),
         "lng": round(base_lng + offsets[7][1], 4), "cost": 25,
         "category": "历史", "description": f"{city}的历史古迹，感受岁月沉淀"},
        {"name": f"{city}夜市", "lat": round(base_lat + offsets[8][0], 4),
         "lng": round(base_lng + offsets[8][1], 4), "cost": 0,
         "category": "美食", "description": f"{city}最热闹的夜市，各种美食琳琅满目"},
        {"name": f"{city}观景台", "lat": round(base_lat + offsets[9][0], 4),
         "lng": round(base_lng + offsets[9][1], 4), "cost": 50,
         "category": "景点", "description": f"登高俯瞰{city}全景，城市风光尽收眼底"},
    ]

    generic_restaurants = [
        {"name": f"{city}本地餐厅", "cost": 80, "type": "午餐",
         "recommendation": f"品尝{city}地道美食，招牌菜值得一试"},
        {"name": f"{city}特色小吃店", "cost": 30, "type": "早餐",
         "recommendation": f"{city}特色早点，开启美好一天"},
        {"name": f"{city}老字号酒楼", "cost": 120, "type": "晚餐",
         "recommendation": f"{city}口碑老店，经典菜品不容错过"},
        {"name": f"{city}网红餐厅", "cost": 90, "type": "午餐",
         "recommendation": f"{city}人气餐厅，环境优雅味道好"},
        {"name": f"{city}夜市大排档", "cost": 60, "type": "晚餐",
         "recommendation": f"{city}最接地气的路边美食"},
        {"name": f"{city}早茶/早点铺", "cost": 25, "type": "早餐",
         "recommendation": f"{city}传统早点，品种丰富"},
        {"name": f"{city}融合菜馆", "cost": 100, "type": "晚餐",
         "recommendation": f"{city}创新融合菜，味蕾新体验"},
    ]

    generic_accommodations = [
        {"name": f"{city}市中心酒店", "cost": 280, "note": f"位于{city}核心区域，交通便利"},
        {"name": f"{city}精品民宿", "cost": 220, "note": f"温馨舒适，体验{city}本地生活"},
        {"name": f"{city}景观酒店", "cost": 350, "note": f"高层观景房，俯瞰{city}美景"},
    ]

    return {
        "spots": generic_spots,
        "restaurants": generic_restaurants,
        "accommodations": generic_accommodations,
    }


def _build_city_data_with_real_poi(city: str) -> dict:
    """Build city data, prioritising real POI from Amap API.

    1. Try to fetch real attractions via Amap API
    2. On success: merge real spots with preset/generic food & accommodation
    3. On failure: fall back to preset data (known city) or generic data (unknown city)
    """
    # Start with a base that has restaurants and accommodations
    if city in CITY_DATA:
        # Known city: clone preset data (we may replace spots with real POI)
        base = {
            "spots": list(CITY_DATA[city]["spots"]),
            "restaurants": list(CITY_DATA[city]["restaurants"]),
            "accommodations": list(CITY_DATA[city]["accommodations"]),
        }
    else:
        base = _build_generic_city_data(city)

    # Try to get real POI attractions from Amap
    try:
        from travel_planner.services.poi_service import search_attractions

        real_pois = search_attractions(city)
        if real_pois and len(real_pois) >= 3:
            logger.info(
                f"Using {len(real_pois)} real POIs from Amap API for '{city}'"
            )
            base["spots"] = real_pois
        else:
            logger.info(
                f"Amap returned {len(real_pois) if real_pois else 0} POIs "
                f"for '{city}' (need >= 3), keeping local data"
            )
    except Exception as e:
        logger.warning(f"Failed to fetch real POI for '{city}': {e}")

    return base


def _get_budget_tier(budget: int, days: int) -> str:
    """Determine budget tier based on daily per-person budget.
    
    Returns one of: "budget", "comfort", "luxury"
    """
    daily = budget / max(1, days)
    if daily < 200:
        return "budget"
    elif daily < 500:
        return "comfort"
    else:
        return "luxury"


def generate_mock_itinerary(
    destination: str, days: int, budget: int, preferences: str = ""
) -> str:
    """Generate a complete mock itinerary for the given destination.

    Data priority:
      1. Real POI from Amap API (if AMAP_API_KEY configured) → real attractions
      2. City-specific preset data (Beijing, Shanghai, etc.)
      3. Dynamically generated generic data (any other city)

    Falls back to the next level if the higher one fails.

    Returns a JSON string matching the expected itinerary schema.
    """
    city_data = _build_city_data_with_real_poi(destination)

    # Budget-aware cost selection: filter restaurants and accommodations by tier
    tier = _get_budget_tier(budget, days)
    if tier == "budget":
        city_data["restaurants"] = [r for r in city_data["restaurants"] if r["cost"] <= 50]
        city_data["accommodations"] = [a for a in city_data["accommodations"] if a["cost"] <= 250]
    elif tier == "comfort":
        city_data["restaurants"] = [r for r in city_data["restaurants"] if 30 <= r["cost"] <= 150]
        city_data["accommodations"] = [a for a in city_data["accommodations"] if 200 <= a["cost"] <= 400]
    else:  # luxury
        city_data["restaurants"] = [r for r in city_data["restaurants"] if r["cost"] >= 80]
        city_data["accommodations"] = [a for a in city_data["accommodations"] if a["cost"] >= 300]

    # Select and distribute spots
    selected_spots = _select_spots(city_data, preferences, days)
    spots_per_day = max(2, min(3, len(selected_spots) // max(1, days)))

    days_data = []
    total_cost = 0

    for day in range(1, days + 1):
        start_idx = (day - 1) * spots_per_day
        end_idx = min(start_idx + spots_per_day, len(selected_spots))
        day_spots = selected_spots[start_idx:end_idx]

        if not day_spots:
            day_spots = random.sample(
                city_data["spots"], min(2, len(city_data["spots"]))
            )

        day_itinerary = _generate_daily_itinerary(
            city_data, day, day_spots, destination
        )
        days_data.append(day_itinerary)

        # Calculate day cost
        for spot in day_itinerary["spots"]:
            total_cost += spot["cost"]
        for meal in day_itinerary["meals"]:
            total_cost += meal["cost"]
        if day_itinerary["accommodation"]:
            total_cost += day_itinerary["accommodation"]["cost"]

    # Build summary
    accommodation_total = sum(
        d["accommodation"]["cost"]
        for d in days_data
        if d.get("accommodation")
    )
    meal_total = sum(
        m["cost"] for d in days_data for m in d.get("meals", [])
    )
    spots_total = sum(
        s["cost"] for d in days_data for s in d.get("spots", [])
    )

    summary = {
        "total_budget": budget,
        "estimated_total": total_cost,
        "spots_cost": spots_total,
        "meal_cost": meal_total,
        "accommodation_cost": accommodation_total,
        "transport_cost": max(0, total_cost - spots_total - meal_total - accommodation_total),
        "other_cost": 0,
    }

    tips = [
        f"建议提前预订热门景点门票，{destination}的旅游旺季人流量较大",
        f"{destination}交通便利，建议使用地铁出行避免堵车",
        "出行前请查看当地天气预报，合理安排衣物",
        f"按照预算¥{budget}，建议预留20%应急资金",
        "行程中的餐饮推荐可根据实际口味调整",
    ]

    result = {
        "days": days_data,
        "summary": summary,
        "tips": tips,
    }

    return json.dumps(result, ensure_ascii=False)


def generate_mock_weather(city: str, days: int) -> list:
    """Generate mock weather data for a city."""
    import math
    from datetime import datetime, timedelta

    today = datetime.now()
    weather_list = []

    base_temp = 25  # default
    base_weather = "晴"
    base_humidity = 60

    if city in WEATHER_MOCK:
        month = today.month
        # Find nearest month data
        nearest = min(WEATHER_MOCK[city], key=lambda x: abs(x["month"] - month))
        base_temp = (nearest["temp_high"] + nearest["temp_low"]) / 2
        base_weather = nearest["weather"]
        base_humidity = nearest["humidity"]

    for i in range(days):
        date = today + timedelta(days=i)
        temp_variation = random.uniform(-3, 3)
        weather_list.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "temp": round(base_temp + temp_variation, 1),
                "temp_high": round(base_temp + 5 + temp_variation, 1),
                "temp_low": round(base_temp - 5 + temp_variation, 1),
                "weather": base_weather,
                "icon": "01d",
                "humidity": min(
                    100, max(20, base_humidity + random.randint(-10, 10))
                ),
            }
        )

    return weather_list
