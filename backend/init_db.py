from main import Base, engine, SessionLocal
import json

pets_data = [
    {"id": 1, "name": "大耳帽兜", "group": "赛季异色", "image_url": "images/pets/大耳帽兜.png", "price": 60, "attributes": ["冰"], "description": "大耳帽兜是一只可爱的冰系精灵，拥有大大的耳朵，能听到很远的声音。在寒冷的冬天，它的耳朵还能起到保暖的作用。性格温和，善于治愈，是训练师们可靠的伙伴。"},
    {"id": 2, "name": "恶魔狼", "group": "赛季异色", "image_url": "images/pets/恶魔狼.png", "price": 35, "attributes": ["恶", "幽"], "description": "恶魔狼是一只神秘的精灵，拥有恶系和幽系的双重属性。擅长使用黑暗力量攻击敌人，在夜间战斗力更强。虽然外表看起来有些可怕，但是实际上它对训练师非常忠诚。"},
    {"id": 3, "name": "奇丽草", "group": "赛季异色", "image_url": "images/pets/奇丽草.png", "price": 45, "attributes": ["草"], "description": "奇丽草是一只优雅的草系精灵，拥有美丽的花朵，能在阳光下进行光合作用，为周围提供新鲜的空气。能够使用各种草系技能，包括寄生种子和光合作用，在团队中起到重要的辅助作用。"},
    {"id": 4, "name": "格兰种子", "group": "赛季异色", "image_url": "images/pets/格兰种子.png", "price": 45, "attributes": ["草", "翼"], "description": "格兰种子是一只神奇的草系与翼系双属性精灵，在幼年时看起来像一颗普通的种子，但是随着成长会发生惊人的变化。拥有令人难以置信的速度，在战场上很难被击中，是一只优秀的速攻型精灵。"},
    {"id": 5, "name": "拉特", "group": "赛季异色", "image_url": "images/pets/拉特.png", "price": 45, "attributes": ["电"], "description": "拉特是一只强大的电系精灵，能释放出强力的电击技能，在雨天威力更大。具有出色的特攻属性，能使用各种电系技能给敌人造成巨大伤害，是队伍中重要的输出精灵。"},
    {"id": 6, "name": "治愈兔", "group": "赛季异色", "image_url": "images/pets/治愈兔.png", "price": 60, "attributes": ["草", "萌"], "description": "治愈兔是一只非常特殊的精灵，拥有治愈的能力，能在队伍中为其他精灵恢复体力，提供重要的辅助支持。性格温柔善良，深受训练师和其他精灵的喜爱。"},
    {"id": 7, "name": "机械方方", "group": "赛季异色", "image_url": "images/pets/机械方方.png", "price": 45, "attributes": ["机"], "description": "机械方方是一只高科技制造的精灵，身体由坚硬的钢铁构成，具有极强的防御能力。能够使用各种高科技武器进行攻击，同时还能提升队友的防御能力，是一只非常全面的精灵。"},
    {"id": 8, "name": "呼呼猪", "group": "赛季异色", "image_url": "images/pets/呼呼猪.png", "price": 45, "attributes": ["普"], "description": "呼呼猪看起来是一只普通的精灵，但是实际上隐藏着巨大的潜力，性格憨厚老实，虽然看起来有些笨拙，但是在战斗中会展现出惊人的力量。身体非常结实，能够承受大量的伤害。"},
    {"id": 9, "name": "柴渣虫", "group": "赛季奇遇异色", "image_url": "images/pets/柴渣虫.png", "price": 65, "attributes": ["虫"], "description": "柴渣虫是一只可爱的虫系精灵，体型虽小但是性格勇敢，总是乐观积极，能够使用各种虫系技能，包括吐丝攻击和虫咬。随着成长，会发生惊人的进化变化。"},
    {"id": 10, "name": "月牙雪熊", "group": "赛季奇遇异色", "image_url": "images/pets/月牙雪熊.png", "price": 35, "attributes": ["冰", "武"], "description": "月牙雪熊是一只生活在雪山上的精灵，拥有强大的冰系能力，能在寒冷的环境中自由行动。身体强壮有力，能够使用各种武系技能。对训练师非常忠诚，愿意为了训练师而战斗。"},
    {"id": 11, "name": "嗜光嗡嗡", "group": "赛季奇遇异色", "image_url": "images/pets/嗜光嗡嗡.png", "price": 65, "attributes": ["虫", "翼"], "description": "嗜光嗡嗡是一只美丽的虫系与翼系双属性精灵，喜欢在阳光下飞舞，能够快速飞行并从空中发起攻击。翅膀有着美丽的花纹，能够释放出迷惑敌人的粉粉。"},
    {"id": 12, "name": "空空颅", "group": "赛季奇遇异色", "image_url": "images/pets/空空颅.png", "price": 60, "attributes": ["幽"], "description": "空空颅是一只神秘的幽系精灵，身体非常特殊，能穿透各种物体，能够使用各种幽系技能，给敌人造成心理和物理的双重伤害。虽然看起来有些可怕，但是其实内心非常温柔。"},
    {"id": 13, "name": "粉粉星", "group": "赛季奇遇异色", "image_url": "images/pets/粉粉星.png", "price": 60, "attributes": ["电", "萌"], "description": "粉粉星是一只闪耀的电系与萌系双属性精灵，身体能够发出柔和的光芒，在黑暗中指引方向。能够使用各种电系和萌系技能，具有出色的特攻能力。是一只可爱且强大的精灵。"},
    {"id": 14, "name": "贝瑟", "group": "赛季奇遇异色", "image_url": "images/pets/贝瑟.png", "price": 60, "attributes": ["水", "地"], "description": "贝瑟是一只生活在水边的精灵，身体结构坚固，能在水中自由游动，能够使用水系和地系技能，既能攻击敌人也能保护自己。是一只可靠的防御型精灵，在队伍中起到重要的保护作用。"},
    {"id": 15, "name": "粉星仔", "group": "赛季奇遇异色", "image_url": "images/pets/粉星仔.png", "price": 60, "attributes": ["电", "萌"], "description": "粉星仔是一只可爱的电系与萌系双属性精灵，身体娇小但是充满活力，能够释放出耀眼的电力，能够使用各种电系和萌系技能，具有出色的速度和特攻能力，是一只非常适合速攻战术的精灵。"},
    {"id": 16, "name": "双灯鱼", "group": "赛季奇遇异色", "image_url": "images/pets/双灯鱼.png", "price": 60, "attributes": ["水", "电"], "description": "双灯鱼是一只独特的水系与电系双属性精灵，头顶的两个灯能在深海中发光，照亮周围的环境。能够在水中自由游动，并使用水系和电系技能攻击敌人。这只精灵在雨天战斗力会大幅提升。"},
    {"id": 17, "name": "绒绒", "group": "赛季战令异色", "image_url": "images/pets/绒仙子.png", "price": 70, "attributes": ["萌"], "description": "绒绒是一只优雅的萌系精灵，拥有美丽的外表，能在空中翩翩起舞。能够使用各种萌系技能，包括魔法攻击和辅助技能。性格温柔，能治愈队友的伤病，是队伍中重要的辅助精灵。"},
    {"id": 18, "name": "犀角鸟", "group": "赛季战令异色", "image_url": "images/pets/犀角鸟.png", "price": 70, "attributes": ["翼", "地"], "description": "犀角鸟是一只威武的翼系与地系双属性精灵，拥有强壮的体魄，能在高空中自由飞翔。头顶有一只锐利的角，能够刺穿坚硬的岩石，具有优秀的物攻能力，能给敌人造成巨大伤害。"},
    {"id": 19, "name": "火红尾", "group": "活动异色", "image_url": "images/pets/火红尾.png", "price": 60, "attributes": ["火"], "description": "火红尾是一只热情的火系精灵，尾巴燃烧着熊熊烈火，显示出它强大的火焰能力。能够使用各种火系技能，在阳光下威力更大。性格活泼，总是充满活力，是训练师的好伙伴。"}
]

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    from main import Pet
    
    inserted_count = 0
    skipped_count = 0

    for pet_data in pets_data:
        existing_pet = db.query(Pet).filter(Pet.id == pet_data["id"]).first()
        if existing_pet:
            skipped_count += 1
        else:
            pet = Pet(
                id=pet_data["id"],
                name=pet_data["name"],
                group=pet_data["group"],
                image_url=pet_data["image_url"],
                price=pet_data["price"],
                attributes=json.dumps(pet_data["attributes"]),
                description=pet_data["description"],
                abilities="[]",
                is_active=True
            )
            db.add(pet)
            inserted_count += 1

    print(f"精灵数据: 新插入 {inserted_count} 条, 跳过已存在 {skipped_count} 条")

    from main import Announcement
    existing_ann = db.query(Announcement).first()
    if not existing_ann:
        ann = Announcement(content="欢迎来到笑笑屁屁-洛克王国异色精灵交易平台！新精灵即将上架，敬请期待~")
        db.add(ann)

    db.commit()
    db.close()
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_db()
