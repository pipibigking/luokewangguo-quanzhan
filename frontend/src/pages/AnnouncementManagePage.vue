<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAnnouncement, updateAnnouncement } from '@/api'
import type { Announcement } from '@/types'
import { createParticleBurst } from '@/utils/particleEffect'

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

function handleSaveClick(e: MouseEvent) {
    createParticleBurst(e.currentTarget as HTMLElement, '#06b6d4')
    handleSave()
}

onMounted(() => {
    loadAnnouncement()
})
</script>

<template>
    <div class="announcement-page">
        <div class="page-header">
            <h2 class="page-title">公告管理</h2>
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
                            @click="handleSaveClick"
                        >
                            <span v-if="saving" class="save-icon">⏳</span>
                            <span v-else class="save-icon">💾</span>
                            保存公告
                        </button>
                    </div>
                </div>

                <div class="info-panel">
                    <div class="info-card">
                        <div class="info-header">
                            <span class="info-icon">🎨</span>
                            <span>关于作者</span>
                        </div>
                        <div class="info-body">
                            <table class="info-table">
                                <tr>
                                    <td class="info-label">作者</td>
                                    <td class="info-value">pipibigking</td>
                                </tr>
                                <tr>
                                    <td class="info-label">项目</td>
                                    <td class="info-value">洛克王国异色精灵图鉴</td>
                                </tr>
                                <tr>
                                    <td class="info-label">版本</td>
                                    <td class="info-value">v1.0.0</td>
                                </tr>
                                <tr>
                                    <td class="info-label">技术栈</td>
                                    <td class="info-value">Vue3 + FastAPI</td>
                                </tr>
                            </table>
                        </div>
                    </div>

                    <div class="info-card">
                        <div class="info-header">
                            <span class="info-icon">📮</span>
                            <span>联系方式</span>
                        </div>
                        <div class="info-body">
                            <table class="info-table">
                                <tr>
                                    <td class="info-label">GitHub</td>
                                    <td class="info-value">
                                        <a href="https://github.com/pipibigking" target="_blank" class="info-link">@pipibigking</a>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="info-label">邮箱</td>
                                    <td class="info-value">pipibigking@example.com</td>
                                </tr>
                                <tr>
                                    <td class="info-label">QQ群</td>
                                    <td class="info-value">123456789</td>
                                </tr>
                            </table>
                        </div>
                    </div>

                    <div class="info-card">
                        <div class="info-header">
                            <span class="info-icon">📊</span>
                            <span>数据统计</span>
                        </div>
                        <div class="info-body">
                            <table class="info-table">
                                <tr>
                                    <td class="info-label">精灵数量</td>
                                    <td class="info-value">21 种</td>
                                </tr>
                                <tr>
                                    <td class="info-label">属性种类</td>
                                    <td class="info-value">18 种</td>
                                </tr>
                                <tr>
                                    <td class="info-label">捕捉球</td>
                                    <td class="info-value">14 种</td>
                                </tr>
                            </table>
                        </div>
                    </div>
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
    position: relative;
    min-height: 100%;
}

.announcement-page::before {
    content: '';
    position: fixed;
    top: 0;
    left: 220px;
    right: 0;
    bottom: 0;
    background: url('/images/bg/独角兽音符粉色.png') center center / cover no-repeat;
    z-index: -2;
}

.announcement-page::after {
    content: '';
    position: fixed;
    top: 0;
    left: 220px;
    right: 0;
    bottom: 0;
    background: rgba(241, 245, 249, 0.75);
    z-index: -1;
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

.editor-panel {
    display: flex;
    flex-direction: column;
}

.panel-label {
    font-size: 14px;
    font-weight: 600;
    color: #475569;
    margin-bottom: 12px;
    padding: 8px 16px;
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(236, 72, 153, 0.3);
    border-radius: 8px;
    display: inline-block;
    width: fit-content;
    backdrop-filter: blur(4px);
}

.editor-textarea {
    flex: 1;
    min-height: 320px;
    padding: 20px;
    border: 2px solid rgba(226, 232, 240, 0.6);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.75);
    font-size: 15px;
    font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    line-height: 1.8;
    color: #1e293b;
    resize: vertical;
    backdrop-filter: blur(8px);
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
    padding: 6px 14px;
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(226, 232, 240, 0.5);
    border-radius: 20px;
    backdrop-filter: blur(4px);
}

.save-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 32px;
    border: none;
    border-radius: 50px;
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 6px 20px rgba(6, 182, 212, 0.35), 0 0 0 0 rgba(6, 182, 212, 0.4);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
}

.save-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.6s;
}

.save-button span {
    position: relative;
    z-index: 1;
}

.save-button:hover:not(:disabled) {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 28px rgba(6, 182, 212, 0.5), 0 0 0 4px rgba(6, 182, 212, 0.1);
}

.save-button:hover:not(:disabled)::before {
    left: 100%;
}

.save-button:active:not(:disabled) {
    transform: translateY(-1px) scale(0.97);
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}

.save-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.save-icon {
    font-size: 18px;
}

/* ======== 右侧信息面板 ======== */
.info-panel {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.info-card {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 16px;
    border: 2px solid rgba(236, 72, 153, 0.15);
    overflow: hidden;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.info-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}

.info-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
    color: #1e293b;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-bottom: 1px solid rgba(236, 72, 153, 0.1);
}

.info-icon {
    font-size: 18px;
}

.info-body {
    padding: 16px 20px;
}

.info-table {
    width: 100%;
    border-collapse: collapse;
}

.info-table tr {
    border-bottom: 1px solid rgba(226, 232, 240, 0.4);
}

.info-table tr:last-child {
    border-bottom: none;
}

.info-table td {
    padding: 10px 0;
    font-size: 14px;
}

.info-label {
    color: #64748b;
    font-weight: 500;
    width: 80px;
    white-space: nowrap;
}

.info-value {
    color: #1e293b;
    font-weight: 600;
    text-align: right;
}

.info-link {
    color: #ec4899;
    text-decoration: none;
    transition: color 0.2s ease;
}

.info-link:hover {
    color: #db2777;
    text-decoration: underline;
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

    .toast-bar {
        top: 16px;
        padding: 12px 24px;
        font-size: 14px;
    }
}
</style>
