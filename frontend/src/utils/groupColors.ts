import { getGroupColors as apiGetGroupColors, updateGroupColor as apiUpdateGroupColor } from '@/api'

const DEFAULT_COLORS: Record<string, string> = {
    '赛季异色': '#8B5CF6',
    '赛季奇遇异色': '#3B82F6',
    '赛季战令异色': '#F97316',
    '活动异色': '#EC4899'
}

let cachedColors: Record<string, string> | null = null

export async function loadGroupColors(): Promise<Record<string, string>> {
    try {
        const colors = await apiGetGroupColors()
        cachedColors = colors
        return colors
    } catch (error) {
        console.error('加载分组颜色失败:', error)
        return cachedColors || {}
    }
}

export async function saveGroupColor(group: string, color: string): Promise<void> {
    try {
        await apiUpdateGroupColor(group, color)
        // 更新缓存
        if (cachedColors) {
            cachedColors[group] = color
        }
    } catch (error) {
        console.error('保存分组颜色失败:', error)
        throw error
    }
}

export function getGroupColor(group: string): string {
    // 优先使用缓存
    if (cachedColors && cachedColors[group]) {
        return cachedColors[group]
    }
    // 使用默认颜色
    if (DEFAULT_COLORS[group]) return DEFAULT_COLORS[group]
    // 生成随机颜色
    if (group) {
        let hash = 0
        for (let i = 0; i < group.length; i++) {
            hash = group.charCodeAt(i) + ((hash << 5) - hash)
        }
        const hue = Math.abs(hash) % 360
        return `hsl(${hue}, 64%, 48%)`
    }
    return '#6B7280'
}

export function getDefaultColors(): Record<string, string> {
    return { ...DEFAULT_COLORS }
}

// 初始化加载颜色
export async function initGroupColors(): Promise<void> {
    await loadGroupColors()
}
