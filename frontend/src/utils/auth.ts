import { 
    adminLogin as apiAdminLogin, 
    getAdminAccounts as apiGetAdminAccounts,
    createAdminAccount as apiCreateAdminAccount,
    updateAdminAccount as apiUpdateAdminAccount,
    deleteAdminAccount as apiDeleteAdminAccount,
    type AdminAccount as ApiAdminAccount
} from '@/api'

const AUTH_KEY = 'admin_authenticated'
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
    return localStorage.getItem(AUTH_KEY) === 'true'
}

export async function login(username: string, password: string): Promise<boolean> {
    try {
        const result = await apiAdminLogin(username, password)
        if (result.success) {
            localStorage.setItem(AUTH_KEY, 'true')
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
    localStorage.removeItem(AUTH_KEY)
    localStorage.removeItem(CURRENT_ADMIN_KEY)
}

export function getCurrentAdmin(): string | null {
    return localStorage.getItem(CURRENT_ADMIN_KEY)
}
