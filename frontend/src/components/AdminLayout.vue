<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { logout } from '@/utils/auth'

const route = useRoute()
const router = useRouter()

interface MenuItem {
    name: string
    path: string
    icon: string
}

const menuItems: MenuItem[] = [
    { name: '精灵管理', path: '/admin/pets', icon: '🐾' },
    { name: '公告管理', path: '/admin/announcement', icon: '📢' },
    { name: '账号管理', path: '/admin/accounts', icon: '👤' }
]

const activePath = computed(() => route.path)

function navigateTo(path: string) {
    router.push(path)
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
                <span class="logo-icon">✨</span>
                <h1 class="logo-text">精灵管理后台</h1>
            </div>

            <nav class="sidebar-nav">
                <button
                    v-for="item in menuItems"
                    :key="item.path"
                    class="nav-item"
                    :class="{ active: activePath === item.path }"
                    @click="navigateTo(item.path)"
                >
                    <span class="nav-icon">{{ item.icon }}</span>
                    <span class="nav-label">{{ item.name }}</span>
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
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 40%, #0f172a 100%);
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
    background:
        radial-gradient(circle at 50% 15%, rgba(99, 102, 241, 0.12) 0%, transparent 50%),
        radial-gradient(circle at 50% 85%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
    pointer-events: none;
}

/* Logo 区域 */
.sidebar-logo {
    padding: 24px 16px 32px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid rgba(99, 102, 241, 0.15);
}

.logo-icon {
    font-size: 28px;
    line-height: 1;
    filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.5));
    animation: logoPulse 3s ease-in-out infinite;
}

@keyframes logoPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.12); }
}

.logo-text {
    font-size: 17px;
    font-weight: 700;
    color: #e2e8f0;
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
    color: #94a3b8;
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
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
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

.nav-item:hover {
    color: #e2e8f0;
    background: rgba(99, 102, 241, 0.12);
    transform: translateX(4px);
}

.nav-item:hover .nav-icon {
    transform: scale(1.2);
}

.nav-item:active {
    transform: translateX(4px) scale(0.97);
}

.nav-item.active {
    color: #ffffff;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
}

.nav-item.active::before {
    opacity: 1;
}

.nav-item.active .nav-icon {
    transform: scale(1.15);
}

/* 底部返回链接 */
.sidebar-footer {
    padding: 12px;
    border-top: 1px solid rgba(99, 102, 241, 0.15);
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
    color: #64748b;
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
    color: #c4b5fd;
    background: rgba(139, 92, 246, 0.12);
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
    background: rgba(239, 68, 68, 0.06);
    color: #f87171;
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
    color: #fca5a5;
    background: rgba(239, 68, 68, 0.14);
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
