<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { getMessages, createMessage, getMessageAvatars } from '@/api'
import type { Message } from '@/types'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ close: [] }>()

const COOLDOWN_SECONDS = 30
const COOLDOWN_KEY = 'message_cooldown_end'

const messages = ref<Message[]>([])
const loading = ref(false)
const loadError = ref('')
const nickname = ref('')
const content = ref('')
const submitting = ref(false)
const cooldown = ref(0)
const toast = ref('')
const toastType = ref<'success' | 'error'>('success')
let toastTimer: number | null = null
let cooldownAnimId = 0
const listRef = ref<HTMLElement | null>(null)

const avatars = ref<{ name: string; src: string }[]>([])
const builtinAvatarFallback = [
    { name: '迪莫', src: '/images/avatar/迪莫.jpg' },
    { name: '火花', src: '/images/avatar/火花.jpg' },
    { name: '菊花梨', src: '/images/avatar/菊花梨.jpg' },
    { name: '喵喵', src: '/images/avatar/喵喵.jpg' },
    { name: '水蓝蓝', src: '/images/avatar/水蓝蓝.jpg' },
    { name: '鸭吉吉', src: '/images/avatar/鸭吉吉.jpg' }
]

async function loadAvatars() {
    try {
        const data = await getMessageAvatars()
        const allAvatars = [...data.builtin.map((a: any) => ({ name: a.name, src: a.url })), ...data.custom.map((a: any) => ({ name: a.name, src: a.url }))]
        avatars.value = allAvatars.length > 0 ? allAvatars : builtinAvatarFallback
    } catch {
        avatars.value = builtinAvatarFallback
    }
}

const selectedAvatar = ref(Number(localStorage.getItem('selectedAvatar') || '0'))
const showAvatarPicker = ref(false)

watch(selectedAvatar, (v) => {
    localStorage.setItem('selectedAvatar', String(v))
})

function showToast(msg: string, type: 'success' | 'error' = 'success') {
    toast.value = msg
    toastType.value = type
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = window.setTimeout(() => { toast.value = '' }, 3000)
}

async function loadMessages() {
    loading.value = true
    loadError.value = ''
    try {
        const data = await getMessages(true)
        messages.value = data.slice(0, 40).reverse()
        await nextTick()
        if (listRef.value) {
            listRef.value.scrollTop = listRef.value.scrollHeight
        }
    } catch {
        loadError.value = '加载留言失败，请检查后端服务'
        messages.value = []
    } finally {
        loading.value = false
    }
}

async function handleSend() {
    const nick = nickname.value.trim()
    const msg = content.value.trim()
    if (!nick || !msg) return
    if (cooldown.value > 0) return

    submitting.value = true
    try {
        await createMessage(nick, msg, selectedAvatar.value)
        content.value = ''
        showToast('留言已发送 ✨', 'success')
        startCooldown()
        await loadMessages()
    } catch (err: any) {
        const detail = err?.response?.data?.detail || '留言失败，请稍后再试'
        showToast(detail, 'error')
        if (detail.includes('频繁')) startCooldown()
    } finally {
        submitting.value = false
    }
}

function startCooldown() {
    cancelAnimationFrame(cooldownAnimId)
    const endTime = Date.now() + COOLDOWN_SECONDS * 1000
    localStorage.setItem(COOLDOWN_KEY, String(endTime))
    runCooldownTick(endTime)
}

function resumeCooldown(endTime: number) {
    const remaining = (endTime - Date.now()) / 1000
    if (remaining <= 0) {
        localStorage.removeItem(COOLDOWN_KEY)
        cooldown.value = 0
        return
    }
    cooldown.value = Math.ceil(remaining)
    runCooldownTick(endTime)
}

function runCooldownTick(endTime: number) {
    cancelAnimationFrame(cooldownAnimId)
    const startTime = performance.now()
    const totalMs = endTime - Date.now()
    let lastSecond = Math.ceil(totalMs / 1000)
    cooldown.value = lastSecond
    function tick(now: number) {
        const elapsed = (now - startTime) / 1000
        const remaining = Math.max(0, (totalMs / 1000) - elapsed)
        const currentSecond = Math.ceil(remaining)
        if (currentSecond !== lastSecond) {
            cooldown.value = currentSecond
            lastSecond = currentSecond
        }
        if (remaining > 0) {
            cooldownAnimId = requestAnimationFrame(tick)
        } else {
            cooldown.value = 0
            localStorage.removeItem(COOLDOWN_KEY)
        }
    }
    cooldownAnimId = requestAnimationFrame(tick)
}

function fmtTime(dateStr: string): string {
    if (!dateStr) return ''
    const d = new Date(dateStr.includes('Z') || dateStr.includes('+') ? dateStr : dateStr + 'Z')
    if (isNaN(d.getTime())) return dateStr
    const pad = (n: number) => n.toString().padStart(2, '0')
    return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function handleOverlayClick() {
    // 仅保留右上角×按钮关闭，点击遮罩不关闭
}

watch(() => props.visible, (v) => {
    if (v) {
        loadMessages()
        loadAvatars()
        const savedEnd = localStorage.getItem(COOLDOWN_KEY)
        if (savedEnd) {
            resumeCooldown(Number(savedEnd))
        }
    }
})

onMounted(() => {
    const savedEnd = localStorage.getItem(COOLDOWN_KEY)
    if (savedEnd) {
        resumeCooldown(Number(savedEnd))
    }
})

onUnmounted(() => {
    cancelAnimationFrame(cooldownAnimId)
})
</script>

<template>
    <div
        v-if="visible"
        class="msg-overlay"
        @click="handleOverlayClick"
    >
        <div class="msg-panel">
            <div class="msg-panel-head">
                <div class="msg-panel-title">
                    <h2>留言板</h2>
                    <span class="msg-panel-badge">{{ messages.length }}</span>
                </div>
                <button class="msg-panel-close" @click="emit('close')">
                    <span>✕</span>
                </button>
            </div>

            <div v-if="toast" class="msg-toast" :class="toastType">{{ toast }}</div>

            <div ref="listRef" class="msg-list">
                <div v-if="loading" class="msg-loading">
                    <span class="loading-dot"></span>
                    加载中...
                </div>
                <div v-else-if="loadError" class="msg-error">
                    <span class="error-icon">⚠️</span>
                    {{ loadError }}
                </div>
                <div v-else-if="messages.length === 0" class="msg-empty">
                    <span class="empty-icon">📝</span>
                    <p>还没有留言</p>
                    <p class="empty-sub">成为第一个留言的人吧</p>
                </div>
                <div
                    v-for="msg in messages"
                    :key="msg.id"
                    class="msg-bubble"
                >
                    <div class="msg-bubble-avatar">
                        <img :src="(avatars[msg.avatar_index >= 0 ? msg.avatar_index : (msg.id % 6)] || avatars[0])?.src" :alt="msg.nickname">
                    </div>
                    <div class="msg-bubble-body">
                        <div class="msg-bubble-head">
                            <span class="msg-bubble-name">{{ msg.nickname }}</span>
                            <span class="msg-bubble-time">{{ fmtTime(msg.created_at) }}</span>
                        </div>
                        <p class="msg-bubble-text">{{ msg.content }}</p>
                    </div>
                </div>
            </div>

            <div class="msg-input-area">
                <div class="avatar-selector">
                    <span class="avatar-label">选择头像：</span>
                    <div class="avatar-options">
                        <button
                            v-for="(avatar, index) in avatars.slice(0, 6)"
                            :key="index"
                            class="avatar-btn"
                            :class="{ active: selectedAvatar === index }"
                            @click="selectedAvatar = index"
                            :title="avatar.name"
                        >
                            <img :src="avatar.src" :alt="avatar.name">
                        </button>
                        <button v-if="avatars.length > 6" class="avatar-btn avatar-more-btn" @click="showAvatarPicker = true" title="更多头像">
                            <span>+</span>
                        </button>
                    </div>
                </div>
                <div class="msg-input-row">
                    <div class="selected-avatar-preview">
                        <img :src="avatars[selectedAvatar]?.src" :alt="avatars[selectedAvatar]?.name" />
                    </div>
                    <input
                        v-model="nickname"
                        type="text"
                        class="msg-nick-input"
                        placeholder="你的昵称"
                        maxlength="20"
                        :disabled="cooldown > 0"
                    />
                    <span v-if="cooldown > 0" class="msg-cooldown">
                        <span class="cooldown-ring">
                            <svg viewBox="0 0 24 24" class="cooldown-svg">
                                <circle cx="12" cy="12" r="10" class="cooldown-track" />
                                <circle cx="12" cy="12" r="10" class="cooldown-fill" :style="{ strokeDashoffset: (1 - cooldown / COOLDOWN_SECONDS) * 62.83 }" />
                            </svg>
                        </span>
                        <span class="cooldown-text">{{ cooldown }}</span>
                    </span>
                </div>
                <textarea
                    v-model="content"
                    class="msg-text-input"
                    placeholder="说点什么吧..."
                    rows="3"
                    maxlength="500"
                    :disabled="cooldown > 0"
                ></textarea>
                <div class="msg-send-row">
                    <span class="msg-char-count">{{ content.length }}/500</span>
                    <button
                        class="msg-send-btn"
                        :class="{ 'cooldown-active': cooldown > 0 }"
                        :disabled="submitting || cooldown > 0 || !nickname.trim() || !content.trim()"
                        @click="handleSend"
                    >
                        <span v-if="submitting" class="btn-loading"></span>
                        <span v-else-if="cooldown > 0">
                            <span class="timer-ring">
                                <svg viewBox="0 0 24 24" class="timer-svg">
                                    <circle cx="12" cy="12" r="10" class="timer-track" />
                                    <circle cx="12" cy="12" r="10" class="timer-progress" :style="{ strokeDashoffset: (1 - cooldown / COOLDOWN_SECONDS) * 62.83 }" />
                                </svg>
                            </span>
                            {{ cooldown }}s
                        </span>
                        <span v-else>发送留言</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- 头像选择弹窗 -->
        <div v-if="showAvatarPicker" class="picker-overlay" @click="showAvatarPicker = false">
            <div class="picker-dialog" @click.stop>
                <div class="picker-header">
                    <h3>选择头像</h3>
                    <button class="picker-close" @click="showAvatarPicker = false">×</button>
                </div>
                <div class="picker-grid">
                    <button
                        v-for="(avatar, index) in avatars"
                        :key="index"
                        class="picker-btn"
                        :class="{ active: selectedAvatar === index }"
                        @click="selectedAvatar = index; showAvatarPicker = false"
                        :title="avatar.name"
                    >
                        <img :src="avatar.src" :alt="avatar.name">
                        <span class="picker-name">{{ avatar.name }}</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.msg-overlay {
    position: fixed;
    inset: 0;
    background: rgba(10, 15, 37, 0.7);
    backdrop-filter: blur(8px);
    display: flex;
    justify-content: flex-end;
    z-index: 1000;
    animation: overlayIn 0.25s ease;
}

@keyframes overlayIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.msg-panel {
    width: 440px;
    max-width: 92vw;
    height: 100vh;
    background: url('/images/bg/6炫彩鸭吉吉.jpg') center center / cover no-repeat;
    display: flex;
    flex-direction: column;
    border-left: 1px solid rgba(99, 102, 241, 0.25);
    box-shadow: -8px 0 40px rgba(0, 0, 0, 0.5);
    animation: panelSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    overflow: hidden;
}

.msg-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    pointer-events: none;
    z-index: 0;
}

@keyframes panelSlideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* ======== 头部 ======== */
.msg-panel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 24px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.msg-panel-title {
    display: flex;
    align-items: center;
    gap: 12px;
}

.msg-panel-title h2 {
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
    letter-spacing: 2px;
}

.msg-panel-icon {
    font-size: 24px;
}

.msg-panel-badge {
    font-size: 12px;
    font-weight: 700;
    color: #a5b4fc;
    background: rgba(99, 102, 241, 0.15);
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid rgba(99, 102, 241, 0.25);
}

.msg-panel-close {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.15);
    background: rgba(255, 255, 255, 0.05);
    color: #94a3b8;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.25s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.msg-panel-close:hover {
    background: rgba(239, 68, 68, 0.7);
    border-color: transparent;
    color: #fff;
    transform: rotate(90deg) scale(1.1);
}

/* ======== Toast ======== */
.msg-toast {
    margin: 12px 24px 0;
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    flex-shrink: 0;
    animation: toastPop 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    z-index: 1;
}

.msg-toast.success {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.msg-toast.error {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

@keyframes toastPop {
    from { opacity: 0; transform: translateY(-12px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ======== 留言列表 ======== */
.msg-list {
    flex: 1;
    overflow-y: auto;
    padding: 16px 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: relative;
    z-index: 1;
}

.msg-list::-webkit-scrollbar {
    width: 4px;
}

.msg-list::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.3);
    border-radius: 2px;
}

.msg-loading,
.msg-error,
.msg-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 48px 16px;
    color: #94a3b8;
    font-size: 14px;
}

.loading-dot {
    width: 24px;
    height: 24px;
    border: 3px solid rgba(99, 102, 241, 0.2);
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-icon { font-size: 28px; }

.empty-icon { font-size: 40px; }

.empty-sub {
    font-size: 12px;
    color: #64748b;
    margin: 0;
}

/* ======== 留言气泡 ======== */
.msg-bubble {
    display: flex;
    gap: 12px;
    animation: bubbleIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes bubbleIn {
    from {
        opacity: 0;
        transform: translateY(16px) scale(0.97);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.msg-bubble-avatar {
    width: 40px;
    height: 40px;
    min-width: 40px;
    border-radius: 50%;
    overflow: hidden;
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.msg-bubble-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.msg-bubble-body {
    flex: 1;
    min-width: 0;
}

.msg-bubble-head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
}

.msg-bubble-name {
    font-size: 13px;
    font-weight: 700;
    color: #a5b4fc;
}

.msg-bubble-time {
    font-size: 11px;
    color: #ffffff;
    font-weight: 500;
    font-variant-numeric: tabular-nums;
    flex-shrink: 0;
}

.msg-bubble-text {
    font-size: 14px;
    color: #cbd5e1;
    line-height: 1.65;
    margin: 0;
    word-break: break-all;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 12px;
    padding: 10px 14px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* ======== 头像选择器 ======== */
.avatar-selector {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    position: relative;
    z-index: 1;
}

.avatar-label {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 500;
    white-space: nowrap;
}

.avatar-options {
    display: flex;
    gap: 6px;
}

.avatar-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 2px solid transparent;
    background: transparent;
    cursor: pointer;
    padding: 0;
    overflow: hidden;
    transition: all 0.2s ease;
    opacity: 0.6;
}

.avatar-btn:hover {
    opacity: 0.9;
    transform: scale(1.1);
}

.avatar-btn.active {
    border-color: #6366f1;
    opacity: 1;
    transform: scale(1.15);
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3);
}

.avatar-btn img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* ======== 输入区域 ======== */
.msg-input-area {
    padding: 16px 24px 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    background: rgba(0, 0, 0, 0.4);
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.msg-input-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}

.selected-avatar-preview {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    overflow: hidden;
    border: 2px solid rgba(255, 255, 255, 0.25);
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.selected-avatar-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.msg-nick-input {
    flex: 1;
    padding: 10px 14px;
    border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.3);
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 600;
    outline: none;
    transition: all 0.25s ease;
}

.msg-nick-input::placeholder {
    color: #64748b;
}

.msg-nick-input:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    background: rgba(0, 0, 0, 0.5);
}

.msg-nick-input:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.msg-cooldown {
    display: flex;
    align-items: center;
    gap: 4px;
}

.cooldown-ring {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.cooldown-svg {
    width: 28px;
    height: 28px;
    transform: rotate(-90deg);
}

.cooldown-track {
    fill: none;
    stroke: rgba(239, 68, 68, 0.2);
    stroke-width: 2;
}

.cooldown-fill {
    fill: none;
    stroke: #ef4444;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-dasharray: 62.83;
    transition: stroke-dashoffset 0.3s linear;
}

.cooldown-text {
    font-size: 18px;
    font-weight: 800;
    color: #f87171;
    font-variant-numeric: tabular-nums;
    min-width: 24px;
    animation: cdPulse 1s ease-in-out infinite;
}

@keyframes cdPulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.msg-text-input {
    width: 100%;
    padding: 12px 14px;
    border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.3);
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 500;
    outline: none;
    resize: vertical;
    font-family: inherit;
    transition: all 0.25s ease;
    min-height: 72px;
}

.msg-text-input::placeholder {
    color: #64748b;
}

.msg-text-input:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    background: rgba(0, 0, 0, 0.5);
}

.msg-text-input:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.msg-send-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
}

.msg-char-count {
    font-size: 12px;
    color: #64748b;
    font-weight: 500;
}

.msg-send-btn {
    padding: 10px 28px;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3);
    display: flex;
    align-items: center;
    gap: 6px;
    position: relative;
    overflow: hidden;
}

.msg-send-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
    transition: left 0.5s;
}

.msg-send-btn:hover::before {
    left: 100%;
}

.msg-send-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(6, 182, 212, 0.5);
    background: linear-gradient(135deg, #0891b2 0%, #2563eb 100%);
}

.msg-send-btn:active:not(:disabled) {
    transform: translateY(0) scale(0.97);
}

.msg-send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.msg-send-btn.cooldown-active {
    background: linear-gradient(135deg, #475569 0%, #334155 100%);
    box-shadow: 0 4px 14px rgba(71, 85, 105, 0.3);
    animation: timerPulse 1s ease-in-out infinite;
}

@keyframes timerPulse {
    0%, 100% { box-shadow: 0 4px 14px rgba(71, 85, 105, 0.3); }
    50% { box-shadow: 0 4px 20px rgba(71, 85, 105, 0.5); }
}

.btn-loading {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}

.timer-ring {
    width: 18px;
    height: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    vertical-align: middle;
    margin-right: 4px;
}

.timer-svg {
    width: 18px;
    height: 18px;
    transform: rotate(-90deg);
}

.timer-track {
    fill: none;
    stroke: rgba(255, 255, 255, 0.2);
    stroke-width: 2.5;
}

.timer-progress {
    fill: none;
    stroke: #38bdf8;
    stroke-width: 2.5;
    stroke-linecap: round;
    stroke-dasharray: 62.83;
    transition: stroke-dashoffset 0.3s linear;
}

/* ======== 更多头像按钮 ======== */
.avatar-more-btn {
    border: 2px dashed rgba(255,255,255,0.3) !important;
    background: rgba(255,255,255,0.05) !important;
    opacity: 0.7 !important;
    font-size: 20px;
    font-weight: 300;
    color: #94a3b8;
    display: flex !important;
    align-items: center;
    justify-content: center;
}

.avatar-more-btn:hover {
    opacity: 1 !important;
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
    background: rgba(56,189,248,0.1) !important;
}

.avatar-more-btn span {
    line-height: 1;
}

/* ======== 头像选择弹窗 ======== */
.picker-overlay {
    position: fixed;
    inset: 0;
    background: rgba(10, 15, 37, 0.7);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    animation: overlayFadeIn 0.2s ease;
}

@keyframes overlayFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.picker-dialog {
    background: #1e293b;
    border-radius: 20px;
    padding: 28px;
    width: 520px;
    max-width: 90vw;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 24px 64px rgba(0,0,0,0.5);
    animation: dialogPopIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes dialogPopIn {
    from { opacity: 0; transform: scale(0.9) translateY(20px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}

.picker-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.picker-header h3 {
    font-size: 18px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
}

.picker-close {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.15);
    background: transparent;
    color: #94a3b8;
    font-size: 18px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.picker-close:hover {
    background: rgba(239,68,68,0.6);
    color: #fff;
    border-color: transparent;
}

.picker-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

.picker-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 12px 8px;
    border-radius: 12px;
    border: 2px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.04);
    cursor: pointer;
    transition: all 0.2s ease;
}

.picker-btn:hover {
    border-color: #38bdf8;
    background: rgba(56,189,248,0.1);
    transform: translateY(-2px);
}

.picker-btn.active {
    border-color: #06b6d4;
    background: rgba(6,182,212,0.2);
    box-shadow: 0 0 0 2px rgba(6,182,212,0.3);
}

.picker-btn img {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
}

.picker-name {
    font-size: 11px;
    color: #94a3b8;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}

.picker-btn.active .picker-name {
    color: #06b6d4;
}

.picker-dialog::-webkit-scrollbar {
    width: 4px;
}

.picker-dialog::-webkit-scrollbar-thumb {
    background: rgba(99,102,241,0.3);
    border-radius: 2px;
}
</style>
