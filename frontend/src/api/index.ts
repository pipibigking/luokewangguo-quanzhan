import axios from 'axios'
import type { Pet, Announcement, Message } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export async function getPets(
  group?: string,
  search?: string,
  sortBy: string = 'id',
  sortOrder: 'asc' | 'desc' = 'asc',
  attribute?: string,
  includeInactive: boolean = false
): Promise<Pet[]> {
  const params: Record<string, string | boolean> = {
    sort_by: sortBy,
    sort_order: sortOrder,
    include_inactive: includeInactive
  }

  if (group) params.group = group
  if (search) params.search = search
  if (attribute) params.attribute = attribute

  const response = await api.get('/pets', { params })
  return response.data
}

export async function getGroups(): Promise<string[]> {
  const response = await api.get('/groups')
  return response.data
}

export async function getPetById(id: number): Promise<Pet> {
  const response = await api.get(`/pets/${id}`)
  return response.data
}

export async function createPet(pet: Omit<Pet, 'id'>): Promise<Pet> {
  const response = await api.post('/pets', pet)
  return response.data
}

export async function updatePet(id: number, pet: Partial<Pet>): Promise<Pet> {
  const response = await api.put(`/pets/${id}`, pet)
  return response.data
}

export async function deletePet(id: number): Promise<void> {
  await api.delete(`/pets/${id}`)
}
// 切换宠物状态 API
export async function togglePetActive(id: number): Promise<Pet> {
  const response = await api.patch(`/pets/${id}/toggle-active`)
  return response.data
}
// 批量激活宠物 API
export async function batchActivatePets(): Promise<{ message: string; count: number }> {
  const response = await api.patch('/pets/batch-activate')
  return response.data
}
// 批量停用宠物 API
export async function batchDeactivatePets(): Promise<{ message: string; count: number }> {
  const response = await api.patch('/pets/batch-deactivate')
  return response.data
}
// 获取公告 API
export async function getAnnouncement(): Promise<Announcement> {
  const response = await api.get('/announcement')
  return response.data
}
// 更新公告 API
export async function updateAnnouncement(content: { content: string }): Promise<Announcement> {
  const response = await api.put('/announcement', content)
  return response.data
}

// 分组颜色 API
export async function getGroupColors(): Promise<Record<string, string>> {
  const response = await api.get('/group-colors')
  return response.data
}
// 更新分组颜色 API
export async function updateGroupColor(groupName: string, color: string): Promise<{ group_name: string; color: string }> {
  const response = await api.put(`/group-colors/${encodeURIComponent(groupName)}`, { color })
  return response.data
}

export async function renameGroup(groupName: string, newName: string): Promise<{ message: string; old_name: string; new_name: string }> {
  const response = await api.put(`/groups/${encodeURIComponent(groupName)}`, { new_name: newName })
  return response.data
}

export async function batchUpdateSortOrder(items: { id: number; sort_order: number }[]): Promise<{ message: string; count: number }> {
  const safeItems = items.map(item => ({
    id: Number(item.id),
    sort_order: Number(item.sort_order)
  }))
  const res = await fetch('/api/pets/sort-order', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items: safeItems })
  })
  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: res.statusText }))
    const error: any = new Error('Request failed')
    error.response = { status: res.status, data: errData }
    throw error
  }
  return res.json()
}

// 管理员账号 API
export interface AdminAccount {
  id: number
  username: string
  created_at: string
  updated_at: string
}
// 获取管理员账号 API
export async function getAdminAccounts(): Promise<AdminAccount[]> {
  const response = await api.get('/admin/accounts')
  return response.data
}

export async function createAdminAccount(username: string, password: string): Promise<AdminAccount> {
  const response = await api.post('/admin/accounts', { username, password })
  return response.data
}

export async function updateAdminAccount(username: string, password: string): Promise<AdminAccount> {
  const response = await api.put(`/admin/accounts/${encodeURIComponent(username)}`, { password })
  return response.data
}

export async function deleteAdminAccount(username: string): Promise<void> {
  await api.delete(`/admin/accounts/${encodeURIComponent(username)}`)
}

export async function adminLogin(username: string, password: string): Promise<{ success: boolean; username: string; message: string }> {
  const response = await api.post('/admin/login', { username, password })
  return response.data
}

export async function getMessages(includeRead: boolean = true): Promise<Message[]> {
  const response = await api.get('/messages', { params: { include_read: includeRead } })
  return response.data
}

export async function getUnreadCount(): Promise<{ count: number }> {
  const response = await api.get('/messages/unread-count')
  return response.data
}

export async function createMessage(nickname: string, content: string): Promise<Message> {
  const response = await api.post('/messages', { nickname, content })
  return response.data
}

export async function markMessageRead(messageId: number): Promise<void> {
  await api.put(`/messages/${messageId}/read`)
}

export async function markAllMessagesRead(): Promise<void> {
  await api.put('/messages/read-all')
}

export async function deleteMessage(messageId: number): Promise<void> {
  await api.delete(`/messages/${messageId}`)
}

export async function uploadImage(file: File): Promise<{ url: string; filename: string }> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  })
  if (!response.ok) {
    const errData = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(errData.detail || '上传失败')
  }
  return response.json()
}

export const IMAGE_BASE_URL = '/images'