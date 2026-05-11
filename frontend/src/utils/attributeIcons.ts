const ATTRIBUTE_ICON_MAP: Record<string, string> = {
    '普': '普通系',
    '草': '草系',
    '火': '火系',
    '水': '水系',
    '光': '光系',
    '地': '地系',
    '冰': '冰系',
    '龙': '龙系',
    '电': '电系',
    '毒': '毒系',
    '虫': '虫系',
    '武': '武系',
    '翼': '翼系',
    '萌': '萌系',
    '幽': '幽系',
    '恶': '恶系',
    '机': '机械系',
    '幻': '幻系'
}

export function getAttributeIconPath(attr: string): string {
    const fullName = ATTRIBUTE_ICON_MAP[attr] || attr
    return `/images/attribute/${fullName}.png`
}

export function getAttributeFullName(attr: string): string {
    return ATTRIBUTE_ICON_MAP[attr] || attr
}
