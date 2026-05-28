<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAccounts, addAccount, updateAccount, deleteAccount, getCurrentAdmin, type AdminAccount } from '@/utils/auth'
import { createParticleBurst } from '@/utils/particleEffect'

const accounts = ref<AdminAccount[]>([])
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)
const toastMsg = ref('')
const toastType = ref<'success' | 'error'>('success')
let toastTimer: number | null = null

const newAccount = ref({ username: '', password: '' })
const editingAccount = ref<AdminAccount | null>(null)
const editingPassword = ref('')
const deletingUsername = ref('')
const showAddPwd = ref(false)
const showEditPwd = ref(false)

function showToast(msg: string, type: 'success' | 'error' = 'success') {
    toastMsg.value = msg
    toastType.value = type
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = window.setTimeout(() => { toastMsg.value = '' }, 3000)
}

async function loadAccounts() {
    accounts.value = await getAccounts()
}

function openAddModal() {
    newAccount.value = { username: '', password: '' }
    showAddModal.value = true
}

function handleAddAccountClick(e: MouseEvent) {
    createParticleBurst(e.currentTarget as HTMLElement, '#06b6d4')
    openAddModal()
}

function closeAddModal() {
    showAddModal.value = false
    showAddPwd.value = false
}

async function handleAdd() {
    if (!newAccount.value.username.trim()) {
        showToast('请输入账号', 'error')
        return
    }
    if (!newAccount.value.password.trim()) {
        showToast('请输入密码', 'error')
        return
    }
    if (newAccount.value.password.length < 4) {
        showToast('密码长度至少4位', 'error')
        return
    }
    
    try {
        await addAccount(newAccount.value.username.trim(), newAccount.value.password.trim())
        showToast('账号添加成功', 'success')
        closeAddModal()
        await loadAccounts()
    } catch (error: any) {
        showToast(error.message || '添加失败', 'error')
    }
}

function openEditModal(account: AdminAccount) {
    editingAccount.value = account
    editingPassword.value = ''
    showEditModal.value = true
}

function closeEditModal() {
    showEditModal.value = false
    editingAccount.value = null
    showEditPwd.value = false
}

async function handleUpdate() {
    if (!editingAccount.value) return
    if (!editingPassword.value.trim()) {
        showToast('请输入新密码', 'error')
        return
    }
    if (editingPassword.value.length < 4) {
        showToast('密码长度至少4位', 'error')
        return
    }
    
    const success = await updateAccount(editingAccount.value.username, editingPassword.value.trim())
    if (success) {
        showToast('密码更新成功', 'success')
        closeEditModal()
        await loadAccounts()
    } else {
        showToast('更新失败', 'error')
    }
}

function confirmDelete(username: string) {
    deletingUsername.value = username
    showDeleteConfirm.value = true
}

function closeDeleteConfirm() {
    showDeleteConfirm.value = false
    deletingUsername.value = ''
}

async function handleDelete() {
    if (!deletingUsername.value) return
    
    const currentAdmin = getCurrentAdmin()
    if (deletingUsername.value === currentAdmin) {
        showToast('不能删除当前登录的账号', 'error')
        closeDeleteConfirm()
        return
    }
    
    try {
        const success = await deleteAccount(deletingUsername.value)
        if (success) {
            showToast('账号删除成功', 'success')
            closeDeleteConfirm()
            await loadAccounts()
        } else {
            showToast('删除失败', 'error')
            closeDeleteConfirm()
        }
    } catch (error: any) {
        showToast(error.message || '删除失败', 'error')
        closeDeleteConfirm()
    }
}

onMounted(() => {
    loadAccounts()
})
</script>

<template>
    <div class="account-manage-page">
        <!-- Toast 提示 -->
        <div v-if="toastMsg" class="toast" :class="toastType">{{ toastMsg }}</div>

        <div class="page-header">
            <h2 class="page-title">账号管理</h2>
            <button class="btn-add" @click="handleAddAccountClick">
                <span class="btn-add-icon">+</span>
                添加账号
            </button>
        </div>

        <div class="accounts-table-wrapper">
            <table class="accounts-table">
                <thead>
                    <tr>
                        <th>账号名称</th>
                        <th>密码</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="account in accounts" :key="account.username" class="account-row">
                        <td class="col-username">
                            <span class="username-text">{{ account.username }}</span>
                        </td>
                        <td class="col-password">
                            <span class="password-mask">••••••••</span>
                        </td>
                        <td class="col-status">
                            <span v-if="account.username === getCurrentAdmin()" class="status-tag current-user">
                                当前登录
                            </span>
                            <span v-else class="status-tag normal-user">正常</span>
                        </td>
                        <td class="col-actions">
                            <button class="btn-action btn-edit" title="修改密码" @click="openEditModal(account)">
                                🔑
                            </button>
                            <button 
                                class="btn-action btn-delete" 
                                :disabled="account.username === getCurrentAdmin()"
                                :title="account.username === getCurrentAdmin() ? '不能删除当前账号' : '删除账号'"
                                @click="confirmDelete(account.username)"
                            >
                                🗑️
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 添加账号弹窗 -->
        <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
            <div class="modal-card">
                <div class="modal-header">
                    <h3 class="modal-title">添加新账号</h3>
                    <button class="modal-close" @click="closeAddModal">×</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">账号名称</label>
                        <input
                            v-model="newAccount.username"
                            type="text"
                            placeholder="请输入账号名称"
                            class="form-input"
                        />
                    </div>
                    <div class="form-group">
                            <label class="form-label">登录密码</label>
                            <div class="pwd-input-wrap">
                                <input
                                    v-model="newAccount.password"
                                    :type="showAddPwd ? 'text' : 'password'"
                                    placeholder="请输入登录密码（至少4位）"
                                    class="form-input"
                                />
                                <button type="button" class="pwd-toggle" @click="showAddPwd = !showAddPwd" :title="showAddPwd ? '隐藏密码' : '显示密码'">
                                    <svg v-if="showAddPwd" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                                    <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                                </button>
                            </div>
                        </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel" @click="closeAddModal">取消</button>
                    <button class="btn-save" @click="handleAdd">确认添加</button>
                </div>
            </div>
        </div>

        <!-- 修改密码弹窗 -->
        <div v-if="showEditModal && editingAccount" class="modal-overlay" @click.self="closeEditModal">
            <div class="modal-card">
                <div class="modal-header">
                    <h3 class="modal-title">修改密码</h3>
                    <button class="modal-close" @click="closeEditModal">×</button>
                </div>
                <div class="modal-body">
                    <p class="edit-hint">正在修改账号：<strong>{{ editingAccount.username }}</strong></p>
                    <div class="form-group">
                            <label class="form-label">新密码</label>
                            <div class="pwd-input-wrap">
                                <input
                                    v-model="editingPassword"
                                    :type="showEditPwd ? 'text' : 'password'"
                                    placeholder="请输入新密码（至少4位）"
                                    class="form-input"
                                />
                                <button type="button" class="pwd-toggle" @click="showEditPwd = !showEditPwd" :title="showEditPwd ? '隐藏密码' : '显示密码'">
                                    <svg v-if="showEditPwd" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                                    <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                                </button>
                            </div>
                        </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel" @click="closeEditModal">取消</button>
                    <button class="btn-save" @click="handleUpdate">确认修改</button>
                </div>
            </div>
        </div>

        <!-- 删除确认弹窗 -->
        <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="closeDeleteConfirm">
            <div class="modal-card modal-confirm">
                <div class="modal-header modal-header-danger">
                    <h3 class="modal-title">确认删除</h3>
                    <button class="modal-close" @click="closeDeleteConfirm">×</button>
                </div>
                <div class="modal-body confirm-body">
                    <div class="confirm-icon">⚠️</div>
                    <p class="confirm-text">
                        确定要删除账号 <strong>"{{ deletingUsername }}"</strong> 吗？
                    </p>
                    <p class="confirm-hint">此操作不可撤销，且至少保留一个管理员账号</p>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel" @click="closeDeleteConfirm">取消</button>
                    <button class="btn-save btn-danger" @click="handleDelete">确认删除</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.account-manage-page {
    position: relative;
    z-index: 1;
    min-height: 100%;
}

.account-manage-page::before {
    content: '';
    position: fixed;
    top: 0;
    left: 220px;
    right: 0;
    bottom: 0;
    background: url('/images/bg/小狮鹫蓝色云朵.png') center center / cover no-repeat;
    z-index: -2;
}

.account-manage-page::after {
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

.btn-add {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 28px;
    border: none;
    border-radius: 50px;
    font-size: 15px;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 6px 20px rgba(6, 182, 212, 0.35), 0 0 0 0 rgba(6, 182, 212, 0.4);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
}

.btn-add::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.6s;
}

.btn-add:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 28px rgba(6, 182, 212, 0.5), 0 0 0 4px rgba(6, 182, 212, 0.1);
}

.btn-add:hover::before {
    left: 100%;
}

.btn-add:active {
    transform: translateY(-1px) scale(0.97);
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}

.btn-add-icon {
    font-size: 20px;
    font-weight: 300;
}

.accounts-table-wrapper {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.75) 0%, rgba(248, 250, 252, 0.7) 100%);
    border-radius: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.7);
    border: 2px solid rgba(99, 102, 241, 0.12);
    overflow: hidden;
    backdrop-filter: blur(8px);
}

.accounts-table {
    width: 100%;
    border-collapse: collapse;
}

.accounts-table thead {
    background: linear-gradient(135deg, #1e293b 0%, #1e3a5f 50%, #0f2847 100%);
}

.accounts-table th {
    padding: 14px 16px;
    font-size: 13px;
    font-weight: 700;
    color: #cbd5e1;
    text-align: left;
    letter-spacing: 0.5px;
}

.accounts-table tbody tr {
    transition: background 0.2s ease;
    border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.accounts-table tbody tr:last-child {
    border-bottom: none;
}

.accounts-table tbody tr:hover {
    background: rgba(99, 102, 241, 0.04);
}

.accounts-table td {
    padding: 16px;
    vertical-align: middle;
}

.username-text {
    font-size: 15px;
    font-weight: 700;
    color: #1e293b;
}

.password-mask {
    font-size: 16px;
    color: #94a3b8;
    letter-spacing: 2px;
}

.status-tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}

.current-user {
    background: rgba(16, 185, 129, 0.12);
    color: #059669;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.normal-user {
    background: rgba(148, 163, 184, 0.12);
    color: #64748b;
    border: 1px solid rgba(148, 163, 184, 0.3);
}

.action-buttons {
    display: flex;
    gap: 6px;
}

.btn-action {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    border: none;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
}

.btn-action:hover:not(:disabled) {
    transform: translateY(-2px) scale(1.1);
}

.btn-edit:hover {
    background: rgba(59, 130, 246, 0.12);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.btn-delete:hover:not(:disabled) {
    background: rgba(239, 68, 68, 0.12);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}

.btn-action:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* 弹窗样式 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(6px);
    display: flex;
    justify-content: center;
    align-items: flex-start;
    z-index: 1000;
    padding: 48px 20px;
    overflow-y: auto;
    animation: overlayIn 0.25s ease;
}

@keyframes overlayIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.modal-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 20px;
    width: 100%;
    max-width: 480px;
    box-shadow: 0 24px 80px rgba(15, 23, 42, 0.35), 0 0 0 1px rgba(99, 102, 241, 0.1) inset;
    animation: modalIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    border: 2px solid rgba(99, 102, 241, 0.15);
    backdrop-filter: blur(12px);
}

@keyframes modalIn {
    from {
        opacity: 0;
        transform: translateY(40px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.modal-confirm {
    max-width: 440px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 28px;
    background: linear-gradient(135deg, #1e293b 0%, #1e3a5f 50%, #0f2847 100%);
    border-radius: 20px 20px 0 0;
    border-bottom: 2px solid rgba(99, 102, 241, 0.2);
}

.modal-header-danger {
    background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #7f1d1d 100%);
    border-bottom-color: rgba(239, 68, 68, 0.3);
}

.modal-title {
    font-size: 18px;
    font-weight: 800;
    color: #fff;
    letter-spacing: 1px;
    margin: 0;
}

.modal-close {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.25);
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    font-size: 22px;
    cursor: pointer;
    transition: all 0.25s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-close:hover {
    background: rgba(239, 68, 68, 0.85);
    border-color: rgba(239, 68, 68, 0.85);
    transform: rotate(90deg) scale(1.1);
}

.modal-body {
    padding: 24px 28px;
}

.confirm-body {
    text-align: center;
    padding: 36px 28px;
}

.edit-hint {
    font-size: 14px;
    color: #475569;
    margin: 0 0 20px 0;
    padding: 12px;
    background: #f8fafc;
    border-radius: 10px;
}

.confirm-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.confirm-text {
    font-size: 16px;
    color: #334155;
    font-weight: 500;
    line-height: 1.6;
    margin: 0;
}

.confirm-hint {
    font-size: 13px;
    color: #94a3b8;
    margin: 8px 0 0;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
}

.form-label {
    font-size: 14px;
    font-weight: 700;
    color: #334155;
}

.form-input {
    padding: 10px 14px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    color: #1e293b;
    background: #f8fafc;
    outline: none;
    transition: all 0.2s ease;
}

.form-input:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
    background: #fff;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 28px 20px;
    border-top: 1px solid #e2e8f0;
}

.btn-cancel {
    padding: 10px 24px;
    border: 2px solid rgba(226, 232, 240, 0.6);
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    color: #475569;
    background: rgba(255, 255, 255, 0.75);
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-cancel:hover {
    border-color: #94a3b8;
    background: #f1f5f9;
    transform: translateY(-1px);
}

.btn-save {
    padding: 10px 28px;
    border: none;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
}

.btn-save:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(99, 102, 241, 0.45);
}

.btn-danger {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
    box-shadow: 0 8px 22px rgba(239, 68, 68, 0.45);
}

/* Toast */
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
    from {
        opacity: 0;
        transform: translateX(-50%) translateY(-20px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateX(-50%) translateY(0) scale(1);
    }
}

.pwd-input-wrap {
    position: relative;
    display: flex;
    align-items: center;
}

.pwd-input-wrap .form-input {
    padding-right: 44px;
}

.pwd-toggle {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
    color: #94a3b8;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;
    border-radius: 4px;
}

.pwd-toggle:hover {
    color: #6366f1;
    background: rgba(99, 102, 241, 0.08);
}
</style>
