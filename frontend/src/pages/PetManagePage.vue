<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPets, getGroups, createPet, updatePet, deletePet, togglePetActive, batchActivatePets, batchDeactivatePets, renameGroup } from '@/api'
import type { Pet } from '@/types'
import { getGroupColor as getGroupColorUtil, saveGroupColor, initGroupColors } from '@/utils/groupColors'
import { getAttributeIconPath } from '@/utils/attributeIcons'

const route = useRoute()
const router = useRouter()

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

// 内联编辑价格相关
const editingPricePetId = ref<number | null>(null)
const editingPriceValue = ref('')

// ═════════════════════════════════════════════════
//  拖拽排序 — 参照 animejs Draggable + Spring 物理
//  生命周期: onGrab → onDrag → onRelease → onSettle
// ═════════════════════════════════════════════════
const drag = {
    active: false,
    petId: 0,
    fromIndex: -1,
    targetIndex: -1,
    startY: 0,
    lastY: 0,
    velocity: 0,
    rowHeight: 0,
    tableRect: null as DOMRect | null,
    clone: null as HTMLElement | null,
    sourceRow: null as HTMLElement | null,
    gapRows: [] as HTMLElement[],
    settleTimer: 0 as any
}

const GAP_HEIGHT = 4
const SPRING_EASE = 'cubic-bezier(0.34, 1.56, 0.64, 1)'
const SETTLE_DURATION = 350
const CLONE_SCALE = 1.03
const GHOST_OPACITY = '0.3'

function initDragHandles() {
    nextTick(() => {
        document.querySelectorAll('.drag-handle').forEach(el => {
            const fresh = el.cloneNode(true) as HTMLElement
            el.parentNode?.replaceChild(fresh, el)
            fresh.addEventListener('pointerdown', onGrab as any)
        })
    })
}

// ── 阶段1: onGrab ──
function onGrab(e: PointerEvent) {
    const row = (e.target as HTMLElement).closest('tr.pet-row') as HTMLElement
    if (!row) return
    const pid = Number(row.getAttribute('data-pet-id'))
    const idx = filteredPets.value.findIndex(p => p.id === pid)
    if (idx < 0 || !pid) return

    e.preventDefault()
    ;(e.target as HTMLElement).setPointerCapture(e.pointerId)

    const rect = row.getBoundingClientRect()

    drag.active = true
    drag.petId = pid
    drag.fromIndex = idx
    drag.targetIndex = idx
    drag.startY = e.clientY
    drag.lastY = e.clientY
    drag.velocity = 0
    drag.rowHeight = rect.height
    drag.tableRect = row.closest('.table-wrapper')!.getBoundingClientRect()
    drag.sourceRow = row
    drag.gapRows = []

    // 源行变半透明（ghost）
    row.style.transition = 'opacity 0.15s'
    row.style.opacity = GHOST_OPACITY

    // 创建浮动克隆
    const clone = row.cloneNode(true) as HTMLElement
    clone.style.cssText = `
        position:fixed;z-index:9999;pointer-events:none;
        left:${rect.left}px;top:${rect.top}px;width:${rect.width}px;
        box-shadow:0 12px 40px rgba(0,0,0,0.28),0 0 0 2px rgba(99,102,241,0.3);
        transform:scale(${CLONE_SCALE});border-radius:12px;
        transition:box-shadow 0.2s;
    `
    document.body.appendChild(clone)
    drag.clone = clone

    document.addEventListener('pointermove', onDrag)
    document.addEventListener('pointerup', onRelease)
    document.addEventListener('pointercancel', onRelease)
}

// ── 阶段2: onDrag ──
function onDrag(e: PointerEvent) {
    if (!drag.active || !drag.clone) return

    drag.velocity = e.clientY - drag.lastY
    drag.lastY = e.clientY
    const dy = e.clientY - drag.startY

    drag.clone.style.transition = 'none'
    drag.clone.style.transform = `translateY(${dy}px) scale(${CLONE_SCALE})`
    drag.clone.style.boxShadow = `0 16px 48px rgba(0,0,0,0.35),0 0 0 3px rgba(99,102,241,0.4)`

    const rows = document.querySelectorAll('tr.pet-row') as NodeListOf<HTMLElement>
    let newTarget = drag.fromIndex
    for (let i = 0; i < rows.length; i++) {
        if (i === drag.fromIndex) continue
        const r = rows[i].getBoundingClientRect()
        const mid = r.top + r.height / 2
        if (e.clientY < mid) {
            newTarget = i
            break
        }
        newTarget = i
    }

    if (newTarget !== drag.targetIndex) {
        drag.targetIndex = newTarget
        updateGaps(rows)
    }
}

// 为被跨越的行添加 transform 偏移以产生"让位"动画
function updateGaps(rows: NodeListOf<HTMLElement>) {
    // 清除旧偏移
    drag.gapRows.forEach(r => {
        r.style.transition = 'transform 0.2s cubic-bezier(0.2,0,0,1)'
        r.style.transform = ''
    })
    drag.gapRows = []

    const from = drag.fromIndex
    const to = drag.targetIndex
    if (from === to) return

    const dist = drag.rowHeight + GAP_HEIGHT * 2

    if (to < from) {
        // 向上拖：from之前、to及之后的行向下偏移
        for (let i = to; i < from; i++) {
            const r = rows[i] as HTMLElement
            if (r === drag.sourceRow) continue
            r.style.transition = 'transform 0.2s cubic-bezier(0.2,0,0,1)'
            r.style.transform = `translateY(${dist}px)`
            drag.gapRows.push(r)
        }
    } else {
        // 向下拖：from之后、to及之前的行向上偏移
        for (let i = from + 1; i <= to; i++) {
            const r = rows[i] as HTMLElement
            r.style.transition = 'transform 0.2s cubic-bezier(0.2,0,0,1)'
            r.style.transform = `translateY(-${dist}px)`
            drag.gapRows.push(r)
        }
    }
}

// ── 阶段3: onRelease → onSettle ──
function onRelease() {
    if (!drag.active) return
    drag.active = false

    document.removeEventListener('pointermove', onDrag)
    document.removeEventListener('pointerup', onRelease)
    document.removeEventListener('pointercancel', onRelease)

    clearTimeout(drag.settleTimer)

    // 清除所有 gap 动画，让行回到原位
    drag.gapRows.forEach(r => {
        r.style.transition = 'transform 0.15s cubic-bezier(0.2,0,0,1)'
        r.style.transform = ''
    })

    if (drag.clone) {
        const clone = drag.clone

        // Spring-settle 动画：克隆滑入目标位置
        clone.style.transition = `transform ${SETTLE_DURATION}ms ${SPRING_EASE}, opacity 0.2s`
        clone.style.transform = `translateY(0) scale(${CLONE_SCALE})`
        clone.style.boxShadow = '0 8px 24px rgba(99,102,241,0.3),0 0 0 2px rgba(99,102,241,0.15)'

        const settled = () => {
            clone.removeEventListener('transitionend', settled)
            if (clone.parentNode) clone.remove()
            drag.clone = null
            finishReorder()
        }
        clone.addEventListener('transitionend', settled)
        // fallback
        drag.settleTimer = setTimeout(settled, SETTLE_DURATION + 80)
    } else {
        finishReorder()
    }
}

// ── 阶段4: 数据重排 + 保存 ──
function finishReorder() {
    const srcRow = drag.sourceRow
    if (srcRow) {
        srcRow.style.opacity = ''
        srcRow.style.transition = 'opacity 0.3s'
        drag.sourceRow = null
    }

    drag.gapRows.forEach(r => {
        r.style.transform = ''
        r.style.transition = ''
    })
    drag.gapRows = []

    if (drag.targetIndex === drag.fromIndex) {
        resetDragState()
        return
    }

    const reordered = [...filteredPets.value]
    const [moved] = reordered.splice(drag.fromIndex, 1)
    reordered.splice(drag.targetIndex, 0, moved)

    const reorderedSet = new Set(reordered.map(p => p.id))
    const newPets: Pet[] = []
    let ri = 0
    for (const p of pets.value) {
        if (reorderedSet.has(p.id)) {
            newPets.push({ ...reordered[ri] })
            ri++
        } else {
            newPets.push({ ...p })
        }
    }
    newPets.forEach((p, idx) => { p.sort_order = idx })
    pets.value = newPets

    resetDragState()
    saveSortOrder(newPets)
}

function resetDragState() {
    drag.fromIndex = -1
    drag.targetIndex = -1
    drag.petId = 0
    drag.clone = null
    drag.sourceRow = null
}

async function saveSortOrder(newPets: Pet[]) {
    const body = '{"items":[' + newPets.map((p, i) => '{"id":' + p.id + ',"sort_order":' + i + '}').join(',') + ']}'

    try {
        const res = await fetch('http://localhost:8004/api/pets/sort-order', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body
        })
        if (res.ok) {
            showToast('排序已保存', 'success')
        } else {
            const errText = await res.text()
            console.error('[拖拽] 422响应体:', errText)
            console.error('[拖拽] 请求体前200字:', body.slice(0, 200))
            throw new Error('status ' + res.status + ': ' + errText)
        }
    } catch (err) {
        console.error('[拖拽] 保存失败:', err)
        showToast('排序保存失败', 'error')
        await loadPets()
    }
}

// 分组改名相关
const editingGroupName = ref<string | null>(null)
const editingGroupNewName = ref('')

// 草稿箱筛选
const showDraftOnly = ref(false)

const sortBy = ref('sort_order')
const sortOrder = ref<'asc' | 'desc'>('asc')
const defaultSortActive = ref(true)

function applyDefaultSort() {
    sortBy.value = 'sort_order'
    sortOrder.value = 'asc'
    defaultSortActive.value = true
}

function toggleSortBy(field: string) {
    if (sortBy.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
        sortBy.value = field
        sortOrder.value = 'asc'
    }
    defaultSortActive.value = sortBy.value === 'sort_order' && sortOrder.value === 'asc'
}

// 监听路由查询参数，支持侧边栏草稿箱导航
watch(() => route.query.draft, (val) => {
    showDraftOnly.value = val === '1'
}, { immediate: true })

let searchTimer: number | null = null
const debouncedSearch = ref('')

function handleSearchInput(e: Event) {
    const target = e.target as HTMLInputElement
    searchKeyword.value = target.value
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
    if (showDraftOnly.value) {
        result = result.filter(p => p.group === '草稿' && !p.is_active)
    } else {
        result = result.filter(p => !(p.group === '草稿' && !p.is_active))
    }
    result.sort((a, b) => {
        let va: number, vb: number
        if (sortBy.value === 'price') {
            va = a.price
            vb = b.price
        } else if (sortBy.value === 'sort_order') {
            va = a.sort_order
            vb = b.sort_order
        } else {
            va = a.id
            vb = b.id
        }
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
    formTitle.value = showDraftOnly.value ? '新建草稿' : '添加精灵'
    Object.assign(formData, emptyForm())
    if (showDraftOnly.value) {
        formData.group = ''
        formData.is_custom_group = false
        formData.is_active = false
    }
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

function completeDraft(pet: Pet) {
    editingPetId.value = pet.id
    formTitle.value = '完成精灵'
    formData.name = pet.name
    formData.image_url = pet.image_url
    formData.price = pet.price || 0
    formData.attributes = pet.attributes ? [...pet.attributes] : []
    formData.description = pet.description || ''
    formData.abilities = pet.abilities ? [...pet.abilities] : []
    formData.is_active = true
    formData.is_custom_group = false
    formData.custom_group = ''
    formData.group = pet.group !== '草稿' ? pet.group : ''
    formData.custom_group_color = '#6366F1'
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
            await updatePet(editingPetId.value, payload as any)
            showToast('精灵更新成功', 'success')
        } else {
            await createPet({ ...payload, sort_order: 0 } as any)
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

async function handleSaveDraft() {
    if (!formData.name.trim()) return

    formSubmitting.value = true
    const draftGroup = '草稿'
    try {
        if (editingPetId.value) {
            const payload: Record<string, unknown> = {
                name: formData.name.trim(),
                group: draftGroup,
                is_active: false,
                image_url: formData.image_url.trim() || ''
            }
            if (formData.price !== undefined) payload.price = formData.price
            if (formData.attributes.length) payload.attributes = formData.attributes
            if (formData.description.trim()) payload.description = formData.description.trim()
            const abilities = formData.abilities.filter(a => a.trim())
            if (abilities.length) payload.abilities = abilities

            await updatePet(editingPetId.value, payload as Partial<Pet>)
            showToast('精灵已存为草稿', 'success')
        } else {
            const payload = {
                name: formData.name.trim(),
                group: draftGroup,
                image_url: formData.image_url.trim() || '',
                price: formData.price || 0,
                attributes: formData.attributes,
                description: formData.description.trim() || '',
                abilities: formData.abilities.filter(a => a.trim()),
                is_active: false
            }
            await createPet(payload as Parameters<typeof createPet>[0])
            showToast('精灵草稿已保存', 'success')
        }
        if (formData.is_custom_group && effectiveGroup.value) {
            saveGroupColor(effectiveGroup.value, formData.custom_group_color)
        }
        closeFormModal()
        await loadPets()
        await loadGroups()
    } catch (err) {
        showToast('保存草稿失败', 'error')
        console.error('保存草稿失败:', err)
    } finally {
        formSubmitting.value = false
    }
}

function confirmDelete(pet: Pet) {
    deletingPet.value = pet
    showDeleteConfirm.value = true
}

// 内联编辑价格 - 开始编辑
function startEditPrice(pet: Pet) {
    editingPricePetId.value = pet.id
    editingPriceValue.value = String(pet.price)
}

// 内联编辑价格 - 保存
async function saveEditPrice(pet: Pet) {
    const value = editingPriceValue.value
    
    // 如果值为空或没有修改，直接退出
    if (value === '' || value === null || value === undefined) {
        editingPricePetId.value = null
        editingPriceValue.value = ''
        return
    }
    
    // 解析价格
    let newPrice: number
    if (typeof value === 'number') {
        newPrice = value
    } else {
        // 先尝试直接转换，再parseInt
        const numValue = Number(value)
        newPrice = isNaN(numValue) ? parseInt(value, 10) : numValue
    }
    
    // 验证价格有效性
    if (isNaN(newPrice) || newPrice < 0 || !isFinite(newPrice)) {
        editingPricePetId.value = null
        editingPriceValue.value = ''
        return
    }
    
    try {
        await updatePet(pet.id, { price: newPrice })
        pet.price = newPrice
        showToast('价格更新成功', 'success')
    } catch (err) {
        showToast('价格更新失败', 'error')
        console.error('更新价格失败:', err)
    } finally {
        editingPricePetId.value = null
        editingPriceValue.value = ''
    }
}

// 内联编辑价格 - 取消编辑
function cancelEditPrice() {
    editingPricePetId.value = null
    editingPriceValue.value = ''
}

// 内联编辑价格 - 按回车键保存
function handlePriceKeydown(pet: Pet, event: KeyboardEvent) {
    if (event.key === 'Enter') {
        saveEditPrice(pet)
    } else if (event.key === 'Escape') {
        cancelEditPrice()
    }
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

async function moveToDraft(pet: Pet) {
    try {
        await updatePet(pet.id, { is_active: false, group: '草稿' } as any)
        showToast('已移至草稿箱', 'success')
        await loadPets()
        await loadGroups()
    } catch (err) {
        showToast('移至草稿箱失败', 'error')
        console.error('移至草稿箱失败:', err)
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

function startRenameGroup(group: string) {
    editingGroupName.value = group
    editingGroupNewName.value = group
}

function cancelRenameGroup() {
    editingGroupName.value = null
    editingGroupNewName.value = ''
}

async function submitRenameGroup(oldName: string) {
    const newName = editingGroupNewName.value.trim()
    if (!newName || newName === oldName) {
        editingGroupName.value = null
        return
    }
    try {
        await renameGroup(oldName, newName)
        showToast(`分组已重命名为 "${newName}"`, 'success')
        editingGroupName.value = null
        await loadPets()
        await loadGroups()
    } catch (err: any) {
        const msg = err?.response?.data?.detail || '重命名失败'
        showToast(msg, 'error')
    }
}

function handleRenameKeydown(oldName: string, event: KeyboardEvent) {
    if (event.key === 'Enter') {
        submitRenameGroup(oldName)
    } else if (event.key === 'Escape') {
        cancelRenameGroup()
    }
}

watch(debouncedSearch, () => {}, { flush: 'post' })
watch(filteredPets, () => { initDragHandles() }, { flush: 'post' })

onMounted(async () => {
    await initGroupColors()
    loadPets()
    loadGroups()
    initDragHandles()
})
</script>

<template>
    <div class="pet-manage-page" :class="{ 'draft-mode': showDraftOnly }">
        <!-- Toast 提示 -->
        <div v-if="toastMsg" class="toast" :class="toastType">{{ toastMsg }}</div>

        <div class="page-header">
            <h2 class="page-title">
                {{ showDraftOnly ? '草稿箱' : '精灵管理' }}
            </h2>
            <p v-if="showDraftOnly" class="page-subtitle">管理尚未完善的精灵草稿</p>
            <div class="header-actions" v-if="!showDraftOnly">
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
            <div class="header-actions" v-else>
                <button class="btn-back-pets" @click="router.push({ path: '/admin/pets' })">
                    ← 精灵管理
                </button>
                <button class="btn-add btn-draft-add" @click="openAddModal">
                    <span class="btn-add-icon">+</span>
                    新建草稿
                </button>
                <span class="draft-count-badge">
                    📋 共 {{ filteredPets.length }} 只草稿
                </span>
            </div>
        </div>

        <div class="filter-bar" :class="{ 'filter-bar-draft': showDraftOnly }">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input
                    type="text"
                    :value="searchKeyword"
                    @input="handleSearchInput"
                    :placeholder="showDraftOnly ? '搜索草稿名称...' : '搜索精灵名称...'"
                    class="search-input"
                />
            </div>

            <div class="filter-group" v-if="!showDraftOnly">
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

            <div class="filter-attributes" v-if="!showDraftOnly">
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

            <div class="sort-buttons">
                <button
                    class="btn-sort"
                    :class="{ active: defaultSortActive }"
                    @click="applyDefaultSort"
                    title="按默认顺序排列"
                >
                    📋 默认排序
                </button>
                <button
                    class="btn-sort"
                    :class="{ active: sortBy === 'id' }"
                    @click="toggleSortBy('id')"
                    :title="'按ID' + (sortBy === 'id' ? (sortOrder === 'asc' ? '升序' : '降序') : '排序')"
                >
                    🔢 ID{{ sortBy === 'id' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
                </button>
                <button
                    class="btn-sort"
                    :class="{ active: sortBy === 'price' }"
                    @click="toggleSortBy('price')"
                    :title="'按价格' + (sortBy === 'price' ? (sortOrder === 'asc' ? '升序' : '降序') : '排序')"
                >
                    💰 价格{{ sortBy === 'price' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
                </button>
            </div>
        </div>

        <div class="group-color-manager" v-if="!showDraftOnly">
            <h3 class="section-title-text">📂 分组管理</h3>
            <div class="color-cards-grid">
                <div v-for="group in groups" :key="group" class="color-card">
                    <div class="color-card-header">
                        <span
                            class="color-preview"
                            :style="{ background: getGroupColor(group) }"
                        ></span>
                        <span
                            v-if="editingGroupName !== group"
                            class="group-name group-name-editable"
                            @dblclick="startRenameGroup(group)"
                            :title="'双击改名'"
                        >{{ group }}</span>
                        <input
                            v-else
                            v-model="editingGroupNewName"
                            type="text"
                            class="group-rename-input"
                            @keydown="handleRenameKeydown(group, $event)"
                            @blur="submitRenameGroup(group)"
                            ref="groupRenameInput"
                        />
                        <button
                            v-if="editingGroupName !== group"
                            class="btn-rename-group"
                            @click="startRenameGroup(group)"
                            title="重命名分组"
                        >✏️</button>
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
                        <th class="col-drag-handle"></th>
                        <th class="col-row-num">#</th>
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
                        <td colspan="9" class="empty-row">暂无匹配的精灵数据</td>
                    </tr>
                    <tr
                        v-for="(pet, petIdx) in filteredPets"
                        :key="pet.id"
                        class="pet-row"
                        :data-pet-id="pet.id"
                    >
                        <td class="col-drag-handle">
                            <span class="drag-handle" title="拖拽排序" style="cursor:grab;user-select:none">⠿</span>
                        </td>
                        <td class="col-row-num">{{ petIdx + 1 }}</td>
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
                            <div class="price-cell">
                                <input
                                    v-if="editingPricePetId === pet.id"
                                    v-model="editingPriceValue"
                                    type="number"
                                    min="0"
                                    class="price-input"
                                    @keydown="handlePriceKeydown(pet, $event)"
                                    @blur="saveEditPrice(pet)"
                                    ref="priceInput"
                                />
                                <span
                                    v-else
                                    class="price-tag editable"
                                    @click="startEditPrice(pet)"
                                >
                                    {{ pet.price }}
                                </span>
                            </div>
                        </td>
                        <td class="col-status">
                            <span class="status-tag" :class="pet.is_active ? 'status-active' : (pet.group === '草稿' && !pet.is_active ? 'status-draft' : 'status-inactive')">
                                {{ pet.is_active ? '已上架' : (pet.group === '草稿' && !pet.is_active ? '草稿' : '已下架') }}
                            </span>
                        </td>
                        <td class="col-actions">
                            <div class="action-buttons">
                                <button v-if="pet.group === '草稿' && !pet.is_active && !showDraftOnly" class="btn-action btn-complete" title="完善信息后上架" @click="openEditModal(pet)">
                                    ✍️
                                </button>
                                <button v-if="pet.group === '草稿' && !pet.is_active && showDraftOnly" class="btn-action btn-finish" title="完成精灵编辑" @click="completeDraft(pet)">
                                    补
                                </button>
                                <button v-if="!(pet.group === '草稿' && !pet.is_active)" class="btn-action btn-edit" title="编辑" @click="openEditModal(pet)">
                                    ✏️
                                </button>
                                <button
                                    v-if="!(pet.group === '草稿' && !pet.is_active)"
                                    class="btn-action"
                                    :class="pet.is_active ? 'btn-offline' : 'btn-online'"
                                    :title="pet.is_active ? '下架' : '上架'"
                                    @click="handleToggleActive(pet)"
                                >
                                    {{ pet.is_active ? '📥' : '📤' }}
                                </button>
                                <button
                                    v-if="!(pet.group === '草稿' && !pet.is_active) && !showDraftOnly"
                                    class="btn-action btn-draft-move"
                                    title="存草稿"
                                    @click="moveToDraft(pet)"
                                >
                                    📋
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
        <div v-if="showFormModal" class="modal-overlay">
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
                        class="btn-draft"
                        :disabled="formSubmitting || !formData.name.trim()"
                        @click="handleSaveDraft"
                    >
                        <span v-if="formSubmitting" class="btn-spinner"></span>
                        {{ formSubmitting ? '保存中...' : '存草稿' }}
                    </button>
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
        <div v-if="showDeleteConfirm" class="modal-overlay">
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
    min-height: 100%;
}

.pet-manage-page::before {
    content: '';
    position: fixed;
    top: 0;
    left: 220px;
    right: 0;
    bottom: 0;
    background: url('/images/bg/阿布星星蓝色.png') center center / cover no-repeat;
    z-index: -2;
}

.pet-manage-page::after {
    content: '';
    position: fixed;
    top: 0;
    left: 220px;
    right: 0;
    bottom: 0;
    background: rgba(241, 245, 249, 0.5);
    z-index: -1;
}

.pet-manage-page.draft-mode::before {
    background: url('/images/bg/菊花梨五角星黄色.png') center center / cover no-repeat;
}

.pet-manage-page.draft-mode::after {
    background: rgba(241, 245, 249, 0.5);
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
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.55) 0%, rgba(248, 250, 252, 0.5) 100%);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    border: 2px solid rgba(99, 102, 241, 0.12);
    backdrop-filter: blur(6px);
}

/* ======== 分组颜色管理器 ======== */
.group-color-manager {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.55) 0%, rgba(248, 250, 252, 0.5) 100%);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    border: 2px solid rgba(99, 102, 241, 0.12);
    backdrop-filter: blur(6px);
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

.group-name-editable {
    cursor: pointer;
    border-bottom: 1px dashed transparent;
    transition: all 0.2s ease;
    padding: 2px 4px;
    border-radius: 4px;
}

.group-name-editable:hover {
    border-bottom-color: #6366f1;
    background: rgba(99, 102, 241, 0.06);
}

.group-rename-input {
    font-size: 13px;
    font-weight: 700;
    color: #1e293b;
    border: 2px solid #6366f1;
    border-radius: 6px;
    padding: 4px 8px;
    outline: none;
    background: #fff;
    width: 100%;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.btn-rename-group {
    width: 24px;
    height: 24px;
    padding: 0;
    border: none;
    border-radius: 4px;
    background: transparent;
    color: #94a3b8;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.btn-rename-group:hover {
    background: rgba(99, 102, 241, 0.1);
    color: #6366f1;
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

.btn-draft-box {
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

.btn-draft-box:hover {
    border-color: #f59e0b;
    color: #d97706;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
}

.btn-draft-box.active {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: #fff;
    border-color: transparent;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
}

/* ======== 排序按钮 ======== */
.btn-sort {
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

.btn-sort:hover {
    border-color: #6366f1;
    color: #6366f1;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.btn-sort:active {
    transform: translateY(-2px) scale(0.97);
}

.btn-sort.active {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #fff;
    border-color: transparent;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}

.sort-buttons {
    display: flex;
    align-items: center;
    gap: 8px;
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
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.55) 0%, rgba(248, 250, 252, 0.5) 100%);
    border-radius: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    border: 2px solid rgba(99, 102, 241, 0.12);
    backdrop-filter: blur(6px);
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
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.55) 0%, rgba(248, 250, 252, 0.5) 100%);
    border-radius: 20px;
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5);
    border: 2px solid rgba(99, 102, 241, 0.12);
    overflow: hidden;
    backdrop-filter: blur(6px);
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

.col-drag-handle { width: 36px; }
.col-row-num { width: 40px; text-align: center; font-weight: 700; color: #94a3b8; font-size: 13px; }
.col-thumb { width: 72px; }
.col-name { min-width: 120px; }
.col-group { min-width: 100px; }
.col-attr { min-width: 140px; }
.col-price { width: 90px; }
.col-status { width: 96px; }
.col-actions { width: 140px; }

.pet-table tbody tr {
    transition: background 0.2s ease, transform 0.2s cubic-bezier(0.2,0,0,1), opacity 0.2s;
    border-bottom: 1px solid rgba(226, 232, 240, 0.6);
    will-change: transform;
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

.pet-row {
    transition: all 0.2s ease;
    cursor: default;
}

.drag-handle {
    display: inline-block;
    cursor: grab;
    font-size: 18px;
    color: #94a3b8;
    padding: 4px;
    transition: color 0.2s;
    user-select: none;
    line-height: 1;
}

.drag-handle:active {
    cursor: grabbing;
}

.pet-row:hover .drag-handle {
    color: #6366f1;
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
    transition: all 0.25s ease;
}

.price-tag.editable {
    cursor: pointer;
}

.price-tag.editable:hover {
    transform: scale(1.08);
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.45);
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
}

.price-cell {
    display: flex;
    align-items: center;
    justify-content: center;
}

.price-input {
    width: 70px;
    padding: 6px 12px;
    border-radius: 8px;
    border: 2px solid #6366f1;
    font-size: 14px;
    font-weight: 700;
    text-align: center;
    background: #fff;
    color: #1e293b;
    outline: none;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    transition: all 0.2s ease;
}

.price-input:focus {
    border-color: #8b5cf6;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.25);
}

.price-input::-webkit-outer-spin-button,
.price-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

.price-input[type=number] {
    -moz-appearance: textfield;
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

.status-draft {
    background: rgba(245, 158, 11, 0.12);
    color: #d97706;
    border: 1px solid rgba(245, 158, 11, 0.3);
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

.btn-complete:hover {
    background: rgba(245, 158, 11, 0.12);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
}

.btn-finish {
    width: auto !important;
    padding: 4px 16px !important;
    font-size: 14px;
    font-weight: 800;
    color: #fff;
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    border-radius: 8px;
    white-space: nowrap;
    gap: 4px;
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.btn-finish:hover {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
    box-shadow: 0 6px 18px rgba(245, 158, 11, 0.45) !important;
    transform: translateY(-2px) scale(1.05) !important;
}

.btn-draft-move:hover {
    background: rgba(245, 158, 11, 0.12) !important;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25) !important;
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

.btn-draft {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 28px;
    border: 2px solid #f59e0b;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    color: #d97706;
    background: #fffbeb;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-draft:hover:not(:disabled) {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: #fff;
    border-color: transparent;
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(245, 158, 11, 0.4);
}

.btn-draft:active:not(:disabled) {
    transform: translateY(0) scale(0.98);
}

.btn-draft:disabled {
    opacity: 0.5;
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

/* ======== 草稿箱模式样式 ======== */
.pet-manage-page.draft-mode .page-header {
    padding-bottom: 16px;
    border-bottom: 2px solid rgba(245, 158, 11, 0.15);
    margin-bottom: 20px;
}

.draft-mode .page-title {
    color: #000000;
    -webkit-text-fill-color: #000000;
}

.page-subtitle {
    font-size: 14px;
    color: #92400e;
    margin: 4px 0 0 0;
    font-weight: 500;
    opacity: 0.7;
}

.btn-draft-add {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.35) !important;
}

.btn-draft-add:hover {
    box-shadow: 0 10px 28px rgba(245, 158, 11, 0.5) !important;
}

.draft-count-badge {
    display: inline-flex;
    align-items: center;
    padding: 8px 18px;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(217, 119, 6, 0.08) 100%);
    border: 2px solid rgba(245, 158, 11, 0.25);
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    color: #92400e;
    white-space: nowrap;
}

.filter-bar-draft {
    border-color: rgba(245, 158, 11, 0.2) !important;
    background: linear-gradient(145deg, rgba(255, 251, 235, 0.98) 0%, rgba(254, 243, 199, 0.94) 100%) !important;
}

.btn-back-pets {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 10px 18px;
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

.btn-back-pets:hover {
    border-color: #6366f1;
    color: #6366f1;
    transform: translateX(-3px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.draft-mode .table-wrapper {
    border-color: rgba(245, 158, 11, 0.2) !important;
    background: linear-gradient(145deg, rgba(255, 251, 235, 0.98) 0%, rgba(254, 243, 199, 0.94) 100%) !important;
}

.draft-mode .pet-table thead {
    background: linear-gradient(135deg, #78350f 0%, #92400e 50%, #78350f 100%) !important;
    border-bottom-color: rgba(245, 158, 11, 0.4) !important;
}

.draft-mode .pet-table th {
    color: #fcd34d !important;
}

.draft-mode .pet-table tbody tr:hover {
    background: rgba(245, 158, 11, 0.06) !important;
}

.draft-mode .drag-handle:hover,
.draft-mode .pet-row:hover .drag-handle {
    color: #d97706 !important;
}

.draft-mode .btn-sort.active {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.4) !important;
}

.draft-mode .btn-sort:hover {
    border-color: #f59e0b !important;
    color: #d97706 !important;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15) !important;
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