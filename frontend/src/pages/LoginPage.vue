<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/utils/auth'
import { createParticleBurst } from '@/utils/particleEffect'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)
const showPassword = ref(false)

async function handleLogin() {
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
    try {
        const result = await login(username.value.trim(), password.value.trim())
        if (result) {
            router.push('/admin')
        } else {
            error.value = '账号或密码错误，请重试'
            password.value = ''
            submitting.value = false
        }
    } catch {
        error.value = '登录失败，请检查网络连接'
        submitting.value = false
    }
}

function goToFront() {
    window.location.href = '/#/'
}
</script>

<template>
    <div class="login-page">
        <div class="login-panel">
            <div class="login-header">
                <div class="login-brand">
                    <div class="brand-icon">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                        </svg>
                    </div>
                    <div class="brand-text">
                        <span class="brand-name">洛克王国</span>
                        <span class="brand-sub">异色精灵管理系统</span>
                    </div>
                </div>
            </div>

            <div class="login-form-wrapper">
                <h1 class="form-title">管理员登录</h1>
                <p class="form-subtitle">欢迎回来，请登录您的账号</p>

                <form class="login-form" @submit.prevent="handleLogin">
                    <div class="input-field">
                        <label class="field-label">管理账号</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                                <circle cx="12" cy="7" r="4"/>
                            </svg>
                            <input
                                v-model="username"
                                type="text"
                                placeholder="请输入管理账号"
                                class="form-input"
                                autocomplete="username"
                            />
                        </div>
                    </div>

                    <div class="input-field">
                        <label class="field-label">管理密码</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                            </svg>
                            <input
                                v-model="password"
                                :type="showPassword ? 'text' : 'password'"
                                placeholder="请输入管理密码"
                                class="form-input"
                                autocomplete="current-password"
                            />
                            <button type="button" class="toggle-btn" @click="showPassword = !showPassword" :title="showPassword ? '隐藏密码' : '显示密码'">
                                <svg v-if="showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                                    <line x1="1" y1="1" x2="23" y2="23"/>
                                </svg>
                                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                    <circle cx="12" cy="12" r="3"/>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <p v-if="error" class="error-message">{{ error }}</p>

                    <button
                        type="submit"
                        class="login-button"
                        :disabled="submitting"
                        @click="(e) => !submitting && createParticleBurst(e.currentTarget as HTMLElement, '#38bdf8')"
                    >
                        <svg v-if="submitting" class="spin-icon" width="18" height="18" viewBox="0 0 24 24" fill="none">
                            <circle class="spin" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-dasharray="180" transform="rotate(-90 12 12)"/>
                        </svg>
                        {{ submitting ? '验证中...' : '登 录' }}
                    </button>
                </form>

                <button class="back-button" @click="goToFront">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 12H5"/>
                        <path d="m12 19-7-7 7-7"/>
                    </svg>
                    返回前台
                </button>
            </div>

            <div class="login-footer">
                <span>屁屁的洛克王国精灵管理系统</span>
            </div>
        </div>

        <div class="login-visual">
            <img
                src="/images/others/dimoenter.png"
                alt="洛克王国"
                class="visual-image"
            />
            <div class="visual-overlay"></div>
            <div class="visual-gradient"></div>
            <div class="visual-content">
                <h2 class="visual-title">和我一起探索洛克王国世界的精灵叭！</h2>
                <p class="visual-description">记录每一只独特的精灵，守护洛克王国的珍贵记忆</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
.login-page {
    display: flex;
    min-height: 100vh;
    background: #f8fafc;
}

.login-panel {
    flex: 0 0 52%;
    display: flex;
    flex-direction: column;
    padding: 32px 52px;
    background: #ffffff;
    box-shadow: 8px 0 32px rgba(0, 0, 0, 0.04);
}

.login-header {
    margin-bottom: 24px;
}

.login-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
}

.brand-text {
    display: flex;
    flex-direction: column;
}

.brand-name {
    font-size: 19px;
    font-weight: 700;
    color: #1e293b;
    letter-spacing: 0.5px;
}

.brand-sub {
    font-size: 13px;
    color: #64748b;
    letter-spacing: 0.3px;
}

.login-form-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.form-title {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}

.form-subtitle {
    font-size: 15px;
    color: #64748b;
    margin: 0 0 28px 0;
    font-weight: 500;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.input-field {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.field-label {
    font-size: 15px;
    font-weight: 600;
    color: #475569;
    letter-spacing: 0.3px;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.input-icon {
    position: absolute;
    left: 16px;
    color: #94a3b8;
    pointer-events: none;
}

.form-input {
    width: 100%;
    padding: 15px 16px 15px 48px;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 500;
    color: #1e293b;
    background: #f8fafc;
    outline: none;
    transition: all 0.2s ease;
    font-family: inherit;
}

.form-input::placeholder {
    color: #94a3b8;
}

.form-input:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
}

.form-input:focus {
    background: #ffffff;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.toggle-btn {
    position: absolute;
    right: 14px;
    background: none;
    border: none;
    cursor: pointer;
    color: #94a3b8;
    padding: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: all 0.2s;
}

.toggle-btn:hover {
    color: #2563eb;
    background: rgba(37, 99, 235, 0.06);
}

.error-message {
    font-size: 14px;
    color: #dc2626;
    font-weight: 500;
    margin: 0;
    padding: 12px 16px;
    background: rgba(220, 38, 38, 0.05);
    border: 1px solid rgba(220, 38, 38, 0.15);
    border-radius: 8px;
    animation: shake 0.3s ease;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%, 60% { transform: translateX(-4px); }
    40%, 80% { transform: translateX(4px); }
}

.login-button {
    width: 100%;
    padding: 16px;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    cursor: pointer;
    transition: all 0.25s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    letter-spacing: 1px;
    margin-top: 8px;
    position: relative;
    overflow: hidden;
}

.login-button:hover:not(:disabled) {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
    transform: translateY(-1px);
}

.login-button:active:not(:disabled) {
    transform: translateY(0);
}

.login-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.spin-icon {
    color: #ffffff;
}

.spin {
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.back-button {
    margin-top: 28px;
    padding: 12px 20px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background: transparent;
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: fit-content;
}

.back-button:hover {
    color: #2563eb;
    border-color: #2563eb;
    background: rgba(37, 99, 235, 0.04);
}

.login-footer {
    margin-top: auto;
    padding-top: 28px;
}

.login-footer span {
    font-size: 13px;
    color: #94a3b8;
}

.login-visual {
    flex: 1;
    position: relative;
    overflow: hidden;
}

.visual-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
    transition: transform 8s ease;
}

.login-page:hover .visual-image {
    transform: scale(1.01);
}

.visual-overlay {
    position: absolute;
    inset: 0;
    background: rgba(15, 23, 42, 0.6);
}

.visual-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        135deg,
        rgba(37, 99, 235, 0.15) 0%,
        transparent 50%,
        rgba(13, 110, 253, 0.1) 100%
    );
}

.visual-content {
    position: absolute;
    bottom: 32px;
    left: 36px;
    z-index: 2;
    max-width: 260px;
}

.visual-title {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.visual-description {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.85);
    margin: 0;
    line-height: 1.3;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
    .login-page {
        flex-direction: column-reverse;
    }

    .login-panel {
        flex: none;
        padding: 20px 20px;
        box-shadow: none;
    }

    .login-visual {
        flex: none;
        height: 200px;
    }

    .visual-content {
        bottom: 20px;
        left: 20px;
        max-width: 220px;
    }

    .visual-title {
        font-size: 18px;
    }

    .visual-description {
        font-size: 12px;
    }
}
</style>
