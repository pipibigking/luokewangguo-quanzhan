<script setup lang="ts">
import type { FilterOptions } from '@/types'
import { ref, watch } from 'vue'
import { getAttributeIconPath } from '@/utils/attributeIcons'

const ATTRIBUTES = ['普', '草', '火', '水', '光', '地', '冰', '龙', '电', '毒', '虫', '武', '翼', '萌', '幽', '恶', '机', '幻']

interface Props {
  groups: string[]
  filterOptions: FilterOptions
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:filterOptions': [options: FilterOptions]
}>()

const isUpdating = ref(false)
const searchTimeout = ref<number | null>(null)

const handleGroupChange = (group: string | null) => {
  isUpdating.value = true
  emit('update:filterOptions', {
    ...props.filterOptions,
    group
  })
  setTimeout(() => { isUpdating.value = false }, 200)
}

const handleAttributeChange = (attribute: string | null) => {
  isUpdating.value = true
  emit('update:filterOptions', {
    ...props.filterOptions,
    attribute
  })
  setTimeout(() => { isUpdating.value = false }, 200)
}

const handleSearchChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = window.setTimeout(() => {
    isUpdating.value = true
    emit('update:filterOptions', {
      ...props.filterOptions,
      search: target.value
    })
    setTimeout(() => { isUpdating.value = false }, 200)
  }, 300)
}

const setSortDefault = () => {
  isUpdating.value = true
  emit('update:filterOptions', {
    ...props.filterOptions,
    sortBy: 'sort_order',
    sortOrder: 'asc'
  })
  setTimeout(() => { isUpdating.value = false }, 200)
}

const setSortPriceAsc = () => {
  isUpdating.value = true
  emit('update:filterOptions', {
    ...props.filterOptions,
    sortBy: 'price',
    sortOrder: 'asc'
  })
  setTimeout(() => { isUpdating.value = false }, 200)
}

const setSortPriceDesc = () => {
  isUpdating.value = true
  emit('update:filterOptions', {
    ...props.filterOptions,
    sortBy: 'price',
    sortOrder: 'desc'
  })
  setTimeout(() => { isUpdating.value = false }, 200)
}

const getAttributeIconStyle = (attr: string) => {
  const colors: Record<string, { bg: string; border: string }> = {
    '普': { bg: 'linear-gradient(135deg, #E5E7EB 0%, #9CA3AF 100%)', border: '#6B7280' },
    '草': { bg: 'linear-gradient(135deg, #A7F3D0 0%, #34D399 100%)', border: '#059669' },
    '火': { bg: 'linear-gradient(135deg, #FECACA 0%, #F87171 100%)', border: '#DC2626' },
    '水': { bg: 'linear-gradient(135deg, #BFDBFE 0%, #60A5FA 100%)', border: '#2563EB' },
    '光': { bg: 'linear-gradient(135deg, #FEF3C7 0%, #FCD34D 100%)', border: '#D97706' },
    '地': { bg: 'linear-gradient(135deg, #FDE68A 0%, #F59E0B 100%)', border: '#B45309' },
    '冰': { bg: 'linear-gradient(135deg, #CFFAFE 0%, #67E8F9 100%)', border: '#0891B2' },
    '龙': { bg: 'linear-gradient(135deg, #DDD6FE 0%, #8B5CF6 100%)', border: '#6D28D9' },
    '电': { bg: 'linear-gradient(135deg, #FEF9C3 0%, #FDE047 100%)', border: '#CA8A04' },
    '毒': { bg: 'linear-gradient(135deg, #F5D0FE 0%, #D946EF 100%)', border: '#A21CAF' },
    '虫': { bg: 'linear-gradient(135deg, #D9F99D 0%, #A3E635 100%)', border: '#65A30D' },
    '武': { bg: 'linear-gradient(135deg, #FECACA 0%, #EF4444 100%)', border: '#B91C1C' },
    '翼': { bg: 'linear-gradient(135deg, #DBEAFE 0%, #818CF8 100%)', border: '#4F46E5' },
    '萌': { bg: 'linear-gradient(135deg, #FCE7F3 0%, #F9A8D4 100%)', border: '#DB2777' },
    '幽': { bg: 'linear-gradient(135deg, #EDE9FE 0%, #C4B5FD 100%)', border: '#7C3AED' },
    '恶': { bg: 'linear-gradient(135deg, #E5E7EB 0%, #9CA3AF 100%)', border: '#4B5563' },
    '机': { bg: 'linear-gradient(135deg, #E5E7EB 0%, #9CA3AF 100%)', border: '#6B7280' },
    '幻': { bg: 'linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%)', border: '#EC4899' }
  }
  return colors[attr] || colors['普']
}
</script>

<template>
  <div class="filter-bar">
    <!-- 分组筛选 -->
    <div class="filter-section">
      <span class="filter-label">分组</span>
      <div class="button-group">
        <button
          @click="handleGroupChange(null)"
          class="filter-button"
          :class="{ active: !filterOptions.group, isUpdating }"
        >
          全部
        </button>
        <button
          v-for="group in groups"
          :key="group"
          @click="handleGroupChange(group)"
          class="filter-button"
          :class="{ active: filterOptions.group === group, isUpdating }"
        >
          {{ group }}
        </button>
      </div>
    </div>

    <!-- 属性筛选 -->
    <div class="filter-section">
      <span class="filter-label">属性</span>
      <div class="attribute-group">
        <button
          @click="handleAttributeChange(null)"
          class="attribute-button"
          :class="{ active: !filterOptions.attribute, isUpdating }"
        >
          全部
        </button>
        <button
          v-for="attr in ATTRIBUTES"
          :key="attr"
          @click="handleAttributeChange(attr)"
          class="attribute-icon-button"
          :class="{ active: filterOptions.attribute === attr, isUpdating }"
          :title="attr + '系'"
        >
          <img :src="getAttributeIconPath(attr)" :alt="attr" class="attribute-button-icon" />
        </button>
      </div>
    </div>

    <!-- 搜索 -->
    <div class="search-section">
      <span class="filter-label">搜索</span>
      <div class="search-box">
        <input
          type="text"
          :value="filterOptions.search"
          @input="handleSearchChange"
          placeholder="输入精灵名称"
          class="search-input"
        />
      </div>
    </div>

    <!-- 排序 -->
    <div class="sort-section">
      <span class="filter-label">排序</span>
      <div class="sort-button-group">
        <button
          @click="setSortDefault"
          class="sort-button"
          :class="{ active: filterOptions.sortBy === 'sort_order', isUpdating }"
        >
          默认排序
        </button>
        <button
          @click="setSortPriceAsc"
          class="sort-button"
          :class="{ active: filterOptions.sortBy === 'price' && filterOptions.sortOrder === 'asc', isUpdating }"
        >
          价格升序
        </button>
        <button
          @click="setSortPriceDesc"
          class="sort-button"
          :class="{ active: filterOptions.sortBy === 'price' && filterOptions.sortOrder === 'desc', isUpdating }"
        >
          价格降序
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-bar {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 252, 0.95) 100%);
  border-radius: 28px;
  padding: 32px;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.95), 0 0 0 1px rgba(96, 165, 250, 0.12);
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 36px;
  border: 2px solid rgba(96, 165, 250, 0.18);
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a2e;
  white-space: nowrap;
  min-width: 44px;
  letter-spacing: 0.3px;
}

.button-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-button {
  padding: 10px 24px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 700;
  border: 2px solid #e2e8f0;
  background: white;
  color: #475569;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.3px;
  position: relative;
  overflow: hidden;
}

.filter-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.filter-button:hover::before {
  left: 100%;
}

.filter-button:hover {
  border-color: #3b82f6;
  color: #1a1a2e;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.2);
}

.filter-button:active {
  transform: translateY(-1px) scale(0.97);
}

.filter-button.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
  }
  50% {
    box-shadow: 0 6px 30px rgba(59, 130, 246, 0.7);
  }
}

.attribute-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.attribute-button {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  border: 2px solid #e2e8f0;
  background: white;
  color: #475569;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.3px;
}

.attribute-button:hover {
  border-color: #3b82f6;
  color: #1a1a2e;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.2);
}

.attribute-button:active {
  transform: translateY(-1px) scale(0.97);
}

.attribute-button.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
  animation: pulse-glow 2s ease-in-out infinite;
}

.attribute-icon-button {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 3px solid #e2e8f0;
  background: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.attribute-icon-button:hover {
  transform: translateY(-4px) scale(1.1);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: #3b82f6;
}

.attribute-icon-button.active {
  border-color: #3b82f6;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
  transform: scale(1.15);
  animation: attribute-pulse 2s ease-in-out infinite;
}

@keyframes attribute-pulse {
  0%, 100% {
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
    transform: scale(1.15);
  }
  50% {
    box-shadow: 0 6px 28px rgba(59, 130, 246, 0.7);
    transform: scale(1.18);
  }
}

.attribute-button-icon {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 300px;
}

.search-box {
  flex: 1;
}

.search-input {
  width: 100%;
  padding: 14px 24px;
  border-radius: 24px;
  border: 2px solid #e2e8f0;
  font-size: 15px;
  transition: all 0.3s ease;
  outline: none;
  background: #fafbff;
  font-weight: 500;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 5px rgba(59, 130, 246, 0.18);
  background: white;
}

.sort-section {
  display: flex;
  align-items: center;
  gap: 14px;
}

.sort-button-group {
  display: flex;
  gap: 8px;
}

.sort-button {
  padding: 10px 24px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 700;
  border: 2px solid #e2e8f0;
  background: white;
  color: #475569;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.3px;
  position: relative;
  overflow: hidden;
}

.sort-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.sort-button:hover::before {
  left: 100%;
}

.sort-button:hover {
  border-color: #3b82f6;
  color: #1a1a2e;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.2);
}

.sort-button:active {
  transform: translateY(-1px) scale(0.97);
}

.sort-button.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
  animation: pulse-glow 2s ease-in-out infinite;
}

.isUpdating {
  opacity: 0.7;
  pointer-events: none;
}
</style>
