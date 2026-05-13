export interface Pet {
  id: number
  name: string
  group: string
  image_url: string
  price: number
  attributes: string[]
  description: string
  abilities: string[]
  is_active: boolean
  sort_order: number
}

export interface FilterOptions {
  group: string | null
  search: string
  sortBy: string
  sortOrder: 'asc' | 'desc'
  attribute: string | null
}

export interface Announcement {
  id: number
  content: string
  updated_at: string
}