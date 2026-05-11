<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/utils/auth'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

function handleLogin() {
    error.value = ''
    if (!username.value.trim()) {
        error.value = '请输入管理员账号'
        return
    }
    if (!password.value.trim()) {
        error.value = '请输入管理员密码'
        return
    }
    submitting.value = true
    setTimeout(() => {
        if (login(username.value.trim(), password.value.trim())) {
            router.push('/admin')
        } else {
            error.value = '账号或密码错误，请重试'
            password.value = ''
        }
        submitting.value = false
    }, 400)
}

function goToFront() {
    window.location.href = '/#/'
}
</script>

<template>
    <div class="login-page">
        <div class="login-bg"></div>
        <div class="login-card">
            <div class="login-header">
                <span class="login-icon">🔐</span>
                <h2 class="login-title">管理员登录</h2>
                <p class="login-subtitle">精灵管理后台</p>
            </div>

            <form class="login-form" @submit.prevent="handleLogin">
                <div class="input-group">
                    <label class="input-label">管理账号</label>
                    <input
                        v-model="username"
                        type="text"
                        placeholder="请输入管理账号"
                        class="login-input"
                        autocomplete="username"
                    />
                </div>

                <div class="input-group">
                    <label class="input-label">管理密码</label>
                    <input
                        v-model="password"
                        type="password"
                        placeholder="请输入管理密码"
                        class="login-input"
                        autocomplete="current-password"
                    />
                </div>

                <p v-if="error" class="error-msg">{{ error }}</p>

                <button
                    type="submit"
                    class="login-btn"
                    :disabled="submitting"
                >
                    <span v-if="submitting" class="btn-spin"></span>
                    {{ submitting ? '验证中...' : '登 录' }}
                </button>
            </form>

            <button class="back-link" @click="goToFront">← 返回前台</button>
        </div>
    </div>
</template>

<style scoped>
.login-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #0f2847 70%, #0f172a 100%);
    position: relative;
    overflow: hidden;
}

.login-bg {
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.12) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.06) 0%, transparent 70%);
    pointer-events: none;
}

.login-card {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.92) 100%);
    border-radius: 24px;
    padding: 48px 40px 36px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 32px 80px rgba(15, 23, 42, 0.5), 0 0 0 1px rgba(99, 102, 241, 0.15) inset;
    position: relative;
    z-index: 1;
    border: 2px solid rgba(99, 102, 241, 0.2);
    animation: cardIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes cardIn {
    from {
        opacity: 0;
        transform: translateY(50px) scale(0.92);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.login-header {
    text-align: center;
    margin-bottom: 36px;
}

.login-icon {
    font-size: 56px;
    display: block;
    margin-bottom: 16px;
    filter: drop-shadow(0 0 16px rgba(99, 102, 241, 0.4));
    animation: iconPulse 3s ease-in-out infinite;
}

@keyframes iconPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}

.login-title {
    font-size: 24px;
    font-weight: 800;
    color: #1e293b;
    letter-spacing: 2px;
    margin: 0 0 8px 0;
}

.login-subtitle {
    font-size: 14px;
    color: #64748b;
    font-weight: 500;
    letter-spacing: 1px;
    margin: 0;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.input-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.input-label {
    font-size: 14px;
    font-weight: 700;
    color: #334155;
}

.login-input {
    width: 100%;
    padding: 14px 18px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 500;
    color: #1e293b;
    background: #f8fafc;
    outline: none;
    transition: all 0.25s ease;
    letter-spacing: 1px;
}

.login-input:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
    background: #fff;
}

.login-input::placeholder {
    letter-spacing: 0;
    color: #cbd5e1;
}

.error-msg {
    font-size: 13px;
    color: #ef4444;
    font-weight: 600;
    margin: 0;
    padding: 8px 14px;
    background: rgba(239, 68, 68, 0.08);
    border-radius: 8px;
    text-align: center;
}

.login-btn {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    letter-spacing: 2px;
    margin-top: 8px;
}

.login-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
    transition: left 0.5s;
}

.login-btn:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(99, 102, 241, 0.5);
}

.login-btn:hover:not(:disabled)::before {
    left: 100%;
}

.login-btn:active:not(:disabled) {
    transform: translateY(-3px) scale(0.97);
}

.login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.btn-spin {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.back-link {
    display: block;
    width: 100%;
    margin-top: 28px;
    padding: 10px;
    border: none;
    border-radius: 10px;
    background: transparent;
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.back-link:hover {
    color: #6366f1;
    background: rgba(99, 102, 241, 0.06);
}
</style>
