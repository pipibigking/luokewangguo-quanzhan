<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAnnouncement, updateAnnouncement } from '@/api'
import type { Announcement } from '@/types'

const content = ref('')
const loading = ref(true)
const saving = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const lastUpdated = ref('')

let toastTimer: ReturnType<typeof setTimeout> | null = null

function showSuccessToast(msg: string) {
    toastMessage.value = msg
    showToast.value = true
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => {
        showToast.value = false
    }, 3000)
}

function formatTime(iso: string): string {
    if (!iso) return ''
    const d = new Date(iso)
    const pad = (n: number) => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadAnnouncement() {
    loading.value = true
    try {
        const data: Announcement = await getAnnouncement()
        content.value = data.content || ''
        lastUpdated.value = data.updated_at ? formatTime(data.updated_at) : ''
    } catch (err) {
        console.error('加载公告失败:', err)
        showSuccessToast('加载公告失败，请检查网络连接')
    } finally {
        loading.value = false
    }
}

async function handleSave() {
    if (saving.value) return
    saving.value = true
    try {
        const data: Announcement = await updateAnnouncement({ content: content.value })
        lastUpdated.value = data.updated_at ? formatTime(data.updated_at) : ''
        showSuccessToast('公告保存成功！')
    } catch (err) {
        console.error('保存公告失败:', err)
        showSuccessToast('保存失败，请重试')
    } finally {
        saving.value = false
    }
}

onMounted(() => {
    loadAnnouncement()
})
</script>

<template>
    <div class="announcement-page">
        <div class="page-header">
            <h2 class="page-title">📢 公告管理</h2>
            <p v-if="lastUpdated" class="page-meta">最后更新：{{ lastUpdated }}</p>
        </div>

        <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <span>加载公告中...</span>
        </div>

        <template v-else>
            <div class="editor-layout">
                <div class="editor-panel">
                    <label class="panel-label">编辑公告内容</label>
                    <textarea
                        v-model="content"
                        class="editor-textarea"
                        placeholder="请输入公告内容..."
                        rows="12"
                    ></textarea>
                    <div class="editor-actions">
                        <span class="char-count">{{ content.length }} 字</span>
                        <button
                            class="save-button"
                            :class="{ 'is-saving': saving }"
                            :disabled="saving"
                            @click="handleSave"
                        >
                            <span v-if="saving" class="save-icon">⏳</span>
                            <span v-else class="save-icon">💾</span>
                            保存公告
                        </button>
                    </div>
                </div>

                <div class="preview-panel">
                    <label class="panel-label">前台预览效果</label>
                    <div class="preview-card">
                        <div class="preview-card-header">
                            <span class="preview-dot"></span>
                            <span>系统公告</span>
                        </div>
                        <div class="preview-card-body">
                            <p v-if="content.trim()" class="preview-text">{{ content }}</p>
                            <p v-else class="preview-placeholder">公告内容为空，前台将不显示公告栏</p>
                        </div>
                    </div>
                    <p class="preview-hint">↑ 以上为前台用户看到的公告效果</p>
                </div>
            </div>
        </template>

        <Transition name="toast">
            <div v-if="showToast" class="toast-bar">
                <span class="toast-icon">✅</span>
                <span>{{ toastMessage }}</span>
            </div>
        </Transition>
    </div>
</template>

<style scoped>
.announcement-page {
    max-width: 1100px;
    margin: 0 auto;
}

.page-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 32px;
    flex-wrap: wrap;
}

.page-title {
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
}

.page-meta {
    font-size: 13px;
    color: #94a3b8;
    margin: 0;
}

.loading-state {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 64px 0;
    justify-content: center;
    color: #64748b;
    font-size: 15px;
}

.loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid rgba(99, 102, 241, 0.15);
    border-top-color: #6366f1;
    border-right-color: #8b5cf6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.editor-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}

.editor-panel,
.preview-panel {
    display: flex;
    flex-direction: column;
}

.panel-label {
    font-size: 14px;
    font-weight: 600;
    color: #475569;
    margin-bottom: 12px;
}

.editor-textarea {
    flex: 1;
    min-height: 320px;
    padding: 20px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    background: #ffffff;
    font-size: 15px;
    font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    line-height: 1.8;
    color: #1e293b;
    resize: vertical;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.editor-textarea::placeholder {
    color: #cbd5e1;
}

.editor-textarea:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1), 0 0 20px rgba(99, 102, 241, 0.08);
}

.editor-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
}

.char-count {
    font-size: 13px;
    color: #94a3b8;
}

.save-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 32px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
    position: relative;
    overflow: hidden;
}

.save-button::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 12px;
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%);
    opacity: 0;
    transition: opacity 0.25s ease;
}

.save-button span {
    position: relative;
    z-index: 1;
}

.save-button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(99, 102, 241, 0.45);
}

.save-button:hover:not(:disabled)::before {
    opacity: 1;
}

.save-button:active:not(:disabled) {
    transform: translateY(0) scale(0.98);
}

.save-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.save-icon {
    font-size: 18px;
}

.preview-panel {
    gap: 4px;
}

.preview-card {
    flex: 1;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(15, 23, 42, 0.5), 0 0 0 1px rgba(99, 102, 241, 0.2);
    display: flex;
    flex-direction: column;
}

.preview-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 16px 24px;
    background: linear-gradient(135deg, #0f2847 0%, #1e3a5f 50%, #0f2847 100%);
    color: #e2e8f0;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 1px;
    border-bottom: 1px solid rgba(99, 102, 241, 0.2);
}

.preview-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #60a5fa;
    box-shadow: 0 0 12px rgba(96, 165, 250, 0.7);
    animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
    0%, 100% { box-shadow: 0 0 8px rgba(96, 165, 250, 0.5); }
    50% { box-shadow: 0 0 20px rgba(96, 165, 250, 0.9); }
}

.preview-card-body {
    flex: 1;
    padding: 24px;
    background: linear-gradient(180deg, #0a0f25 0%, #1e293b 50%, #0f172a 100%);
    min-height: 260px;
}

.preview-text {
    color: rgba(255, 255, 255, 0.9);
    font-size: 15px;
    line-height: 2;
    white-space: pre-wrap;
    word-break: break-word;
    text-shadow: 0 0 20px rgba(147, 197, 253, 0.3);
}

.preview-placeholder {
    color: rgba(255, 255, 255, 0.3);
    font-size: 14px;
    font-style: italic;
    text-align: center;
    padding-top: 40px;
}

.preview-hint {
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
    margin-top: 12px;
}

.toast-bar {
    position: fixed;
    top: 32px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 32px;
    border-radius: 12px;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
    box-shadow: 0 8px 32px rgba(16, 185, 129, 0.4);
    z-index: 9999;
    pointer-events: none;
    white-space: nowrap;
}

.toast-icon {
    font-size: 18px;
}

.toast-enter-active {
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toast-leave-active {
    transition: all 0.3s ease-in;
}

.toast-enter-from {
    opacity: 0;
    transform: translateX(-50%) translateY(-24px) scale(0.85);
}

.toast-leave-to {
    opacity: 0;
    transform: translateX(-50%) translateY(-16px) scale(0.9);
}

@media (max-width: 768px) {
    .editor-layout {
        grid-template-columns: 1fr;
    }

    .preview-card-body {
        min-height: 200px;
    }

    .toast-bar {
        top: 16px;
        padding: 12px 24px;
        font-size: 14px;
    }
}
</style>
