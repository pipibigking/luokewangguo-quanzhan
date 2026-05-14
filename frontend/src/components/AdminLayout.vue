<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { logout } from '@/utils/auth'
import { getUnreadCount } from '@/api'

const route = useRoute()
const router = useRouter()

interface MenuItem {
    name: string
    path: string
    icon: string
    query?: Record<string, string>
}

const menuItems: MenuItem[] = [
    { name: '精灵管理', path: '/admin/pets', icon: '' },
    { name: '草稿箱', path: '/admin/pets', icon: '', query: { draft: '1' } },
    { name: '留言管理', path: '/admin/messages', icon: '' },
    { name: '公告管理', path: '/admin/announcement', icon: '' },
    { name: '账号管理', path: '/admin/accounts', icon: '' }
]

const unreadCount = ref(0)
let pollTimer: number | null = null

async function fetchUnreadCount() {
    try {
        const data = await getUnreadCount()
        unreadCount.value = data.count
    } catch {
        // 忽略轮询错误
    }
}

function onUnreadCountChanged() {
    fetchUnreadCount()
}

onMounted(() => {
    fetchUnreadCount()
    pollTimer = window.setInterval(fetchUnreadCount, 10000)
    window.addEventListener('unread-count-changed', onUnreadCountChanged)
})

onUnmounted(() => {
    if (pollTimer) clearInterval(pollTimer)
    window.removeEventListener('unread-count-changed', onUnreadCountChanged)
})

const activePath = computed(() => route.path)
const activeQuery = computed(() => route.query)

function navigateTo(item: MenuItem) {
    if (item.query) {
        router.push({ path: item.path, query: item.query })
    } else {
        router.push(item.path)
    }
}

function isActive(item: MenuItem): boolean {
    if (item.path !== activePath.value) return false
    if (item.query && item.query.draft) {
        return activeQuery.value.draft === item.query.draft
    }
    if (!item.query) {
        return !activeQuery.value.draft
    }
    return false
}

function goToFront() {
    window.location.href = '/#/'
}

function handleLogout() {
    logout()
    router.push('/login')
}
</script>

<template>
    <div class="admin-layout">
        <aside class="sidebar">
            <div class="sidebar-logo">
                <h1 class="logo-text">系统管理后台</h1>
            </div>

            <nav class="sidebar-nav">
                <button
                    v-for="item in menuItems"
                    :key="item.name"
                    class="nav-item"
                    :class="{ active: isActive(item) }"
                    @click="navigateTo(item)"
                >
                    <span class="nav-icon">{{ item.icon }}</span>
                    <span class="nav-label">{{ item.name }}</span>
                    <span v-if="item.name === '留言管理' && unreadCount > 0" class="nav-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
                </button>
            </nav>

            <div class="sidebar-footer">
                <button class="back-link" @click="goToFront">
                    <span class="back-icon">←</span>
                    <span>返回前台</span>
                </button>
                <button class="logout-link" @click="handleLogout">
                    <span class="logout-icon">🚪</span>
                    <span>退出登录</span>
                </button>
            </div>
        </aside>

        <main class="main-area">
            <div class="main-content">
                <router-view />
            </div>
        </main>
    </div>
</template>

<style scoped>
.admin-layout {
    display: flex;
    height: 100vh;
    overflow: hidden;
}

/* ======== 侧边栏 ======== */
.sidebar {
    width: 220px;
    min-width: 220px;
    background: url('/images/bg/像素合照.jpg') center center / cover no-repeat;
    display: flex;
    flex-direction: column;
    border-right: 1px solid rgba(99, 102, 241, 0.2);
    box-shadow: 4px 0 24px rgba(15, 23, 42, 0.4);
    position: relative;
    z-index: 10;
}

.sidebar::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(15, 23, 42, 0.6);
    pointer-events: none;
    z-index: 1;
}

/* Logo 区域 */
.sidebar-logo {
    padding: 24px 16px 32px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    z-index: 2;
}

.logo-text {
    font-size: 17px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 1px;
    white-space: nowrap;
    text-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
}

/* 导航区域 */
.sidebar-nav {
    flex: 1;
    padding: 16px 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    overflow-y: auto;
    position: relative;
    z-index: 2;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 12px 16px;
    border: none;
    border-radius: 10px;
    background: transparent;
    color: #fff;
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.nav-item::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 10px;
    opacity: 0;
    transition: opacity 0.25s ease;
    z-index: 0;
}

.nav-icon {
    font-size: 18px;
    line-height: 1;
    position: relative;
    z-index: 1;
    transition: transform 0.25s ease;
}

.nav-label {
    position: relative;
    z-index: 1;
}

.nav-badge {
    position: relative;
    z-index: 1;
    min-width: 20px;
    height: 20px;
    padding: 0 6px;
    border-radius: 10px;
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: auto;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.5);
    animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.12); }
}

.nav-item:hover {
    color: #fff;
    transform: translateX(4px);
}

.nav-item:hover .nav-icon {
    transform: scale(1.2);
}

.nav-item:active {
    transform: translateX(4px) scale(0.97);
}

/* ======== 各导航项差异化样式 ======== */
.nav-item {
    position: relative;
    overflow: hidden;
    z-index: 1;
}

.nav-item::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 0%;
    border-radius: 10px;
    transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: -1;
}

.nav-item.active {
    color: #ffffff;
}

/* 精灵管理 - 深青绿色 */
.nav-item:nth-child(1):hover,
.nav-item:nth-child(1).active {
    background: rgba(13, 148, 136, 0.35);
    box-shadow: 0 4px 16px rgba(13, 148, 136, 0.45);
}
.nav-item:nth-child(1)::after {
    background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
}
.nav-item:nth-child(1).active::after {
    height: 100%;
}

/* 草稿箱 - 黄色 */
.nav-item:nth-child(2):hover,
.nav-item:nth-child(2).active {
    background: rgba(245, 158, 11, 0.25);
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.35);
}
.nav-item:nth-child(2)::after {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}
.nav-item:nth-child(2).active::after {
    height: 100%;
}

/* 留言管理 - 绿色 */
.nav-item:nth-child(3):hover,
.nav-item:nth-child(3).active {
    background: rgba(16, 185, 129, 0.25);
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
}
.nav-item:nth-child(3)::after {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}
.nav-item:nth-child(3).active::after {
    height: 100%;
}

/* 公告管理 - 粉色 */
.nav-item:nth-child(4):hover,
.nav-item:nth-child(4).active {
    background: rgba(236, 72, 153, 0.25);
    box-shadow: 0 4px 16px rgba(236, 72, 153, 0.35);
}
.nav-item:nth-child(4)::after {
    background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
}
.nav-item:nth-child(4).active::after {
    height: 100%;
}

/* 账号管理 - 蓝色 */
.nav-item:nth-child(5):hover,
.nav-item:nth-child(5).active {
    background: rgba(56, 189, 248, 0.25);
    box-shadow: 0 4px 16px rgba(56, 189, 248, 0.35);
}
.nav-item:nth-child(5)::after {
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
}
.nav-item:nth-child(5).active::after {
    height: 100%;
}

.nav-item.active .nav-icon {
    transform: scale(1.15);
}

/* 底部返回链接 */
.sidebar-footer {
    padding: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    z-index: 2;
}

.back-link {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 12px 16px;
    border: none;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.04);
    color: #fff;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-icon {
    font-size: 16px;
    transition: transform 0.25s ease;
}

.back-link:hover {
    color: #1e293b;
    background: #fff;
}

.back-link:hover .back-icon {
    transform: translateX(-4px);
}

.back-link:active {
    transform: scale(0.97);
}

.logout-link {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 12px 16px;
    border: none;
    border-radius: 10px;
    background: rgba(239, 68, 68, 0.08);
    color: #fff;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    margin-top: 6px;
}

.logout-icon {
    font-size: 16px;
    transition: transform 0.25s ease;
}

.logout-link:hover {
    color: #1e293b;
    background: #ef4444;
}

.logout-link:hover .logout-icon {
    transform: translateX(3px);
}

.logout-link:active {
    transform: scale(0.97);
}

/* ======== 主内容区 ======== */
.main-area {
    flex: 1;
    background: #f1f5f9;
    overflow-y: auto;
    position: relative;
}

.main-area::before {
    content: '';
    position: fixed;
    top: 0;
    right: 0;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.main-content {
    padding: 32px;
    position: relative;
    z-index: 1;
    min-height: 100%;
}
</style>
