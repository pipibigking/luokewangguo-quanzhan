import axios from 'axios'
import type { Pet, Announcement } from '@/types'

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

export async function togglePetActive(id: number): Promise<Pet> {
  const response = await api.patch(`/pets/${id}/toggle-active`)
  return response.data
}

export async function batchActivatePets(): Promise<{ message: string; count: number }> {
  const response = await api.patch('/pets/batch-activate')
  return response.data
}

export async function batchDeactivatePets(): Promise<{ message: string; count: number }> {
  const response = await api.patch('/pets/batch-deactivate')
  return response.data
}

export async function getAnnouncement(): Promise<Announcement> {
  const response = await api.get('/announcement')
  return response.data
}

export async function updateAnnouncement(content: { content: string }): Promise<Announcement> {
  const response = await api.put('/announcement', content)
  return response.data
}

// 分组颜色 API
export async function getGroupColors(): Promise<Record<string, string>> {
  const response = await api.get('/group-colors')
  return response.data
}

export async function updateGroupColor(groupName: string, color: string): Promise<{ group_name: string; color: string }> {
  const response = await api.put(`/group-colors/${encodeURIComponent(groupName)}`, { color })
  return response.data
}

// 管理员账号 API
export interface AdminAccount {
  id: number
  username: string
  created_at: string
  updated_at: string
}

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

export const IMAGE_BASE_URL = '/images'