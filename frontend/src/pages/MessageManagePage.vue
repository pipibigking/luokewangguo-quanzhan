<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMessages, markMessageRead, markAllMessagesRead, deleteMessage, getUnreadCount } from '@/api'
import type { Message } from '@/types'
import { createParticleBurst } from '@/utils/particleEffect'

const messages = ref<Message[]>([])
const loading = ref(true)
const toastMsg = ref('')
const toastType = ref<'success' | 'error'>('success')
let toastTimer: number | null = null

const avatars = [
    '/images/avatar/迪莫.jpg',
    '/images/avatar/火花.jpg',
    '/images/avatar/菊花梨.jpg',
    '/images/avatar/喵喵.jpg',
    '/images/avatar/水蓝蓝.jpg',
    '/images/avatar/鸭吉吉.jpg'
]

function getAvatarSrc(msgId: number): string {
    return avatars[msgId % avatars.length]
}

function showToast(msg: string, type: 'success' | 'error' = 'success') {
    toastMsg.value = msg
    toastType.value = type
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = window.setTimeout(() => { toastMsg.value = '' }, 3000)
}

async function loadMessages() {
    loading.value = true
    try {
        const data = await getMessages(true)
        messages.value = data
    } catch {
        showToast('加载留言失败', 'error')
    } finally {
        loading.value = false
    }
}

function notifyUnreadChanged() {
    setTimeout(() => {
        window.dispatchEvent(new CustomEvent('unread-count-changed'))
    }, 0)
}

async function handleMarkRead(msg: Message) {
    if (msg.is_read) return
    try {
        await markMessageRead(msg.id)
        msg.is_read = true
        await fetchUnreadCount()
        notifyUnreadChanged()
    } catch {
        showToast('标记已读失败', 'error')
    }
}

async function handleMarkAllRead() {
    try {
        await markAllMessagesRead()
        messages.value.forEach(m => { m.is_read = true })
        await fetchUnreadCount()
        notifyUnreadChanged()
        showToast('全部标记为已读', 'success')
    } catch {
        showToast('操作失败', 'error')
    }
}

function handleMarkAllReadClick(e: MouseEvent) {
    createParticleBurst(e.currentTarget as HTMLElement, '#06b6d4')
    handleMarkAllRead()
}

async function fetchUnreadCount() {
    try {
        const data = await getUnreadCount()
        unreadMessages.value = data.count
    } catch {}
}

async function handleDelete(msg: Message) {
    if (!confirm(`确定要删除"${msg.nickname}"的留言吗？`)) return
    try {
        await deleteMessage(msg.id)
        // 使用浅拷贝创建新数组，确保 Vue 响应式正确触发
        const updatedMessages = messages.value.filter(m => m.id !== msg.id)
        messages.value = [...updatedMessages]
        await fetchUnreadCount()
        notifyUnreadChanged()
        showToast('留言已删除', 'success')
    } catch (err) {
        console.error('删除留言失败:', err)
        showToast('删除失败', 'error')
    }
}

function formatTime(dateStr: string): string {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    // 检查日期是否有效
    if (isNaN(d.getTime())) return ''
    const pad = (n: number) => n.toString().padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

const unreadMessages = ref(0)

onMounted(async () => {
    await loadMessages()
    try {
        const data = await getUnreadCount()
        unreadMessages.value = data.count
    } catch {}
})
</script>

<template>
    <div class="message-manage-page">
        <div v-if="toastMsg" class="toast" :class="toastType">{{ toastMsg }}</div>

        <div class="page-header">
            <h2 class="page-title">留言管理</h2>
            <div class="header-actions">
                <button
                    class="btn-read-all"
                    @click="handleMarkAllReadClick"
                >
                    全部已读
                </button>
            </div>
        </div>

        <div v-if="loading" class="state-container">
            <div class="loading-spinner"></div>
            <p class="state-text">正在加载留言...</p>
        </div>

        <div v-else-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">💬</div>
            <p class="empty-text">暂无留言</p>
        </div>

        <div v-else class="message-list">
            <div
                v-for="(msg, index) in messages"
                :key="msg.id ?? `msg-${index}`"
                class="message-card"
                :class="{ unread: !msg.is_read }"
                @click="handleMarkRead(msg)"
            >
                <div class="message-header">
                    <div class="message-user">
                        <img :src="getAvatarSrc(msg.id ?? 0)" class="user-avatar-img" :alt="msg.nickname || '用户'">
                        <span class="user-name">{{ msg.nickname || '匿名用户' }}</span>
                        <span v-if="!msg.is_read" class="unread-dot"></span>
                    </div>
                    <span class="message-time">{{ formatTime(msg.created_at) }}</span>
                </div>
                <div class="message-body">
                    <p class="message-content">{{ msg.content || '' }}</p>
                </div>
                <div class="message-footer">
                    <span class="status-tag" :class="msg.is_read ? 'read' : 'unread-status'">
                        {{ msg.is_read ? '已读' : '未读' }}
                    </span>
                    <button class="btn-delete-msg" @click.stop="handleDelete(msg)" title="删除留言">
                        🗑️
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.message-manage-page {
    position: relative;
    min-height: 100%;
}

.message-manage-page::before {
    content: '';
    position: fixed;
    top: 0;
    left: 220px;
    right: 0;
    bottom: 0;
    background: url('/images/bg/抹茶布丁绿色爱心.png') center center / cover no-repeat;
    z-index: -2;
}

.message-manage-page::after {
    content: '';
    position: fixed;
    top: 0;
    left: 220px;
    right: 0;
    bottom: 0;
    background: rgba(241, 245, 249, 0.5);
    z-index: -1;
}

.toast {
    position: fixed;
    top: 24px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 28px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    z-index: 2000;
    animation: toastIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: 0 8px 28px rgba(15, 23, 42, 0.3);
}

.toast.success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.toast.error {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

@keyframes toastIn {
    from { opacity: 0; transform: translateX(-50%) translateY(-20px) scale(0.9); }
    to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.page-title {
    font-size: 24px;
    font-weight: 800;
    color: #1e293b;
    letter-spacing: 1px;
    margin: 0;
}

.header-actions {
    display: flex;
    gap: 12px;
}

.btn-read-all {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 24px;
    border: none;
    border-radius: 50px;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 6px 20px rgba(6, 182, 212, 0.35);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
}

.btn-read-all::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.6s;
}

.btn-read-all:hover::before {
    left: 100%;
}

.btn-read-all:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 28px rgba(6, 182, 212, 0.5), 0 0 0 4px rgba(6, 182, 212, 0.1);
}

.btn-read-all:active {
    transform: translateY(-1px) scale(0.97);
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}

.state-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    background: linear-gradient(145deg, rgba(255,255,255,0.55) 0%, rgba(248,250,252,0.5) 100%);
    border-radius: 20px;
    box-shadow: 0 6px 24px rgba(15,23,42,0.1);
    backdrop-filter: blur(6px);
}

.loading-spinner {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(99,102,241,0.15);
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 20px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.state-text {
    font-size: 15px;
    color: #475569;
    font-weight: 600;
}

.empty-state {
    text-align: center;
    padding: 80px 20px;
    background: linear-gradient(145deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.92) 100%);
    border-radius: 20px;
    box-shadow: 0 6px 24px rgba(15,23,42,0.1);
}

.empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
}

.empty-text {
    font-size: 18px;
    color: #94a3b8;
    font-weight: 600;
}

.message-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.message-card {
    background: rgba(255, 255, 255, 0.55);
    border-radius: 16px;
    padding: 20px 24px;
    border: 2px solid rgba(226, 232, 240, 0.4);
    cursor: pointer;
    transition: all 0.25s ease;
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    backdrop-filter: blur(6px);
}

.message-card:hover {
    border-color: #6366f1;
    box-shadow: 0 6px 24px rgba(99,102,241,0.12);
    transform: translateY(-2px);
}

.message-card.unread {
    border-color: #f59e0b;
    background: linear-gradient(135deg, #fffbeb 0%, #fff 100%);
    box-shadow: 0 2px 12px rgba(245,158,11,0.1);
}

.message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.message-user {
    display: flex;
    align-items: center;
    gap: 10px;
}

.user-avatar-img {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #e2e8f0;
}

.user-name {
    font-size: 15px;
    font-weight: 700;
    color: #1e293b;
}

.unread-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ef4444;
    box-shadow: 0 0 8px rgba(239,68,68,0.5);
    animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.5); }
}

.message-time {
    font-size: 13px;
    color: #94a3b8;
    font-weight: 500;
}

.message-body {
    margin-bottom: 12px;
}

.message-content {
    font-size: 15px;
    color: #334155;
    line-height: 1.7;
    margin: 0;
    word-break: break-all;
}

.message-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.status-tag {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}

.status-tag.read {
    background: rgba(148,163,184,0.12);
    color: #64748b;
}

.status-tag.unread-status {
    background: rgba(245,158,11,0.12);
    color: #d97706;
}

.btn-delete-msg {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    border: none;
    background: transparent;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-delete-msg:hover {
    background: rgba(239,68,68,0.12);
    box-shadow: 0 4px 12px rgba(239,68,68,0.25);
    transform: scale(1.1);
}
</style>
