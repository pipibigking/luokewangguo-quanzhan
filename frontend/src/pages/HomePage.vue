<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getPets, getGroups } from '@/api'
import type { Pet, FilterOptions } from '@/types'
import { initGroupColors } from '@/utils/groupColors'
import PetCard from '@/components/PetCard.vue'
import PetModal from '@/components/PetModal.vue'
import FilterBar from '@/components/FilterBar.vue'
import AnnouncementBar from '@/components/AnnouncementBar.vue'

const router = useRouter()

const pets = ref<Pet[]>([])
const groups = ref<string[]>([])
const loading = ref(true)
const error = ref('')
const selectedPet = ref<Pet | null>(null)
const showModal = ref(false)
const canvasBgRef = ref<HTMLCanvasElement | null>(null)
const canvasSnowRef = ref<HTMLCanvasElement | null>(null)
const titleRef = ref<HTMLElement | null>(null)
const titleIconSrc = '/images/balls/棱镜球.png'

/* ======== 背景粒子连线网络 ======== */
interface NetParticle {
  x: number; y: number; vx: number; vy: number; r: number
}

let bgAnimId = 0
let bgCtx: CanvasRenderingContext2D | null = null
let bgW = 0; let bgH = 0
let netParticles: NetParticle[] = []
let mouseX = -999; let mouseY = -999

function initBgCanvas() {
  const canvas = canvasBgRef.value
  if (!canvas) return
  bgCtx = canvas.getContext('2d')
  bgW = window.innerWidth
  bgH = window.innerHeight
  canvas.width = bgW
  canvas.height = bgH
  const count = Math.floor((bgW * bgH) / 15000)
  netParticles = Array.from({ length: count }, () => ({
    x: Math.random() * bgW,
    y: Math.random() * bgH,
    vx: (Math.random() - 0.5) * 0.5,
    vy: (Math.random() - 0.5) * 0.5,
    r: Math.random() * 2.2 + 1
  }))
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('resize', resizeBg)
  animateBg()
}

function resizeBg() {
  const canvas = canvasBgRef.value
  if (!canvas) return
  bgW = window.innerWidth
  bgH = window.innerHeight
  canvas.width = bgW
  canvas.height = bgH
}

function onMouseMove(e: MouseEvent) {
  mouseX = e.clientX
  mouseY = e.clientY
}

function animateBg() {
  if (!bgCtx) return
  const ctx = bgCtx
  ctx.clearRect(0, 0, bgW, bgH)

  for (const p of netParticles) {
    p.x += p.vx
    p.y += p.vy
    if (p.x < 0 || p.x > bgW) p.vx *= -1
    if (p.y < 0 || p.y > bgH) p.vy *= -1

    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(147, 197, 253, 0.6)'
    ctx.fill()
  }

  for (let i = 0; i < netParticles.length; i++) {
    for (let j = i + 1; j < netParticles.length; j++) {
      const dx = netParticles[i].x - netParticles[j].x
      const dy = netParticles[i].y - netParticles[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 120) {
        ctx.beginPath()
        ctx.moveTo(netParticles[i].x, netParticles[i].y)
        ctx.lineTo(netParticles[j].x, netParticles[j].y)
        ctx.strokeStyle = `rgba(147, 197, 253, ${0.22 * (1 - dist / 120)})`
        ctx.lineWidth = 0.6
        ctx.stroke()
      }
    }

    const mdx = netParticles[i].x - mouseX
    const mdy = netParticles[i].y - mouseY
    const mDist = Math.sqrt(mdx * mdx + mdy * mdy)
    if (mDist < 180) {
      ctx.beginPath()
      ctx.moveTo(netParticles[i].x, netParticles[i].y)
      ctx.lineTo(mouseX, mouseY)
      ctx.strokeStyle = `rgba(96, 165, 250, ${0.35 * (1 - mDist / 180)})`
      ctx.lineWidth = 0.8
      ctx.stroke()
    }
  }

  bgAnimId = requestAnimationFrame(animateBg)
}

function destroyBg() {
  if (bgAnimId) { cancelAnimationFrame(bgAnimId); bgAnimId = 0 }
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('resize', resizeBg)
  netParticles = []; bgCtx = null
}

/* ======== Header 多元素粒子雪花特效 ======== */
interface HeaderSnow {
  x: number; y: number; size: number; speed: number; wind: number
  opacity: number; swing: number; swingT: number; rotation: number; rotSpeed: number
  imgIndex: number
}

let snowAnimId = 0
let snowCtx: CanvasRenderingContext2D | null = null
let snowW = 0; let snowH = 0
let headerSnows: HeaderSnow[] = []
const snowImgs: (HTMLImageElement | null)[] = [null, null, null]
const snowImgPaths = [
  '/images/balls/织梦棱镜球.png',
  '/images/balls/可可果球.png',
  '/images/balls/国王球.png'
]
let snowImgsLoaded = 0
let headerEl: HTMLElement | null = null

function initHeaderSnow() {
  const canvas = canvasSnowRef.value
  if (!canvas) return
  snowCtx = canvas.getContext('2d')
  headerEl = canvas.closest('.app-header') as HTMLElement
  snowImgsLoaded = 0
  snowImgs.fill(null)
  snowImgPaths.forEach((path, i) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      snowImgs[i] = img
      snowImgsLoaded++
      if (snowImgsLoaded >= snowImgPaths.length) startHeaderSnow()
    }
    img.onerror = () => {
      console.warn(`雪花素材加载失败: ${path}`)
      snowImgsLoaded++
      if (snowImgsLoaded >= snowImgPaths.length) startHeaderSnow()
    }
    img.src = path
  })
  window.addEventListener('resize', resizeHeaderSnow)
}

function startHeaderSnow() {
  resizeHeaderSnow()
  createHeaderSnows()
  animateHeaderSnow()
}

function resizeHeaderSnow() {
  const canvas = canvasSnowRef.value
  if (!canvas || !headerEl) return
  snowW = headerEl.offsetWidth
  snowH = headerEl.offsetHeight
  canvas.width = snowW
  canvas.height = snowH
  canvas.style.width = snowW + 'px'
  canvas.style.height = snowH + 'px'
}

function createHeaderSnows() {
  headerSnows = []
  const count = 28
  for (let i = 0; i < count; i++) {
    headerSnows.push({
      x: Math.random() * (snowW || window.innerWidth),
      y: Math.random() * (snowH || 360),
      size: Math.random() * 18 + 12,
      speed: Math.random() * 0.7 + 0.2,
      wind: Math.random() * 0.5 - 0.25,
      opacity: Math.random() * 0.45 + 0.5,
      swing: Math.random() * 0.5 - 0.25,
      swingT: Math.random() * Math.PI * 2,
      rotation: Math.random() * 360,
      rotSpeed: (Math.random() - 0.5) * 1.0,
      imgIndex: Math.floor(Math.random() * 3)
    })
  }
}

function animateHeaderSnow() {
  if (!snowCtx) return
  const ctx = snowCtx
  ctx.clearRect(0, 0, snowW, snowH)

  for (const s of headerSnows) {
    s.y += s.speed
    s.swingT += 0.01
    s.x += s.wind + Math.sin(s.swingT) * s.swing
    s.rotation += s.rotSpeed

    if (s.y > snowH + 30) { s.y = -30; s.x = Math.random() * snowW }
    if (s.x > snowW + 30) s.x = -30
    if (s.x < -30) s.x = snowW + 30

    ctx.save()
    ctx.globalAlpha = s.opacity
    ctx.translate(s.x, s.y)
    ctx.rotate((s.rotation * Math.PI) / 180)

    const img = snowImgs[s.imgIndex]
    if (img && img.complete && img.naturalWidth > 0) {
      ctx.drawImage(img, -s.size / 2, -s.size / 2, s.size, s.size)
    } else {
      ctx.beginPath()
      const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, s.size * 0.6)
      grad.addColorStop(0, 'rgba(147,197,253,0.95)')
      grad.addColorStop(0.3, 'rgba(96,165,250,0.7)')
      grad.addColorStop(0.6, 'rgba(59,130,246,0.3)')
      grad.addColorStop(1, 'rgba(37,99,235,0)')
      ctx.fillStyle = grad
      ctx.beginPath()
      ctx.arc(0, 0, s.size * 0.45, 0, Math.PI * 2)
      ctx.fill()
      const innerGrad = ctx.createRadialGradient(0, -s.size * 0.15, 0, 0, 0, s.size * 0.25)
      innerGrad.addColorStop(0, 'rgba(255,255,255,0.9)')
      innerGrad.addColorStop(1, 'rgba(191,219,254,0.5)')
      ctx.fillStyle = innerGrad
      ctx.beginPath()
      ctx.arc(0, -s.size * 0.1, s.size * 0.2, 0, Math.PI * 2)
      ctx.fill()
    }

    ctx.restore()
  }

  snowAnimId = requestAnimationFrame(animateHeaderSnow)
}

function destroyHeaderSnow() {
  if (snowAnimId) { cancelAnimationFrame(snowAnimId); snowAnimId = 0 }
  window.removeEventListener('resize', resizeHeaderSnow)
  headerSnows = []; snowCtx = null; snowImgs[0] = null; snowImgs[1] = null; snowImgs[2] = null; headerEl = null
}

const filterOptions = reactive<FilterOptions>({
  group: null,
  search: '',
  sortBy: 'price',
  sortOrder: 'asc',
  attribute: null
})

const titleText = '笑笑&屁屁-洛克王国世界'
const titleChars = ref<{ char: string; delay: number }[]>([])

function initializeTitleChars() {
  titleChars.value = titleText.split('').map((char, index) => ({
    char: char === ' ' ? '\u00A0' : char,
    delay: index * 0.08
  }))
}

const filteredPets = computed(() => {
  let result = [...pets.value]
  
  if (filterOptions.group) {
    result = result.filter(pet => pet.group === filterOptions.group)
  }
  
  if (filterOptions.search) {
    const searchTerm = filterOptions.search.toLowerCase()
    result = result.filter(pet => 
      pet.name.toLowerCase().includes(searchTerm)
    )
  }
  
  if (filterOptions.attribute) {
    result = result.filter(pet => 
      pet.attributes && pet.attributes.includes(filterOptions.attribute)
    )
  }
  
  if (filterOptions.sortBy === 'price') {
    result.sort((a, b) => {
      if (filterOptions.sortOrder === 'asc') {
        return a.price - b.price
      } else {
        return b.price - a.price
      }
    })
  }
  
  return result
})

async function loadPets() {
  loading.value = true
  error.value = ''
  try {
    const data = await getPets(
      filterOptions.group || undefined,
      filterOptions.search || undefined,
      filterOptions.sortBy,
      filterOptions.sortOrder,
      filterOptions.attribute || undefined,
      false
    )
    pets.value = data
  } catch (err) {
    error.value = '加载精灵数据失败，请检查后端服务是否启动'
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

function handlePetClick(pet: Pet) {
  selectedPet.value = pet
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function goToAdmin() {
  router.push('/admin')
}

watch(filterOptions, () => {
  loadPets()
}, { deep: true })

onMounted(async () => {
  initializeTitleChars()
  initBgCanvas()
  initHeaderSnow()
  await initGroupColors() // 初始化加载分组颜色
  loadGroups()
  loadPets()
})

onUnmounted(() => {
  destroyBg()
  destroyHeaderSnow()
})
</script>

<template>
  <div class="app-container">
    <!-- Canvas 粒子连线网络背景 -->
    <canvas ref="canvasBgRef" class="particle-canvas-bg"></canvas>
    
    <!-- 顶部标题 -->
    <header class="app-header">
      <!-- Header 织梦棱镜球雪花画布 -->
      <canvas ref="canvasSnowRef" class="snow-canvas"></canvas>
      <div class="header-content">
        <img class="title-icon" :src="titleIconSrc" alt="棱镜球" />
        <h1 ref="titleRef" class="header-title">
          <span 
            v-for="(item, index) in titleChars" 
            :key="index" 
            class="title-char"
            :data-char="item.char"
            :style="{ animationDelay: item.delay + 's' }"
          >
            {{ item.char }}
          </span>
        </h1>
        <p class="header-subtitle">异色精灵图鉴</p>
      </div>
      <div class="header-glow"></div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <!-- 筛选栏 -->
      <div class="filter-wrapper">
        <FilterBar
          :groups="groups"
          :filter-options="filterOptions"
          @update:filter-options="(options) => Object.assign(filterOptions, options)"
        />
      </div>

      <!-- 公告栏 -->
      <AnnouncementBar />

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container fade-in">
        <div class="loading-spinner"></div>
        <p class="loading-text">正在召唤精灵...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container fade-in">
        <p class="error-text">{{ error }}</p>
        <button @click="loadPets" class="retry-button">重新召唤</button>
      </div>

      <!-- 无数据状态 -->
      <div v-else-if="filteredPets.length === 0" class="empty-container fade-in">
        <p class="empty-text">精灵们藏起来了...</p>
        <p class="empty-hint">试试其他召唤方式吧</p>
      </div>

      <!-- 精灵卡片网格 -->
      <transition-group name="pets-list" tag="div" v-else class="pets-grid">
        <PetCard
          v-for="(pet, index) in filteredPets"
          :key="pet.id"
          :pet="pet"
          :index="index"
          @click="handlePetClick(pet)"
          class="pet-card-item"
        />
      </transition-group>
    </main>

    <!-- 页脚 -->
    <footer class="app-footer">
      <p class="footer-text">洛克王国异色精灵展示平台</p>
      <button class="admin-entry" @click="goToAdmin" title="管理后台">
        <span class="admin-entry-icon">⚙️</span>
      </button>
    </footer>

    <!-- 详情弹窗 -->
    <PetModal
      :pet="selectedPet"
      :pets="filteredPets"
      :visible="showModal"
      @close="closeModal"
    />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans SC', 'Ma Shan Zheng', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(180deg, #0a0f25 0%, #1e293b 50%, #0f172a 100%);
  min-height: 100vh;
  overflow-x: hidden;
}

.app-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0f25 0%, #1e293b 50%, #0f172a 100%);
  position: relative;
}

/* Canvas 粒子连线网络背景 */
.particle-canvas-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

/* Header 雪花画布 */
.snow-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

/* Header 样式 */
.app-header {
  background: linear-gradient(135deg, 
    #0a1628 0%, 
    #0f2847 25%, 
    #1e3a5f 50%, 
    #0f2847 75%, 
    #0a1628 100%);
  padding: 55px 24px 65px 24px;
  text-align: center;
  box-shadow: 0 25px 80px rgba(15, 23, 42, 0.7), 
              0 -10px 40px rgba(96, 165, 250, 0.1) inset;
  position: relative;
  overflow: hidden;
  border-bottom: 4px solid transparent;
  border-image: linear-gradient(90deg, 
    transparent, 
    #3b82f6, 
    #60a5fa, 
    #38bdf8, 
    #3b82f6, 
    transparent) 1;
}

.app-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.12) 0%, transparent 50%),
    radial-gradient(circle at 80% 30%, rgba(56, 189, 248, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
  pointer-events: none;
  animation: headerAura 8s ease-in-out infinite;
}

@keyframes headerAura {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.header-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, 
    rgba(96, 165, 250, 0.25) 0%, 
    rgba(59, 130, 246, 0.18) 30%, 
    rgba(56, 189, 248, 0.1) 50%,
    transparent 70%);
  animation: pulseGlow 5s ease-in-out infinite;
  z-index: 0;
}

@keyframes pulseGlow {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  25% {
    transform: translate(-50%, -50%) scale(1.15);
    opacity: 0.8;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 0.7;
  }
  75% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.9;
  }
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.title-icon {
  width: 72px;
  height: 72px;
  object-fit: contain;
  margin-bottom: 8px;
  filter: drop-shadow(0 0 30px rgba(96, 165, 250, 0.9)) drop-shadow(0 0 60px rgba(59, 130, 246, 0.5));
  animation: iconFloat 3s ease-in-out infinite;
  z-index: 10;
}

@keyframes iconFloat {
  0%, 100% { 
    transform: translateY(0) scale(1) rotate(0deg); 
    filter: drop-shadow(0 0 30px rgba(96, 165, 250, 0.9)) drop-shadow(0 0 60px rgba(59, 130, 246, 0.5));
  }
  25% { 
    transform: translateY(-15px) scale(1.1) rotate(-8deg); 
    filter: drop-shadow(0 0 40px rgba(96, 165, 250, 1)) drop-shadow(0 0 80px rgba(59, 130, 246, 0.6));
  }
  50% { 
    transform: translateY(-8px) scale(1.05) rotate(0deg); 
    filter: drop-shadow(0 0 35px rgba(96, 165, 250, 0.95)) drop-shadow(0 0 70px rgba(59, 130, 246, 0.55));
  }
  75% { 
    transform: translateY(-15px) scale(1.1) rotate(8deg); 
    filter: drop-shadow(0 0 40px rgba(96, 165, 250, 1)) drop-shadow(0 0 80px rgba(59, 130, 246, 0.6));
  }
}

.header-title {
  font-size: 52px;
  font-weight: 700;
  letter-spacing: 8px;
  position: relative;
  line-height: 1.2;
  display: flex;
  justify-content: center;
  align-items: center;
  text-shadow: none;
  flex-wrap: wrap;
}

.title-char {
  display: inline-block;
  position: relative;
  font-family: 'Ma Shan Zheng', 'ZCOOL KuaiLe', 'Noto Serif SC', cursive, sans-serif;
  font-weight: 700;
  font-size: 68px;
  letter-spacing: 4px;
  color: #1e293b;
  text-shadow: 
    2px 2px 0 #60a5fa,
    4px 4px 0 #3b82f6,
    6px 6px 0 rgba(59, 130, 246, 0.5),
    0 0 30px rgba(96, 165, 250, 0.6);
  opacity: 0;
  transform: translateY(80px) scale(0.3) rotate(-15deg);
  animation: charRevealBounce 1.1s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.title-char::before {
  content: attr(data-char);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, 
    rgba(96, 165, 250, 0.95) 0%, 
    rgba(59, 130, 246, 0.8) 30%, 
    rgba(37, 99, 235, 0.9) 60%, 
    rgba(59, 130, 246, 0.8) 80%, 
    rgba(96, 165, 250, 0.95) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  z-index: 1;
  opacity: 1;
  filter: drop-shadow(0 0 15px rgba(96, 165, 250, 0.9));
}

.title-char::after {
  content: attr(data-char);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, 
    rgba(255, 255, 255, 0.9) 0%, 
    rgba(190, 220, 255, 0.5) 40%, 
    transparent 70%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  z-index: 2;
  opacity: 0.6;
  pointer-events: none;
}

.title-char:hover {
  transform: scale(1.3) rotate(8deg) translateY(-8px);
  text-shadow: 
    2px 2px 0 #93c5fd,
    4px 4px 0 #60a5fa,
    6px 6px 0 #3b82f6,
    8px 8px 0 rgba(37, 99, 235, 0.5),
    0 0 40px rgba(96, 165, 250, 0.9),
    0 0 80px rgba(59, 130, 246, 0.6);
}

@keyframes charRevealBounce {
  0% {
    opacity: 0;
    transform: translateY(80px) scale(0.3) rotate(-15deg);
  }
  40% {
    opacity: 0.9;
    transform: translateY(-10px) scale(1.25) rotate(8deg);
  }
  60% {
    opacity: 1;
    transform: translateY(5px) scale(0.95) rotate(-3deg);
  }
  80% {
    transform: translateY(-3px) scale(1.05) rotate(2deg);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1) rotate(0deg);
  }
}

.header-title:hover .title-char {
  transform: translateY(-10px) scale(1.25) rotate(8deg);
  letter-spacing: 12px;
}

.header-title:hover .title-char::after {
  opacity: 1;
}

.title-char:hover {
  transform: translateY(-15px) scale(1.4) rotateY(15deg) rotate(5deg) !important;
  background: linear-gradient(180deg, 
    #ffffff 0%, 
    #60a5fa 20%, 
    #3b82f6 50%, 
    #60a5fa 80%, 
    #ffffff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-char:hover::before {
  opacity: 1;
  background: linear-gradient(180deg, 
    rgba(255, 255, 255, 1) 0%, 
    rgba(96, 165, 250, 0.8) 50%, 
    transparent 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  font-size: 22px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  letter-spacing: 4px;
  opacity: 0.95;
  text-transform: uppercase;
}

/* Main content */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 24px;
  position: relative;
  z-index: 1;
}

/* Filter wrapper */
.filter-wrapper {
  opacity: 1;
  animation: filterSlideIn 0.8s ease-out 0.5s both;
}

@keyframes filterSlideIn {
  from {
    opacity: 0;
    transform: translateX(-60px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 淡入动画 */
.fade-in {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120px 20px;
}

.loading-spinner {
  width: 80px;
  height: 80px;
  border: 5px solid rgba(96, 165, 250, 0.2);
  border-top-color: #60a5fa;
  border-right-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 24px;
  box-shadow: 0 0 30px rgba(96, 165, 250, 0.3);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 18px;
  color: #60a5fa;
  font-weight: 600;
  text-shadow: 0 0 20px rgba(96, 165, 250, 0.5);
}

.error-container {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 252, 0.95) 100%);
  border-radius: 28px;
  padding: 56px 48px;
  text-align: center;
  box-shadow: 0 16px 48px rgba(15, 23, 42, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.95);
  max-width: 500px;
  margin: 80px auto;
  border: 2px solid rgba(96, 165, 250, 0.25);
}

.error-text {
  font-size: 18px;
  color: #dc2626;
  font-weight: 600;
  margin-bottom: 28px;
}

.retry-button {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  padding: 14px 40px;
  border-radius: 28px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.retry-button:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.6);
}

.empty-container {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 252, 0.95) 100%);
  border-radius: 28px;
  padding: 56px 48px;
  text-align: center;
  box-shadow: 0 16px 48px rgba(15, 23, 42, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.95);
  max-width: 500px;
  margin: 80px auto;
  border: 2px solid rgba(96, 165, 250, 0.25);
}

.empty-text {
  font-size: 20px;
  color: #475569;
  font-weight: 600;
  margin-bottom: 12px;
}

.empty-hint {
  font-size: 15px;
  color: #94a3b8;
}

.pets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 28px;
  margin-top: 28px;
  min-height: 200px;
  position: relative;
}

/* Transition group animations */
.pets-list-enter-active,
.pets-list-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.pets-list-enter-from {
  opacity: 0;
  transform: translateY(40px) scale(0.85);
}

.pets-list-leave-to {
  opacity: 0;
  transform: translateY(-30px) scale(0.85);
  position: absolute;
}

.pets-list-move {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.app-footer {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  padding: 36px 20px;
  text-align: center;
  margin-top: 60px;
  border-top: 1px solid rgba(96, 165, 250, 0.2);
  position: relative;
  z-index: 1;
}

.footer-text {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 500;
}

.admin-entry {
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(96, 165, 250, 0.25);
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 18px;
}

.admin-entry:hover {
  background: rgba(99, 102, 241, 0.3);
  border-color: rgba(139, 92, 246, 0.5);
  color: #fff;
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
}

.admin-entry-icon {
  font-size: 18px;
  line-height: 1;
}
</style>
