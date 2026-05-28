<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAnnouncement, updateAnnouncement, getSiteConfig, updateSiteConfig } from '@/api'
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

// 作者信息 - 可编辑（已持久化到数据库）
interface AuthorInfo {
    author: string
    project: string
    version: string
    tech: string
    github: string
    email: string
    qq: string
    phone: string
}

const defaultInfo: AuthorInfo = {
    author: 'pipibigking',
    project: '洛克王国异色精灵图鉴',
    version: 'v1.0.0',
    tech: '前端：Vue 3 + TypeScript + Tailwind CSS + Vite\n后端：Python + FastAPI + SQLite\n部署：阿里云 ECS（CentOS 7.9）',
    github: 'https://github.com/pipibigking',
    email: '2807380340@qq.com',
    qq: '196303221',
    phone: '你的电话号码'
}

const authorInfo = ref<AuthorInfo>({ ...defaultInfo })
const editingInfo = ref(false)

function mapConfigToInfo(config: Record<string, string>): AuthorInfo {
    return {
        author: config['author_name'] || defaultInfo.author,
        project: config['project_name'] || defaultInfo.project,
        version: config['version'] || defaultInfo.version,
        tech: config['tech_stack'] || defaultInfo.tech,
        github: config['github_url'] || defaultInfo.github,
        email: config['email'] || defaultInfo.email,
        qq: config['qq'] || defaultInfo.qq,
        phone: config['phone'] || defaultInfo.phone
    }
}

function mapInfoToConfig(info: AuthorInfo): Record<string, string> {
    return {
        'author_name': info.author,
        'project_name': info.project,
        'version': info.version,
        'tech_stack': info.tech,
        'github_url': info.github,
        'email': info.email,
        'qq': info.qq,
        'phone': info.phone
    }
}

async function loadAuthorInfo() {
    try {
        const config = await getSiteConfig()
        authorInfo.value = mapConfigToInfo(config)
    } catch {
        authorInfo.value = { ...defaultInfo }
    }
}

async function saveAuthorInfo() {
    try {
        await updateSiteConfig(mapInfoToConfig(authorInfo.value))
        editingInfo.value = false
        showSuccessToast('作者信息保存成功！')
    } catch {
        showSuccessToast('保存失败')
    }
}

async function resetAuthorInfo() {
    authorInfo.value = { ...defaultInfo }
    try {
        await updateSiteConfig(mapInfoToConfig(defaultInfo))
        editingInfo.value = false
        showSuccessToast('已恢复默认信息')
    } catch {
        showSuccessToast('恢复失败')
    }
}

onMounted(() => {
    loadAnnouncement()
    loadAuthorInfo()
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
                            <span v-if="saving" class="save-icon">[S]</span>
                            <span v-else class="save-icon">[S]</span>
                            保存公告
                        </button>
                    </div>
                </div>

                <div class="info-panel">
                    <div class="info-card">
                        <div class="info-header">
                            <span class="info-icon">[A]</span>
                            <span>关于作者</span>
                        </div>
                        <div class="info-body">
                            <table class="info-table">
                                <tr>
                                    <td class="info-label">作者</td>
                                    <td v-if="!editingInfo" class="info-value">{{ authorInfo.author }}</td>
                                    <td v-else class="info-value"><input v-model="authorInfo.author" class="info-input" /></td>
                                </tr>
                                <tr>
                                    <td class="info-label">项目</td>
                                    <td v-if="!editingInfo" class="info-value">{{ authorInfo.project }}</td>
                                    <td v-else class="info-value"><input v-model="authorInfo.project" class="info-input" /></td>
                                </tr>
                                <tr>
                                    <td class="info-label">版本</td>
                                    <td v-if="!editingInfo" class="info-value">{{ authorInfo.version }}</td>
                                    <td v-else class="info-value"><input v-model="authorInfo.version" class="info-input" /></td>
                                </tr>
                                <tr>
                                    <td class="info-label">技术栈</td>
                                    <td v-if="!editingInfo" class="info-value tech-stack">{{ authorInfo.tech }}</td>
                                    <td v-else class="info-value"><textarea v-model="authorInfo.tech" class="info-input tech-input" rows="4"></textarea></td>
                                </tr>
                            </table>
                        </div>
                    </div>

                    <div class="info-card">
                        <div class="info-header">
                            <span class="info-icon">[C]</span>
                            <span>联系方式</span>
                        </div>
                        <div class="info-body">
                            <table class="info-table">
                                <tr>
                                    <td class="info-label">GitHub</td>
                                    <td v-if="!editingInfo" class="info-value">
                                        <a :href="authorInfo.github" target="_blank" class="info-link">@{{ authorInfo.author }}</a>
                                    </td>
                                    <td v-else class="info-value"><input v-model="authorInfo.github" class="info-input" /></td>
                                </tr>
                                <tr>
                                    <td class="info-label">邮箱</td>
                                    <td v-if="!editingInfo" class="info-value">{{ authorInfo.email }}</td>
                                    <td v-else class="info-value"><input v-model="authorInfo.email" class="info-input" /></td>
                                </tr>
                                <tr>
                                    <td class="info-label">QQ群</td>
                                    <td v-if="!editingInfo" class="info-value">{{ authorInfo.qq }}</td>
                                    <td v-else class="info-value"><input v-model="authorInfo.qq" class="info-input" /></td>
                                </tr>
                                <tr>
                                    <td class="info-label">电话</td>
                                    <td v-if="!editingInfo" class="info-value">{{ authorInfo.phone }}</td>
                                    <td v-else class="info-value"><input v-model="authorInfo.phone" class="info-input" /></td>
                                </tr>
                            </table>
                        </div>
                    </div>

                    <div class="info-actions">
                        <button v-if="!editingInfo" class="btn-edit" @click="editingInfo = true">编辑信息</button>
                        <template v-else>
                            <button class="btn-save-info" @click="saveAuthorInfo">保存</button>
                            <button class="btn-reset" @click="resetAuthorInfo">恢复默认</button>
                            <button class="btn-cancel" @click="editingInfo = false; loadAuthorInfo()">取消</button>
                        </template>
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
    background: rgba(241, 245, 249, 0.5);
    z-index: -1;
}

.page-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 32px;
    padding-bottom: 16px;
    border-bottom: 2px solid rgba(6, 182, 212, 0.15);
    flex-wrap: wrap;
}

.page-title {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
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
    background: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(236, 72, 153, 0.25);
    border-radius: 8px;
    display: inline-block;
    width: fit-content;
    backdrop-filter: blur(4px);
}

.editor-textarea {
    flex: 1;
    min-height: 320px;
    padding: 20px;
    border: 2px solid rgba(226, 232, 240, 0.4);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.55);
    font-size: 15px;
    font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    line-height: 1.8;
    color: #1e293b;
    resize: vertical;
    backdrop-filter: blur(6px);
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
    background: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(226, 232, 240, 0.35);
    border-radius: 20px;
    backdrop-filter: blur(4px);
}

.save-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 10px 24px;
    border: none;
    border-radius: 50px;
    background: linear-gradient(135deg, #ec4899 0%, #f472b6 50%, #db2777 100%);
    color: #ffffff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 16px rgba(236, 72, 153, 0.35);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
    min-width: 120px;
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
    box-shadow: 0 8px 24px rgba(236, 72, 153, 0.45), 0 0 0 4px rgba(236, 72, 153, 0.1);
}

.save-button:hover:not(:disabled)::before {
    left: 100%;
}

.save-button:active:not(:disabled) {
    transform: translateY(-1px) scale(0.97);
}

.save-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.save-icon {
    font-size: 13px;
    font-weight: 700;
    opacity: 0.8;
}

/* ======== 右侧信息面板 ======== */
.info-panel {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.info-card {
    background: rgba(255, 255, 255, 0.5);
    border-radius: 16px;
    border: 2px solid rgba(236, 72, 153, 0.12);
    overflow: hidden;
    backdrop-filter: blur(6px);
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.info-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
}

.info-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.12) 0%, rgba(139, 92, 246, 0.08) 100%);
    color: #1e293b;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-bottom: 1px solid rgba(236, 72, 153, 0.08);
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
    border-bottom: 1px solid rgba(226, 232, 240, 0.3);
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

.info-input {
    width: 100%;
    padding: 4px 8px;
    border: 1px solid rgba(236, 72, 153, 0.3);
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.7);
    font-size: 14px;
    color: #1e293b;
    outline: none;
    transition: border-color 0.2s;
}

.info-input:focus {
    border-color: #ec4899;
    box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.1);
}

.tech-stack {
    white-space: pre-line;
    line-height: 1.8;
    font-size: 13px;
}

.tech-input {
    resize: vertical;
    min-height: 80px;
    font-family: inherit;
}

.info-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
}

/* ======== 统一按钮风格（与粉色背景主题适配） ======== */
.btn-edit,
.btn-save-info,
.btn-reset,
.btn-cancel {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 10px 24px;
    border: none;
    border-radius: 50px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
    min-width: 90px;
}

.btn-edit::before,
.btn-save-info::before,
.btn-reset::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.6s;
}

.btn-edit:hover::before,
.btn-save-info:hover::before,
.btn-reset:hover::before {
    left: 100%;
}

/* 编辑信息 - 粉色渐变（与背景主题一致） */
.btn-edit {
    background: linear-gradient(135deg, #ec4899 0%, #f472b6 50%, #db2777 100%);
    color: #fff;
    box-shadow: 0 4px 16px rgba(236, 72, 153, 0.35);
}

.btn-edit:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 24px rgba(236, 72, 153, 0.45), 0 0 0 4px rgba(236, 72, 153, 0.1);
}

.btn-edit:active {
    transform: translateY(-1px) scale(0.97);
}

/* 保存 - 青绿色渐变 */
.btn-save-info {
    background: linear-gradient(135deg, #14b8a6 0%, #2dd4bf 50%, #0d9488 100%);
    color: #fff;
    box-shadow: 0 4px 16px rgba(20, 184, 166, 0.35);
}

.btn-save-info:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 24px rgba(20, 184, 166, 0.45), 0 0 0 4px rgba(20, 184, 166, 0.1);
}

.btn-save-info:active {
    transform: translateY(-1px) scale(0.97);
}

/* 恢复默认 - 琥珀色渐变 */
.btn-reset {
    background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 50%, #d97706 100%);
    color: #fff;
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.35);
}

.btn-reset:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.45), 0 0 0 4px rgba(245, 158, 11, 0.1);
}

.btn-reset:active {
    transform: translateY(-1px) scale(0.97);
}

/* 取消 - 毛玻璃风格 */
.btn-cancel {
    background: rgba(255, 255, 255, 0.25);
    border: 1px solid rgba(236, 72, 153, 0.25);
    color: #64748b;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
}

.btn-cancel:hover {
    background: rgba(255, 255, 255, 0.45);
    border-color: rgba(236, 72, 153, 0.4);
    color: #1e293b;
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
}

.btn-cancel:active {
    transform: translateY(-1px) scale(0.97);
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
