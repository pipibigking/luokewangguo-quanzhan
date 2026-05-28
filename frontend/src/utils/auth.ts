import {
    adminLogin as apiAdminLogin,
    getAdminAccounts as apiGetAdminAccounts,
    createAdminAccount as apiCreateAdminAccount,
    updateAdminAccount as apiUpdateAdminAccount,
    deleteAdminAccount as apiDeleteAdminAccount
} from '@/api'

const TOKEN_KEY = 'admin_token'
const CURRENT_ADMIN_KEY = 'current_admin'

export interface AdminAccount {
    id: number
    username: string
    created_at: string
    updated_at: string
}

export async function getAccounts(): Promise<AdminAccount[]> {
    try {
        return await apiGetAdminAccounts()
    } catch (error) {
        console.error('获取账号列表失败:', error)
        return []
    }
}

export async function addAccount(username: string, password: string): Promise<boolean> {
    try {
        await apiCreateAdminAccount(username, password)
        return true
    } catch (error: any) {
        console.error('添加账号失败:', error)
        if (error.response?.data?.detail === '账号已存在') {
            throw new Error('账号已存在')
        }
        throw new Error('添加账号失败')
    }
}

export async function updateAccount(username: string, newPassword: string): Promise<boolean> {
    try {
        await apiUpdateAdminAccount(username, newPassword)
        return true
    } catch (error) {
        console.error('更新账号失败:', error)
        return false
    }
}

export async function deleteAccount(username: string): Promise<boolean> {
    try {
        await apiDeleteAdminAccount(username)
        return true
    } catch (error: any) {
        console.error('删除账号失败:', error)
        if (error.response?.data?.detail === '至少保留一个管理员账号') {
            throw new Error('至少保留一个管理员账号')
        }
        return false
    }
}

export function isAuthenticated(): boolean {
    const token = localStorage.getItem(TOKEN_KEY)
    return token !== null && token !== ''
}

export function getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
}

export async function login(username: string, password: string): Promise<boolean> {
    try {
        const result = await apiAdminLogin(username, password)
        if (result.success && result.token) {
            localStorage.setItem(TOKEN_KEY, result.token)
            localStorage.setItem(CURRENT_ADMIN_KEY, username)
            return true
        }
        return false
    } catch (error) {
        console.error('登录失败:', error)
        return false
    }
}

export function logout(): void {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(CURRENT_ADMIN_KEY)
}

export function getCurrentAdmin(): string | null {
    return localStorage.getItem(CURRENT_ADMIN_KEY)
}

export async function verifyToken(): Promise<boolean> {
    try {
        const response = await fetch('/api/admin/verify', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        })
        if (response.ok) {
            const data = await response.json()
            return data.valid === true
        }
        return false
    } catch {
        return false
    }
}