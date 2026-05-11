<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { getPets, getGroups, createPet, updatePet, deletePet, togglePetActive, batchActivatePets, batchDeactivatePets } from '@/api'
import type { Pet } from '@/types'
import { getGroupColor as getGroupColorUtil, loadGroupColors, saveGroupColor, initGroupColors } from '@/utils/groupColors'
import { getAttributeIconPath } from '@/utils/attributeIcons'

const ATTRIBUTES = ['普', '草', '火', '水', '光', '地', '冰', '龙', '电', '毒', '虫', '武', '翼', '萌', '幽', '恶', '机', '幻']

const toastMsg = ref('')
const toastType = ref<'success' | 'error'>('success')
let toastTimer: number | null = null

function showToast(msg: string, type: 'success' | 'error' = 'success') {
    toastMsg.value = msg
    toastType.value = type
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = window.setTimeout(() => { toastMsg.value = '' }, 3000)
}

function getFullUrl(url: string): string {
    if (!url) return ''
    if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/')) return url
    return '/' + url
}

interface PetFormData {
    name: string
    group: string
    image_url: string
    price: number
    attributes: string[]
    description: string
    abilities: string[]
    is_active: boolean
    is_custom_group: boolean
    custom_group: string
    custom_group_color: string
}

const emptyForm = (): PetFormData => ({
    name: '',
    group: '',
    image_url: '',
    price: 0,
    attributes: [],
    description: '',
    abilities: [],
    is_active: true,
    is_custom_group: false,
    custom_group: '',
    custom_group_color: '#6366F1'
})

const pets = ref<Pet[]>([])
const groups = ref<string[]>([])
const loading = ref(true)
const error = ref('')
const searchKeyword = ref('')
const filterGroup = ref<string | null>(null)
const filterAttribute = ref<string | null>(null)

const showFormModal = ref(false)
const showDeleteConfirm = ref(false)
const formTitle = ref('添加精灵')
const formData = reactive<PetFormData>(emptyForm())
const editingPetId = ref<number | null>(null)
const deletingPet = ref<Pet | null>(null)
const formSubmitting = ref(false)
const deleteSubmitting = ref(false)
const batchSubmitting = ref(false)

const sortBy = ref('id')
const sortOrder = ref<'asc' | 'desc'>('asc')

let searchTimer: number | null = null
const debouncedSearch = ref('')

function handleSearchInput(e: Event) {
    const target = e.target as HTMLInputElement
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = window.setTimeout(() => {
        debouncedSearch.value = target.value
    }, 300)
}

const getGroupColor = (group: string) => {
    return getGroupColorUtil(group)
}

const PRESET_COLORS = [
    '#6366F1', '#8B5CF6', '#EC4899', '#F97316',
    '#10B981', '#06B6D4', '#3B82F6', '#EAB308',
    '#EF4444', '#14B8A6', '#F43F5E', '#6366F1',
    '#84CC16', '#A855F7', '#0EA5E9', '#F59E0B'
]

const filteredPets = computed(() => {
    let result = [...pets.value]
    if (debouncedSearch.value) {
        const s = debouncedSearch.value.toLowerCase()
        result = result.filter(p => p.name.toLowerCase().includes(s))
    }
    if (filterGroup.value) {
        result = result.filter(p => p.group === filterGroup.value)
    }
    if (filterAttribute.value) {
        result = result.filter(p => p.attributes.includes(filterAttribute.value!))
    }
    result.sort((a, b) => {
        const va = sortBy.value === 'price' ? a.price : a.id
        const vb = sortBy.value === 'price' ? b.price : b.id
        return sortOrder.value === 'asc' ? va - vb : vb - va
    })
    return result
})

const effectiveGroup = computed(() => {
    if (formData.is_custom_group && formData.custom_group.trim()) {
        return formData.custom_group.trim()
    }
    return formData.group
})

async function loadPets() {
    loading.value = true
    error.value = ''
    try {
        const data = await getPets(undefined, undefined, sortBy.value, sortOrder.value, undefined, true)
        pets.value = data
    } catch (err) {
        error.value = '加载精灵数据失败，请检查后端服务'
        showToast('加载精灵列表失败', 'error')
        console.error(err)
    } finally {
        loading.value = false
    }
}

async function loadGroups() {
    try {
        const data = await getGroups()
        groups.value = data
    } catch (err) {
        console.error('加载分组失败:', err)
    }
}

function openAddModal() {
    editingPetId.value = null
    formTitle.value = '添加精灵'
    Object.assign(formData, emptyForm())
    showFormModal.value = true
}

function openEditModal(pet: Pet) {
    editingPetId.value = pet.id
    formTitle.value = '编辑精灵'
    const isCustom = !groups.value.includes(pet.group) && !!pet.group
    formData.name = pet.name
    formData.image_url = pet.image_url
    formData.price = pet.price
    formData.attributes = [...pet.attributes]
    formData.description = pet.description
    formData.abilities = pet.abilities ? [...pet.abilities] : []
    formData.is_active = pet.is_active
    formData.is_custom_group = isCustom
    formData.custom_group = isCustom ? pet.group : ''
    formData.group = isCustom ? '' : pet.group
    formData.custom_group_color = getGroupColorUtil(pet.group)
    showFormModal.value = true
}

function closeFormModal() {
    showFormModal.value = false
}

async function handleFormSubmit() {
    if (!formData.name.trim()) return
    if (!formData.image_url.trim()) return
    const group = effectiveGroup.value
    if (!group) return

    formSubmitting.value = true
    try {
        const payload = {
            name: formData.name.trim(),
            group,
            image_url: formData.image_url.trim(),
            price: formData.price,
            attributes: formData.attributes,
            description: formData.description.trim(),
            abilities: formData.abilities.filter(a => a.trim()),
            is_active: formData.is_active
        }

        if (editingPetId.value) {
            await updatePet(editingPetId.value, payload)
            showToast('精灵更新成功', 'success')
        } else {
            await createPet(payload)
            showToast('精灵添加成功', 'success')
        }
        if (formData.is_custom_group) {
            saveGroupColor(group, formData.custom_group_color)
        }
        closeFormModal()
        await loadPets()
        await loadGroups()
    } catch (err) {
        showToast(editingPetId.value ? '更新精灵失败' : '添加精灵失败', 'error')
        console.error('保存精灵失败:', err)
    } finally {
        formSubmitting.value = false
    }
}

function confirmDelete(pet: Pet) {
    deletingPet.value = pet
    showDeleteConfirm.value = true
}

function closeDeleteConfirm() {
    showDeleteConfirm.value = false
    deletingPet.value = null
}

async function handleDelete() {
    if (!deletingPet.value) return
    deleteSubmitting.value = true
    try {
        await deletePet(deletingPet.value.id)
        showToast('精灵已删除', 'success')
        closeDeleteConfirm()
        await loadPets()
        await loadGroups()
    } catch (err) {
        showToast('删除精灵失败', 'error')
        console.error('删除精灵失败:', err)
    } finally {
        deleteSubmitting.value = false
    }
}

async function handleToggleActive(pet: Pet) {
    try {
        await togglePetActive(pet.id)
        showToast(pet.is_active ? '精灵已下架' : '精灵已上架', 'success')
        await loadPets()
    } catch (err) {
        showToast('切换状态失败', 'error')
        console.error('切换状态失败:', err)
    }
}

async function handleBatchActivate() {
    batchSubmitting.value = true
    try {
        const result = await batchActivatePets()
        showToast(result.message, 'success')
        await loadPets()
    } catch (err) {
        showToast('批量上架失败', 'error')
        console.error('批量上架失败:', err)
    } finally {
        batchSubmitting.value = false
    }
}

async function handleBatchDeactivate() {
    batchSubmitting.value = true
    try {
        const result = await batchDeactivatePets()
        showToast(result.message, 'success')
        await loadPets()
    } catch (err) {
        showToast('批量下架失败', 'error')
        console.error('批量下架失败:', err)
    } finally {
        batchSubmitting.value = false
    }
}

function toggleAttribute(attr: string) {
    const idx = formData.attributes.indexOf(attr)
    if (idx >= 0) {
        formData.attributes.splice(idx, 1)
    } else {
        formData.attributes.push(attr)
    }
}

function addAbility() {
    formData.abilities.push('')
}

function removeAbility(index: number) {
    formData.abilities.splice(index, 1)
}

function updateAbility(index: number, value: string) {
    formData.abilities[index] = value
}

function handleGroupSelect(e: Event) {
    const target = e.target as HTMLSelectElement
    const value = target.value
    if (value === '__custom__') {
        formData.is_custom_group = true
        formData.group = ''
    } else {
        formData.is_custom_group = false
        formData.group = value
        formData.custom_group = ''
    }
}

async function updateGroupColor(group: string, color: string) {
    try {
        await saveGroupColor(group, color)
        showToast(`分组 "${group}" 颜色已更新`, 'success')
    } catch (error) {
        showToast('颜色更新失败', 'error')
    }
}

watch(debouncedSearch, () => {}, { flush: 'post' })

onMounted(async () => {
    await initGroupColors() // 初始化加载分组颜色
    loadPets()
    loadGroups()
})
</script>

<template>
    <div class="pet-manage-page">
        <!-- Toast 提示 -->
        <div v-if="toastMsg" class="toast" :class="toastType">{{ toastMsg }}</div>

        <div class="page-header">
            <h2 class="page-title">✨ 精灵管理</h2>
            <div class="header-actions">
                <button class="btn-add" @click="openAddModal">
                    <span class="btn-add-icon">+</span>
                    添加精灵
                </button>
                <button
                    class="btn-batch btn-batch-on"
                    :disabled="batchSubmitting"
                    @click="handleBatchActivate"
                >
                    📤 一键上架
                </button>
                <button
                    class="btn-batch btn-batch-off"
                    :disabled="batchSubmitting"
                    @click="handleBatchDeactivate"
                >
                    📥 一键下架
                </button>
            </div>
        </div>

        <div class="filter-bar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input
                    type="text"
                    :value="searchKeyword"
                    @input="handleSearchInput"
                    placeholder="搜索精灵名称..."
                    class="search-input"
                />
            </div>

            <div class="filter-group">
                <span class="filter-label">分组</span>
                <select
                    :value="filterGroup || ''"
                    @change="filterGroup = ($event.target as HTMLSelectElement).value || null"
                    class="filter-select"
                >
                    <option value="">全部分组</option>
                    <option v-for="g in groups" :key="g" :value="g">{{ g }}</option>
                </select>
            </div>

            <div class="filter-attributes">
                <span class="filter-label">属性</span>
                <div class="attribute-buttons">
                    <button
                        class="attr-btn"
                        :class="{ active: !filterAttribute }"
                        @click="filterAttribute = null"
                    >
                        全部
                    </button>
                    <button
                        v-for="attr in ATTRIBUTES"
                        :key="attr"
                        class="attr-btn attr-icon-btn"
                        :class="{ active: filterAttribute === attr }"
                        :title="attr + '系'"
                        @click="filterAttribute = filterAttribute === attr ? null : attr"
                    >
                        <img :src="getAttributeIconPath(attr)" :alt="attr" class="attr-icon-img" />
                    </button>
                </div>
            </div>

            <button class="btn-refresh" @click="loadPets">
                <span class="refresh-icon">🔄</span>
                刷新
            </button>
        </div>

        <div class="group-color-manager">
            <h3 class="section-title-text">🎨 分组颜色管理</h3>
            <div class="color-cards-grid">
                <div v-for="group in groups" :key="group" class="color-card">
                    <div class="color-card-header">
                        <span
                            class="color-preview"
                            :style="{ background: getGroupColor(group) }"
                        ></span>
                        <span class="group-name">{{ group }}</span>
                    </div>
                    <div class="color-card-body">
                        <input
                            type="color"
                            :value="getGroupColor(group)"
                            @input="updateGroupColor(group, ($event.target as HTMLInputElement).value)"
                            class="color-picker-small"
                        />
                        <span class="color-hex">{{ getGroupColor(group) }}</span>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="loading" class="state-container">
            <div class="loading-spinner"></div>
            <p class="state-text">正在加载精灵数据...</p>
        </div>

        <div v-else-if="error" class="state-container state-error">
            <p class="state-text error-text">{{ error }}</p>
            <button class="btn-retry" @click="loadPets">重新加载</button>
        </div>

        <div v-else class="table-wrapper">
            <table class="pet-table">
                <thead>
                    <tr>
                        <th class="col-thumb">缩略图</th>
                        <th class="col-name">名称</th>
                        <th class="col-group">分组</th>
                        <th class="col-attr">属性</th>
                        <th class="col-price">价格</th>
                        <th class="col-status">状态</th>
                        <th class="col-actions">操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="filteredPets.length === 0">
                        <td colspan="7" class="empty-row">暂无匹配的精灵数据</td>
                    </tr>
                    <tr
                        v-for="pet in filteredPets"
                        :key="pet.id"
                        class="pet-row"
                    >
                        <td class="col-thumb">
                            <img :src="getFullUrl(pet.image_url)" :alt="pet.name" class="pet-thumb" />
                        </td>
                        <td class="col-name">
                            <span class="pet-name-text">{{ pet.name }}</span>
                        </td>
                        <td class="col-group">
                            <span
                                class="group-tag"
                                :style="{ background: getGroupColor(pet.group) }"
                            >
                                {{ pet.group }}
                            </span>
                        </td>
                        <td class="col-attr">
                            <div class="attr-icons">
                                <img
                                    v-for="attr in pet.attributes"
                                    :key="attr"
                                    :src="getAttributeIconPath(attr)"
                                    :alt="attr"
                                    :title="attr + '系'"
                                    class="attr-icon-sm"
                                />
                                <span v-if="!pet.attributes || pet.attributes.length === 0" class="no-attr">-</span>
                            </div>
                        </td>
                        <td class="col-price">
                            <span class="price-tag">{{ pet.price }}</span>
                        </td>
                        <td class="col-status">
                            <span class="status-tag" :class="pet.is_active ? 'status-active' : 'status-inactive'">
                                {{ pet.is_active ? '已上架' : '已下架' }}
                            </span>
                        </td>
                        <td class="col-actions">
                            <div class="action-buttons">
                                <button class="btn-action btn-edit" title="编辑" @click="openEditModal(pet)">
                                    ✏️
                                </button>
                                <button
                                    class="btn-action"
                                    :class="pet.is_active ? 'btn-offline' : 'btn-online'"
                                    :title="pet.is_active ? '下架' : '上架'"
                                    @click="handleToggleActive(pet)"
                                >
                                    {{ pet.is_active ? '📥' : '📤' }}
                                </button>
                                <button class="btn-action btn-delete" title="删除" @click="confirmDelete(pet)">
                                    🗑️
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 添加/编辑弹窗 -->
        <div v-if="showFormModal" class="modal-overlay" @click.self="closeFormModal">
            <div class="modal-card">
                <div class="modal-header">
                    <h3 class="modal-title">{{ formTitle }}</h3>
                    <button class="modal-close" @click="closeFormModal">×</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">精灵名称</label>
                        <input
                            v-model="formData.name"
                            type="text"
                            placeholder="请输入精灵名称"
                            class="form-input"
                        />
                    </div>

                    <div class="form-group">
                        <label class="form-label">精灵图片 URL</label>
                        <input
                            v-model="formData.image_url"
                            type="text"
                            placeholder="请输入图片地址"
                            class="form-input"
                        />
                        <div v-if="formData.image_url" class="image-preview">
                            <img :src="getFullUrl(formData.image_url)" alt="预览" class="preview-img" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">精灵属性（多选）</label>
                        <div class="attr-select-grid">
                            <button
                                v-for="attr in ATTRIBUTES"
                                :key="attr"
                                class="attr-select-btn"
                                :class="{ selected: formData.attributes.includes(attr) }"
                                @click="toggleAttribute(attr)"
                            >
                                <img :src="getAttributeIconPath(attr)" :alt="attr" class="attr-select-icon" />
                                <span>{{ attr }}</span>
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">购买价格</label>
                        <input
                            v-model.number="formData.price"
                            type="number"
                            placeholder="请输入价格"
                            class="form-input"
                            min="0"
                            step="1"
                        />
                    </div>

                    <div class="form-group">
                        <label class="form-label">精灵描述</label>
                        <textarea
                            v-model="formData.description"
                            placeholder="请输入精灵描述"
                            class="form-textarea"
                            rows="3"
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label class="form-label">
                            能力特点
                            <button type="button" class="add-ability-btn" @click="addAbility" title="添加特点">+</button>
                        </label>
                        <div class="abilities-list-edit">
                            <div v-for="(ability, index) in formData.abilities" :key="index" class="ability-item">
                                <input
                                    type="text"
                                    :value="ability"
                                    @input="updateAbility(index, ($event.target as HTMLInputElement).value)"
                                    placeholder="输入能力特点..."
                                    class="form-input ability-input"
                                />
                                <button type="button" class="remove-ability-btn" @click="removeAbility(index)" title="删除">×</button>
                            </div>
                            <p v-if="formData.abilities.length === 0" class="no-abilities-hint">暂无能力特点，点击 + 添加</p>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">分组选择</label>
                        <select
                            :value="formData.is_custom_group ? '__custom__' : formData.group"
                            @change="handleGroupSelect"
                            class="form-input"
                        >
                            <option value="" disabled>请选择分组</option>
                            <option v-for="g in groups" :key="g" :value="g">{{ g }}</option>
                            <option value="__custom__">自定义分组...</option>
                        </select>
                        <input
                            v-if="formData.is_custom_group"
                            v-model="formData.custom_group"
                            type="text"
                            placeholder="输入自定义分组名称"
                            class="form-input custom-group-input"
                        />
                        <div v-if="formData.is_custom_group" class="color-picker-section">
                            <label class="form-label">组别颜色</label>
                            <div class="color-picker-row">
                                <input
                                    type="color"
                                    v-model="formData.custom_group_color"
                                    class="color-input-native"
                                />
                                <span
                                    class="color-preview-dot"
                                    :style="{ background: formData.custom_group_color }"
                                ></span>
                                <span class="color-hex-text">{{ formData.custom_group_color }}</span>
                            </div>
                            <div class="preset-colors">
                                <button
                                    v-for="c in PRESET_COLORS"
                                    :key="c"
                                    class="preset-color-btn"
                                    :class="{ selected: formData.custom_group_color === c }"
                                    :style="{ background: c }"
                                    @click="formData.custom_group_color = c"
                                    :title="c"
                                ></button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel" @click="closeFormModal">取消</button>
                    <button
                        class="btn-save"
                        :disabled="formSubmitting || !formData.name.trim() || !formData.image_url.trim() || !effectiveGroup"
                        @click="handleFormSubmit"
                    >
                        <span v-if="formSubmitting" class="btn-spinner"></span>
                        {{ formSubmitting ? '保存中...' : '保存' }}
                    </button>
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
                        确定要删除精灵 <strong>"{{ deletingPet?.name }}"</strong> 吗？
                    </p>
                    <p class="confirm-hint">此操作不可撤销</p>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel" @click="closeDeleteConfirm">取消</button>
                    <button
                        class="btn-save btn-danger"
                        :disabled="deleteSubmitting"
                        @click="handleDelete"
                    >
                        <span v-if="deleteSubmitting" class="btn-spinner"></span>
                        {{ deleteSubmitting ? '删除中...' : '确认删除' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.pet-manage-page {
    position: relative;
    z-index: 1;
}

/* ======== 页面头部 ======== */
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.page-title {
    font-size: 24px;
    font-weight: 800;
    color: #1e293b;
    letter-spacing: 1px;
    margin: 0;
}

.btn-add {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 28px;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
    position: relative;
    overflow: hidden;
}

.btn-add::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
    transition: left 0.5s;
}

.btn-add:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(99, 102, 241, 0.5);
}

.btn-add:hover::before {
    left: 100%;
}

.btn-add:active {
    transform: translateY(-3px) scale(0.97);
}

.btn-add-icon {
    font-size: 20px;
    font-weight: 300;
    line-height: 1;
}

/* ======== 批量操作按钮 ======== */
.header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.btn-batch {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 24px;
    border: 2px solid transparent;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    white-space: nowrap;
}

.btn-batch:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
}

.btn-batch-on {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);
}

.btn-batch-on:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(16, 185, 129, 0.5);
}

.btn-batch-off {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
    box-shadow: 0 6px 20px rgba(249, 115, 22, 0.35);
}

.btn-batch-off:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(249, 115, 22, 0.5);
}

/* ======== 筛选栏 ======== */
.filter-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.92) 100%);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(99, 102, 241, 0.12);
}

/* ======== 分组颜色管理器 ======== */
.group-color-manager {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.92) 100%);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(99, 102, 241, 0.12);
}

.section-title-text {
    font-size: 16px;
    font-weight: 800;
    color: #1e293b;
    margin: 0 0 16px 0;
    letter-spacing: 0.5px;
}

.color-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
}

.color-card {
    background: #fff;
    border-radius: 12px;
    padding: 14px;
    border: 2px solid #e2e8f0;
    transition: all 0.25s ease;
}

.color-card:hover {
    border-color: #6366f1;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.15);
    transform: translateY(-2px);
}

.color-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.color-preview {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    border: 2px solid rgba(15, 23, 42, 0.1);
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.1);
}

.group-name {
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
}

.color-card-body {
    display: flex;
    align-items: center;
    gap: 10px;
}

.color-picker-small {
    width: 36px;
    height: 32px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    padding: 2px;
    background: #fff;
    transition: border-color 0.2s ease;
}

.color-picker-small:hover {
    border-color: #6366f1;
}

.color-hex {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    font-family: monospace;
}

.filter-label {
    font-size: 13px;
    font-weight: 700;
    color: #475569;
    white-space: nowrap;
    margin-right: 4px;
}

.search-box {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    min-width: 200px;
}

.search-icon {
    font-size: 16px;
    flex-shrink: 0;
}

.search-input {
    flex: 1;
    padding: 10px 16px;
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    font-size: 14px;
    font-weight: 500;
    outline: none;
    transition: all 0.25s ease;
    background: #f8fafc;
    color: #1e293b;
}

.search-input:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
    background: #fff;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.filter-select {
    padding: 10px 36px 10px 14px;
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    font-size: 14px;
    font-weight: 600;
    outline: none;
    transition: all 0.25s ease;
    background: #f8fafc;
    color: #1e293b;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23475569' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
}

.filter-select:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
    background-color: #fff;
}

.filter-attributes {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.attribute-buttons {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    align-items: center;
}

.attr-btn {
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    border: 2px solid #e2e8f0;
    background: #fff;
    color: #475569;
    cursor: pointer;
    transition: all 0.2s ease;
}

.attr-btn:hover {
    border-color: #6366f1;
    color: #6366f1;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.attr-btn.active {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #fff;
    border-color: transparent;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}

.attr-icon-btn {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    padding: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.attr-icon-img {
    width: 24px;
    height: 24px;
    object-fit: contain;
}

.btn-refresh {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 10px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    border: 2px solid #e2e8f0;
    background: #fff;
    color: #475569;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.btn-refresh:hover {
    border-color: #6366f1;
    color: #6366f1;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.btn-refresh:active {
    transform: translateY(-2px) scale(0.97);
}

.refresh-icon {
    font-size: 14px;
}

/* ======== 状态容器 ======== */
.state-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.92) 100%);
    border-radius: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(99, 102, 241, 0.12);
}

.state-error {
    border-color: rgba(239, 68, 68, 0.25);
}

.loading-spinner {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(99, 102, 241, 0.15);
    border-top-color: #6366f1;
    border-right-color: #8b5cf6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 20px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.state-text {
    font-size: 15px;
    color: #475569;
    font-weight: 600;
}

.error-text {
    color: #ef4444;
    margin-bottom: 20px;
}

.btn-retry {
    padding: 10px 28px;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    cursor: pointer;
    transition: all 0.25s ease;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
}

.btn-retry:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(59, 130, 246, 0.5);
}

/* ======== 表格 ======== */
.table-wrapper {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.92) 100%);
    border-radius: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(99, 102, 241, 0.12);
    overflow: hidden;
}

.pet-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: auto;
}

.pet-table thead {
    background: linear-gradient(135deg, #1e293b 0%, #1e3a5f 50%, #0f2847 100%);
}

.pet-table th {
    padding: 14px 16px;
    font-size: 13px;
    font-weight: 700;
    color: #cbd5e1;
    text-align: left;
    letter-spacing: 0.5px;
    white-space: nowrap;
    border-bottom: 2px solid rgba(99, 102, 241, 0.25);
}

.col-thumb { width: 72px; }
.col-name { min-width: 120px; }
.col-group { min-width: 100px; }
.col-attr { min-width: 140px; }
.col-price { width: 90px; }
.col-status { width: 96px; }
.col-actions { width: 140px; }

.pet-table tbody tr {
    transition: background 0.2s ease;
    border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.pet-table tbody tr:last-child {
    border-bottom: none;
}

.pet-table tbody tr:hover {
    background: rgba(99, 102, 241, 0.04);
}

.pet-table td {
    padding: 12px 16px;
    vertical-align: middle;
}

.empty-row {
    text-align: center !important;
    padding: 48px 16px !important;
    color: #94a3b8;
    font-size: 15px;
    font-weight: 600;
}

.pet-thumb {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    object-fit: cover;
    border: 2px solid rgba(99, 102, 241, 0.15);
    transition: all 0.2s ease;
    background: #f1f5f9;
}

.pet-row:hover .pet-thumb {
    transform: scale(1.08);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.pet-name-text {
    font-size: 15px;
    font-weight: 700;
    color: #1e293b;
}

.group-tag {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 0.3px;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.15);
}

.attr-icons {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    align-items: center;
}

.attr-icon-sm {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    object-fit: contain;
    background: #f8fafc;
    border: 1px solid rgba(0, 0, 0, 0.06);
    transition: all 0.2s ease;
}

.pet-row:hover .attr-icon-sm {
    transform: scale(1.1);
}

.no-attr {
    font-size: 13px;
    color: #94a3b8;
}

.price-tag {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 800;
    color: #fff;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
}

.status-tag {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.3px;
    white-space: nowrap;
}

.status-active {
    background: rgba(16, 185, 129, 0.12);
    color: #059669;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-inactive {
    background: rgba(148, 163, 184, 0.12);
    color: #64748b;
    border: 1px solid rgba(148, 163, 184, 0.3);
}

.action-buttons {
    display: flex;
    gap: 6px;
}

.btn-action {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    border: none;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
}

.btn-action:hover {
    transform: translateY(-2px) scale(1.1);
}

.btn-action:active {
    transform: translateY(-2px) scale(0.95);
}

.btn-edit:hover {
    background: rgba(59, 130, 246, 0.12);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.btn-online:hover {
    background: rgba(16, 185, 129, 0.12);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.btn-offline:hover {
    background: rgba(245, 158, 11, 0.12);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
}

.btn-delete:hover {
    background: rgba(239, 68, 68, 0.12);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}

/* ======== 弹窗 ======== */
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
    background: #fff;
    border-radius: 20px;
    width: 100%;
    max-width: 620px;
    box-shadow: 0 24px 80px rgba(15, 23, 42, 0.35), 0 0 0 1px rgba(99, 102, 241, 0.1) inset;
    animation: modalIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    border: 2px solid rgba(99, 102, 241, 0.15);
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
    line-height: 1;
}

.modal-close:hover {
    background: rgba(239, 68, 68, 0.85);
    border-color: rgba(239, 68, 68, 0.85);
    transform: rotate(90deg) scale(1.1);
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.modal-body {
    padding: 24px 28px;
    max-height: 60vh;
    overflow-y: auto;
}

.confirm-body {
    text-align: center;
    padding: 36px 28px;
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

/* ======== 表单 ======== */
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

.form-input::placeholder {
    color: #cbd5e1;
}

.form-textarea {
    padding: 10px 14px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    color: #1e293b;
    background: #f8fafc;
    outline: none;
    transition: all 0.2s ease;
    resize: vertical;
    font-family: inherit;
}

.form-textarea:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
    background: #fff;
}

.form-textarea::placeholder {
    color: #cbd5e1;
}

/* 能力特点编辑 */
.add-ability-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    border: 2px solid #6366f1;
    background: #fff;
    color: #6366f1;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    margin-left: 8px;
    transition: all 0.2s ease;
}

.add-ability-btn:hover {
    background: #6366f1;
    color: #fff;
    transform: scale(1.1);
}

.abilities-list-edit {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.ability-item {
    display: flex;
    gap: 10px;
    align-items: center;
}

.ability-input {
    flex: 1;
}

.remove-ability-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    border: 2px solid #ef4444;
    background: #fff;
    color: #ef4444;
    font-size: 20px;
    font-weight: 300;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.remove-ability-btn:hover {
    background: #ef4444;
    color: #fff;
    transform: scale(1.1);
}

.no-abilities-hint {
    font-size: 13px;
    color: #94a3b8;
    font-style: italic;
    margin: 0;
    padding: 12px;
    text-align: center;
    background: #f8fafc;
    border-radius: 8px;
    border: 2px dashed #e2e8f0;
}

.custom-group-input {
    margin-top: 4px;
}

/* 颜色选择器 */
.color-picker-section {
    margin-top: 12px;
}

.color-picker-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 8px;
}

.color-input-native {
    width: 40px;
    height: 36px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    padding: 2px;
    background: #fff;
    transition: border-color 0.2s ease;
}

.color-input-native:hover {
    border-color: #6366f1;
}

.color-preview-dot {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid rgba(15, 23, 42, 0.12);
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.12);
}

.color-hex-text {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    font-family: monospace;
}

.preset-colors {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.preset-color-btn {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    border: 3px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.1);
}

.preset-color-btn:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
}

.preset-color-btn.selected {
    border-color: #1e293b;
    transform: scale(1.2);
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.3);
}

.image-preview {
    margin-top: 8px;
    display: flex;
    justify-content: center;
    background: #f8fafc;
    border-radius: 12px;
    padding: 12px;
    border: 2px dashed #e2e8f0;
}

.preview-img {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    object-fit: cover;
    border: 2px solid rgba(99, 102, 241, 0.15);
    background: #f1f5f9;
}

.attr-select-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;
}

.attr-select-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 8px 4px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 700;
    border: 2px solid #e2e8f0;
    background: #fff;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s ease;
}

.attr-select-btn:hover {
    border-color: #6366f1;
    color: #6366f1;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.12);
}

.attr-select-btn.selected {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #fff;
    border-color: transparent;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}

.attr-select-icon {
    width: 24px;
    height: 24px;
    object-fit: contain;
}

/* ======== 弹窗底部 ======== */
.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 28px 20px;
    border-top: 1px solid #e2e8f0;
}

.btn-cancel {
    padding: 10px 24px;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    color: #475569;
    background: #fff;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-cancel:hover {
    border-color: #94a3b8;
    background: #f1f5f9;
    transform: translateY(-1px);
}

.btn-save {
    display: flex;
    align-items: center;
    gap: 8px;
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

.btn-save:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(99, 102, 241, 0.45);
}

.btn-save:active:not(:disabled) {
    transform: translateY(0) scale(0.98);
}

.btn-save:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-danger {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3);
}

.btn-danger:hover:not(:disabled) {
    box-shadow: 0 8px 22px rgba(239, 68, 68, 0.45);
}

.btn-spinner {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}

@media (max-width: 768px) {
    .page-header {
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
    }

    .filter-bar {
        flex-direction: column;
        align-items: stretch;
    }

    .filter-attributes {
        flex-direction: column;
        align-items: flex-start;
    }

    .attr-select-grid {
        grid-template-columns: repeat(4, 1fr);
    }

    .pet-table {
        font-size: 13px;
    }

    .col-group,
    .col-price,
    .col-status {
        display: none;
    }

    .modal-card {
        max-width: 95vw;
        margin: 0 8px;
    }

    .modal-body {
        padding: 20px 16px;
    }

    .modal-footer {
        padding: 12px 16px 16px;
    }
}

/* Toast 提示 */
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
</style>