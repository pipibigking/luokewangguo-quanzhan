<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMessages, markMessageRead, markAllMessagesRead, deleteMessage, getUnreadCount, getMessageAvatars, uploadMessageAvatar, deleteMessageAvatar } from '@/api'
import type { Message } from '@/types'
import type { AvatarItem } from '@/api'
import { createParticleBurst } from '@/utils/particleEffect'

const messages = ref<Message[]>([])
const loading = ref(true)
const toastMsg = ref('')
const toastType = ref<'success' | 'error'>('success')
let toastTimer: number | null = null

const AVATAR_FALLBACK_LIST: AvatarItem[] = [
    { id: -1, name: '迪莫', url: '/images/avatar/迪莫.jpg' },
    { id: -2, name: '火花', url: '/images/avatar/火花.jpg' },
    { id: -3, name: '菊花梨', url: '/images/avatar/菊花梨.jpg' },
    { id: -4, name: '喵喵', url: '/images/avatar/喵喵.jpg' },
    { id: -5, name: '水蓝蓝', url: '/images/avatar/水蓝蓝.jpg' },
    { id: -6, name: '鸭吉吉', url: '/images/avatar/鸭吉吉.jpg' }
]

const builtinAvatars = ref<AvatarItem[]>(AVATAR_FALLBACK_LIST)
const customAvatars = ref<AvatarItem[]>([])
const allAvatars = ref<AvatarItem[]>(AVATAR_FALLBACK_LIST)
const deletedGlobalIndices = ref<number[]>([])

function getAvatarSrc(msg: Message): string {
    const idx = msg.avatar_index >= 0 ? msg.avatar_index : (msg.id % 6)
    if (deletedGlobalIndices.value.includes(idx) || idx >= allAvatars.value.length) {
        return AVATAR_FALLBACK_LIST[0].url
    }
    return allAvatars.value[idx]?.url || AVATAR_FALLBACK_LIST[0].url
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

async function loadAvatars() {
    try {
        const data = await getMessageAvatars()
        builtinAvatars.value = data.builtin.length > 0 ? data.builtin : AVATAR_FALLBACK_LIST
        customAvatars.value = data.custom
        allAvatars.value = [...builtinAvatars.value, ...data.custom]
    } catch {}
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

const showDeleteConfirm = ref(false)
const deletingMsg = ref<Message | null>(null)
const deleteSubmitting = ref(false)

function confirmDelete(msg: Message) {
    deletingMsg.value = msg
    showDeleteConfirm.value = true
}

async function handleDeleteConfirm() {
    if (!deletingMsg.value) return
    deleteSubmitting.value = true
    try {
        await deleteMessage(deletingMsg.value.id)
        const updatedMessages = messages.value.filter(m => m.id !== deletingMsg.value!.id)
        messages.value = [...updatedMessages]
        await fetchUnreadCount()
        notifyUnreadChanged()
        showToast('留言已删除', 'success')
    } catch (err) {
        console.error('删除留言失败:', err)
        showToast('删除失败', 'error')
    } finally {
        deleteSubmitting.value = false
        showDeleteConfirm.value = false
        deletingMsg.value = null
    }
}

function cancelDelete() {
    showDeleteConfirm.value = false
    deletingMsg.value = null
}

const uploadUploading = ref(false)
const uploadProgress = ref('')
const showPreviewModal = ref(false)
const previewAvatarUrl = ref('')

const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
const MAX_IMAGE_SIZE = 5 * 1024 * 1024

async function handleAvatarUpload(e: Event) {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (!file) return

    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
        showToast('仅支持 JPG、PNG、GIF、WebP 格式', 'error')
        input.value = ''
        return
    }

    if (file.size > MAX_IMAGE_SIZE) {
        showToast('图片大小不能超过 5MB', 'error')
        input.value = ''
        return
    }

    uploadUploading.value = true
    uploadProgress.value = '上传中...'
    try {
        await uploadMessageAvatar(file)
        uploadProgress.value = '上传完成 ✓'
        await loadAvatars()
        showToast('头像上传成功', 'success')
    } catch (err) {
        console.error('上传失败:', err)
        showToast('头像上传失败', 'error')
        uploadProgress.value = ''
    } finally {
        uploadUploading.value = false
        input.value = ''
        setTimeout(() => { uploadProgress.value = '' }, 2000)
    }
}

async function handleDeleteCustomAvatar(avatarId: number) {
    const customIdx = customAvatars.value.findIndex(a => a.id === avatarId)
    if (customIdx >= 0) {
        deletedGlobalIndices.value.push(6 + customIdx)
    }
    try {
        await deleteMessageAvatar(avatarId)
        await loadAvatars()
        showToast('头像已删除', 'success')
    } catch {
        showToast('删除失败', 'error')
    }
}

function openPreview(url: string) {
    previewAvatarUrl.value = url
    showPreviewModal.value = true
}

function closePreview() {
    showPreviewModal.value = false
    previewAvatarUrl.value = ''
}

function formatTime(dateStr: string): string {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return ''
    const pad = (n: number) => n.toString().padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

const unreadMessages = ref(0)

onMounted(async () => {
    await Promise.all([loadMessages(), loadAvatars()])
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
                <button class="btn-read-all" @click="handleMarkAllReadClick">全部已读</button>
            </div>
        </div>

        <div class="content-layout">
            <div class="main-content">
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
                                <img :src="getAvatarSrc(msg)" class="user-avatar-img" :alt="msg.nickname || '用户'">
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
                            <button class="btn-delete-msg" @click.stop="confirmDelete(msg)" title="删除留言">🗑️</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="avatar-manage-panel">
                <h3 class="avatar-manage-title">头像管理</h3>

                <div class="avatar-upload-area">
                    <label class="upload-avatar-btn" :class="{ uploading: uploadUploading }">
                        <input type="file" accept="image/jpeg,image/png,image/gif,image/webp" @change="handleAvatarUpload" />
                        <span v-if="uploadProgress">{{ uploadProgress }}</span>
                        <span v-else>+ 上传新头像</span>
                    </label>
                </div>

                <div v-if="customAvatars.length > 0" class="custom-avatars">
                    <h4 class="sub-title">自定义头像</h4>
                    <div class="avatar-grid">
                        <div v-for="avatar in customAvatars" :key="avatar.id" class="avatar-item">
                            <div class="avatar-preview-wrap" @click="openPreview(avatar.url)">
                                <img :src="avatar.url" :alt="avatar.name" class="avatar-preview-img" />
                                <button class="avatar-remove-btn" @click.stop="handleDeleteCustomAvatar(avatar.id)" title="删除">×</button>
                            </div>
                            <span class="avatar-name">{{ avatar.name }}</span>
                        </div>
                    </div>
                </div>

                <p v-else class="no-avatar-hint">还没有自定义头像，点击上方按钮上传</p>
            </div>
        </div>

        <div v-if="showDeleteConfirm" class="confirm-overlay" @click="cancelDelete">
            <div class="confirm-dialog" @click.stop>
                <div class="confirm-icon">⚠️</div>
                <p class="confirm-text">是否删除此留言？</p>
                <p v-if="deletingMsg" class="confirm-detail">{{ deletingMsg.nickname }}：{{ deletingMsg.content?.slice(0, 30) }}{{ (deletingMsg.content?.length || 0) > 30 ? '...' : '' }}</p>
                <div class="confirm-actions">
                    <button class="confirm-btn cancel" :disabled="deleteSubmitting" @click="cancelDelete">取消</button>
                    <button class="confirm-btn agree" :disabled="deleteSubmitting" @click="handleDeleteConfirm">
                        <span v-if="deleteSubmitting" class="btn-spinner"></span>
                        <span v-else>同意</span>
                    </button>
                </div>
            </div>
        </div>

        <div v-if="showPreviewModal" class="preview-overlay" @click="closePreview">
            <div class="preview-content" @click.stop>
                <button class="preview-close-btn" @click="closePreview">×</button>
                <img :src="previewAvatarUrl" alt="头像预览" class="preview-image" />
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
    padding-bottom: 16px;
    border-bottom: 2px solid rgba(6, 182, 212, 0.15);
}

.page-title {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
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

.content-layout {
    display: flex;
    gap: 24px;
    align-items: flex-start;
}

.main-content {
    flex: 1;
    min-width: 0;
}

.avatar-manage-panel {
    width: 260px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(226, 232, 240, 0.4);
    flex-shrink: 0;
}

.avatar-manage-title {
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 16px 0;
}

.sub-title {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    margin: 16px 0 10px 0;
}

.upload-avatar-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    background: #f8fafc;
    border: 2px dashed #cbd5e1;
    cursor: pointer;
    transition: all 0.2s ease;
}

.upload-avatar-btn:hover {
    border-color: #2563eb;
    color: #2563eb;
    background: rgba(37, 99, 235, 0.04);
}

.upload-avatar-btn.uploading {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
}

.upload-avatar-btn input[type="file"] {
    display: none;
}

.avatar-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
}

.avatar-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}

.avatar-preview-wrap {
    width: 72px;
    height: 72px;
    border-radius: 12px;
    overflow: visible;
    border: 2px solid #e2e8f0;
    position: relative;
    cursor: pointer;
    transition: border-color 0.2s;
}

.avatar-preview-wrap:hover {
    border-color: #06b6d4;
}

.avatar-preview-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 10px;
}

.avatar-remove-btn {
    position: absolute;
    top: -10px;
    right: -10px;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    border: 2px solid #fff;
    background: #ef4444;
    color: #fff;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.2s, transform 0.2s;
    line-height: 1;
    padding: 0;
    z-index: 3;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

.avatar-item:hover .avatar-remove-btn {
    opacity: 1;
}

.avatar-remove-btn:hover {
    transform: scale(1.2);
    background: #dc2626;
}

.avatar-name {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
}

.no-avatar-hint {
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
    margin: 24px 0 8px;
    line-height: 1.6;
}

/* ======== 预览弹窗 ======== */
.preview-overlay {
    position: fixed;
    inset: 0;
    background: rgba(10, 15, 37, 0.75);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 3000;
    animation: overlayFadeIn 0.2s ease;
}

.preview-content {
    position: relative;
    max-width: 80vw;
    max-height: 80vh;
    animation: dialogPopIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.preview-image {
    max-width: 100%;
    max-height: 80vh;
    border-radius: 16px;
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
}

.preview-close-btn {
    position: absolute;
    top: -16px;
    right: -16px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.3);
    background: rgba(0,0,0,0.5);
    color: #fff;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    line-height: 1;
}

.preview-close-btn:hover {
    background: rgba(239,68,68,0.8);
    transform: rotate(90deg);
    border-color: transparent;
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

.confirm-overlay {
    position: fixed;
    inset: 0;
    background: rgba(10, 15, 37, 0.6);
    backdrop-filter: blur(6px);
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

.confirm-dialog {
    background: #fff;
    border-radius: 20px;
    padding: 36px 40px 28px;
    width: 380px;
    max-width: 90vw;
    text-align: center;
    box-shadow: 0 24px 64px rgba(15, 23, 42, 0.35);
    animation: dialogPopIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes dialogPopIn {
    from { opacity: 0; transform: scale(0.9) translateY(20px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}

.confirm-icon {
    font-size: 48px;
    margin-bottom: 12px;
}

.confirm-text {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 8px;
}

.confirm-detail {
    font-size: 13px;
    color: #64748b;
    margin: 0 0 24px;
    line-height: 1.5;
    word-break: break-all;
}

.confirm-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
}

.confirm-btn {
    padding: 10px 36px;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.25s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    min-width: 100px;
}

.confirm-btn.cancel {
    border: 2px solid #e2e8f0;
    background: #fff;
    color: #475569;
}

.confirm-btn.cancel:hover {
    border-color: #94a3b8;
    background: #f8fafc;
    transform: translateY(-2px);
}

.confirm-btn.agree {
    border: none;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: #fff;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
}

.confirm-btn.agree:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(37, 99, 235, 0.5);
}

.confirm-btn.agree:active {
    transform: translateY(0) scale(0.97);
}

.confirm-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}

@media (max-width: 900px) {
    .content-layout {
        flex-direction: column-reverse;
    }
    .avatar-manage-panel {
        width: 100%;
    }
}
</style>