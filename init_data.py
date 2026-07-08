from app import create_app
from extensions import db
from models.movie import Movie

def init_data():
    app = create_app()
    with app.app_context():
        # 删除旧数据
        Movie.query.delete()
        db.session.commit()

        movies = [
            Movie(title='肖申克的救赎', year=1994, genre='剧情 / 犯罪', duration=142, rating=9.7,
                  description='一场谋杀案使银行家安迪（蒂姆·罗宾斯 Tim Robbins 饰）蒙冤入狱，被判终身监禁。在肖申克监狱中，他经历了种种非人道的折磨，却从未放弃对自由的渴望。他凭借自己的专业知识为狱警处理税务，赢得了狱警的信任和庇护。同时，他用一把小锤子，花了近20年的时间，在牢房中挖出了一条通往自由的隧道。在一个风雨交加的夜晚，安迪成功越狱，重获新生。而他的好友瑞德（摩根·弗里曼 Morgan Freeman 饰）也在他的影响下，找到了生活的希望。这是一部关于希望、自由和友谊的经典之作，被誉为影史最伟大的电影之一。',
                  is_active=True, is_upcoming=False,
                  video_url='https://www.iqiyi.com/v_19rra0h3wg.html'),

            Movie(title='泰坦尼克号', year=1997, genre='剧情 / 爱情 / 灾难', duration=194, rating=9.5,
                  description='1912年4月10日，号称 \"世界工业史上的奇迹\" 的豪华客轮泰坦尼克号开始了它的处女航。年轻的贵族少女露丝（凯特·温丝莱特 Kate Winslet 饰）与穷画家杰克（莱昂纳多·迪卡普里奥 Leonardo DiCaprio 饰）在船上相遇，两人跨越阶级的鸿沟，迅速坠入爱河。然而，这艘号称 \"永不沉没\" 的巨轮，在航行途中意外撞上冰山，即将沉没。在生死关头，杰克把生的机会留给了露丝，自己却永远沉入了冰冷的大西洋。这段凄美的爱情故事，成为了影史永恒的经典，感动了全球无数观众。',
                  is_active=True, is_upcoming=False,
                  video_url='https://www.iqiyi.com/v_1lu8c0ub5bc.html'),

            Movie(title='星际穿越', year=2014, genre='科幻 / 冒险', duration=169, rating=9.4,
                  description='在不远的未来，地球黄沙遍野，小麦、秋葵等基础农作物相继因枯萎病灭绝，人类面临着生存危机。前NASA宇航员库珀（马修·麦康纳 Matthew McConaughey 饰）发现了一个神秘的引力异常现象，并因此被招募参与一项拯救人类的星际穿越计划。他告别了年幼的女儿墨菲，踏上了穿越虫洞、寻找人类新家园的征途。在浩瀚的宇宙中，库珀遭遇了时间膨胀、黑洞等极端物理现象，他与地球上的女儿之间也因时间流逝速度的不同，产生了一段跨越时空的父女深情。这是一部震撼人心的科幻史诗，重新定义了人类对宇宙和时间的认知。',
                  is_active=True, is_upcoming=False,
                  video_url='https://www.iqiyi.com/v_19rr7qhp7c.html'),

            Movie(title='盗梦空间', year=2010, genre='科幻 / 悬疑', duration=148, rating=9.3,
                  description='道姆·柯布（莱昂纳多·迪卡普里奥 Leonardo DiCaprio 饰）是一位技艺高超的盗贼，他专攻的领域是人的梦境——他能够在别人做梦时，潜入对方的潜意识中盗取机密信息。为了回到自己日思夜想的儿女身边，柯布接受了一个看似不可能完成的任务：在目标人物的梦境中植入一个想法（即 \"Inception\"）。为此，他组建了一支顶尖的团队，包括筑梦师、伪装师、药剂师等，层层深入多层梦境。在这场梦中梦中，现实与虚幻的界限逐渐模糊，柯布也不得不面对自己内心最深处的执念。这是一部脑洞大开、逻辑精妙的科幻悬疑神作，让观众在观影结束后依然沉浸在思考之中。',
                  is_active=True, is_upcoming=False,
                  video_url='https://www.iqiyi.com/v_19rra64i9c.html'),

            Movie(title='阿凡达', year=2009, genre='科幻 / 冒险', duration=162, rating=8.8,
                  description='故事发生在2154年，人类为了获取潘多拉星球上一种名为 \"Unobtanium\" 的稀有矿物，启动了 \"阿凡达计划\"。前海军陆战队员杰克·萨利（萨姆·沃辛顿 Sam Worthington 饰）因双腿瘫痪，被派往潘多拉星球，通过连接自己的意识来控制一个由人类基因与纳美人基因结合而成的 \"阿凡达\" 身体。在深入探索潘多拉的过程中，杰克结识了纳美族公主涅提妮（佐伊·索尔达娜 Zoe Saldana 饰），并逐渐被纳美人的文化和潘多拉的神奇生态所吸引。面对人类对潘多拉资源的贪婪掠夺，杰克最终选择站在纳美人一边，带领他们保卫自己的家园。这部电影以其革命性的3D视觉效果和深刻的生态主题，开创了电影技术的新纪元，成为全球影史票房冠军。',
                  is_active=True, is_upcoming=False,
                  video_url='https://www.iqiyi.com/v_20krtha8qxs.html'),

            Movie(title='复仇者联盟4', year=2019, genre='科幻 / 动作', duration=181, rating=8.5,
                  description='在灭霸一个响指消灭了宇宙一半生命后，幸存的复仇者们陷入了前所未有的绝望和迷茫。五年后，他们通过蚁人偶然发现的量子领域，找到了一条可能逆转败局的路径——穿越时空，回到过去收集无限宝石。为此，美国队长、钢铁侠、雷神等初代复仇者们再次集结，计划执行一项几乎不可能完成的 \"时间劫持\" 任务。在这个过程中，他们不仅要面对过去的自己，还要做出艰难的牺牲。这是一部漫威电影宇宙十年布局的巅峰之作，集结了数十位超级英雄，为初代复仇者的故事画上了一个悲壮而圆满的句号。',
                  is_active=True, is_upcoming=False,
                  video_url='https://www.iqiyi.com/v_19rr7q1fy0.html'),

            Movie(title='哪吒之魔童降世', year=2019, genre='动画 / 奇幻', duration=110, rating=8.4,
                  description='天地灵气孕育出一颗能量巨大的混元珠，元始天尊将其提炼成灵珠和魔丸。灵珠本应投胎为陈塘关李靖之子哪吒，然而由于申公豹从中作梗，魔丸阴差阳错地被投入了哪吒体内，哪吒一出生便被世人视为妖怪。在父母和师父太乙真人的关爱与教导下，哪吒并没有自暴自弃，他坚信 \"我命由我不由天\"，决定用自己的力量去打破偏见，保护自己的家人和百姓。当陈塘关面临被毁灭的危机时，哪吒挺身而出，与命运抗争到底。这部电影以其独特的画风、幽默的台词和燃爆的情感内核，成为中国影史票房最高的国产动画电影，打破了无数人对国漫的刻板印象。',
                  is_active=True, is_upcoming=False,
                  video_url='https://www.iqiyi.com/v_19rrcuke28.html'),
        ]

        db.session.add_all(movies)
        db.session.commit()
        print(f"✅ 成功添加 {len(movies)} 部电影（含视频链接）！")
        print("📌 提示：请将海报图片放入 static/posters/ 文件夹")
        print("📌 提示：请将轮播图图片放入 static/carousel/ 文件夹")

if __name__ == '__main__':
    init_data()