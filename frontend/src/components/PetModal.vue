<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Pet } from '@/types'
import { getGroupColor } from '@/utils/groupColors'
import { getAttributeIconPath } from '@/utils/attributeIcons'

interface Props {
  pet: Pet | null
  pets: Pet[]
  visible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const currentPet = ref<Pet | null>(null)
const isFadingOut = ref(false)

const currentIndex = computed(() => {
  if (!currentPet.value) return 0
  return props.pets.findIndex(p => p.id === currentPet.value!.id)
})



const handleClose = () => {
  emit('close')
}

const prevPet = () => {
  if (props.pets.length === 0) return
  isFadingOut.value = true
  setTimeout(() => {
    const idx = currentIndex.value
    const newIdx = idx > 0 ? idx - 1 : props.pets.length - 1
    currentPet.value = props.pets[newIdx]
    isFadingOut.value = false
  }, 200)
}

const nextPet = () => {
  if (props.pets.length === 0) return
  isFadingOut.value = true
  setTimeout(() => {
    const idx = currentIndex.value
    const newIdx = idx < props.pets.length - 1 ? idx + 1 : 0
    currentPet.value = props.pets[newIdx]
    isFadingOut.value = false
  }, 200)
}

watch(() => props.pet, (newPet) => {
  if (newPet) {
    currentPet.value = newPet
  }
})

watch(() => props.visible, (newVisible) => {
  if (newVisible && props.pet) {
    currentPet.value = props.pet
  }
})
</script>

<template>
  <div v-if="visible && currentPet" class="modal-overlay" @click="handleClose">
    <div class="modal-wrapper" @click.stop>
      <!-- 左侧翻页按钮 -->
      <button class="side-nav-button left-nav" @click="prevPet" title="上一页">
        <span class="side-nav-arrow">‹</span>
        <span class="side-nav-label">上一页</span>
      </button>

      <div class="modal-container">
        <div class="modal-header">
          <h2 class="modal-title">✨ 精灵详情</h2>
          <button class="close-button" @click="handleClose">×</button>
        </div>

        <div class="modal-content" :class="{ fading: isFadingOut }">
          <div class="pet-detail">
            <!-- 左侧区域 -->
            <div class="pet-left-section">
              <div class="pet-image-box">
                <img :src="currentPet.image_url" :alt="currentPet.name" class="detail-image" />
                <div class="image-glow"></div>
              </div>

              <div v-if="currentPet.attributes && currentPet.attributes.length > 0" class="attributes-section">
                <h4 class="section-title">
                  <span class="icon">⚡</span>
                  精灵属性
                </h4>
                <div class="attribute-descriptions">
                  <div v-for="attr in currentPet.attributes" :key="attr" class="attribute-desc">
                    <div class="attribute-name-row">
                      <img :src="getAttributeIconPath(attr)" :alt="attr" class="attribute-icon-small" />
                      <h5 class="attribute-name">{{ attr }}系属性</h5>
                    </div>
                  </div>
                </div>
              </div>

              <div class="price-info">
                <div class="price-icon">💰</div>
                <div class="price-text-wrapper">
                  <span class="price-label">购买价格</span>
                  <span class="price-value-large">{{ currentPet.price }}</span>
                </div>
              </div>
            </div>

            <!-- 右侧区域 -->
            <div class="pet-info-section">
              <div class="pet-header">
                <h3 class="pet-name-large">{{ currentPet.name }}</h3>
                <span class="group-badge" :style="{ background: getGroupColor(currentPet.group) }">
                  {{ currentPet.group }}
                </span>
              </div>

              <div class="abilities-section">
                <h4 class="section-title">
                  <span class="icon">⚔️</span>
                  能力特点
                </h4>
                <ul class="abilities-list">
                  <li v-if="currentPet.abilities && currentPet.abilities.length > 0" v-for="(ability, index) in currentPet.abilities" :key="index">
                    {{ ability }}
                  </li>
                  <li v-else>暂无能力特点信息</li>
                </ul>
              </div>

              <div class="description-section">
                <h4 class="section-title">
                  <span class="icon">📖</span>
                  精灵描述
                </h4>
                <p class="description-text">{{ currentPet.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧翻页按钮 -->
      <button class="side-nav-button right-nav" @click="nextPet" title="下一页">
        <span class="side-nav-label">下一页</span>
        <span class="side-nav-arrow">›</span>
      </button>
    </div>

    <!-- 页码指示器 -->
    <div class="page-indicator">
      第 {{ currentIndex + 1 }} 只 / 共 {{ pets.length }} 只
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(15, 35, 64, 0.94) 100%);
  backdrop-filter: blur(18px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 24px;
  animation: overlayFadeIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes overlayFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-wrapper {
  display: flex;
  align-items: center;
  gap: 0;
  max-width: 780px;
  width: 100%;
}

.modal-container {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%);
  border-radius: 28px;
  width: 100%;
  min-width: 0;
  box-shadow: 
    0 40px 120px rgba(15, 23, 42, 0.55), 
    0 0 0 1px rgba(59, 130, 246, 0.15) inset, 
    0 0 100px rgba(59, 130, 246, 0.08);
  position: relative;
  animation: modalSlideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 2px solid rgba(96, 165, 250, 0.2);
  flex-shrink: 1;
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(45px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  border-bottom: 2px solid transparent;
  border-image: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.4), transparent) 1;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f2847 100%);
  border-radius: 28px 28px 0 0;
}

.modal-title {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(90deg, #60a5fa 0%, #38bdf8 50%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: 1.8px;
}

.close-button {
  background: rgba(255, 255, 255, 0.14);
  border: 2px solid rgba(96, 165, 250, 0.35);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  font-size: 26px;
  font-weight: 300;
  color: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.close-button:hover {
  background: rgba(239, 68, 68, 0.95);
  border-color: rgba(239, 68, 68, 0.95);
  transform: rotate(90deg) scale(1.12);
  box-shadow: 0 8px 28px rgba(239, 68, 68, 0.45);
}

.modal-content {
  padding: 24px 28px 28px 28px;
  transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-content.fading {
  opacity: 0;
}

.pet-detail {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

/* 左右翻页按钮 */
.side-nav-button {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 48px;
  height: 110px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.18) 0%, rgba(37, 99, 235, 0.22) 100%);
  border: 2px solid rgba(96, 165, 250, 0.3);
  border-radius: 14px;
  color: #93c5fd;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  backdrop-filter: blur(10px);
}

.left-nav {
  margin-right: -8px;
}

.right-nav {
  margin-left: -8px;
}

.side-nav-button:hover {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-color: #60a5fa;
  color: white;
  transform: scale(1.05);
  box-shadow: 0 16px 44px rgba(37, 99, 235, 0.55);
}

.side-nav-button:active {
  transform: scale(0.95);
}

.side-nav-arrow {
  font-size: 28px;
  font-weight: 300;
  line-height: 1;
}

.side-nav-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  writing-mode: vertical-rl;
}

/* 左侧区域 */
.pet-left-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 240px;
  flex-shrink: 0;
}

.pet-image-box {
  background: linear-gradient(145deg, #eff6ff 0%, #dbeafe 30%, #e0f2fe 70%, #f0f9ff 100%);
  border-radius: 16px;
  padding: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 14px 38px rgba(15, 23, 42, 0.15), inset 0 2px 0 rgba(255, 255, 255, 0.95);
  position: relative;
  overflow: hidden;
  border: 2px solid rgba(96, 165, 250, 0.18);
  aspect-ratio: 1 / 1;
}

.image-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(96, 165, 250, 0.15) 0%, transparent 60%);
  animation: glowPulse 3.5s ease-in-out infinite;
  pointer-events: none;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.9; transform: translate(-50%, -50%) scale(1.15); }
}

.detail-image {
  width: 100%;
  height: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: 16px;
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 14px 28px rgba(15, 23, 42, 0.18));
  transition: all 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.detail-image:hover {
  transform: scale(1.06);
  filter: drop-shadow(0 20px 40px rgba(15, 23, 42, 0.28));
}

/* 属性部分 */
.attributes-section {
  background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 14px;
  padding: 14px;
  border: 1px solid rgba(59, 130, 246, 0.12);
  box-shadow: 0 5px 18px rgba(15, 23, 42, 0.08);
}

.section-title {
  font-size: 14px;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 10px 0;
  letter-spacing: 0.4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title .icon {
  font-size: 14px;
}

.attribute-descriptions {
  background: white;
  border-radius: 10px;
  padding: 10px;
  border: 1px solid rgba(15, 23, 42, 0.05);
}

.attribute-desc {
  margin-bottom: 6px;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.attribute-desc:hover {
  background: rgba(59, 130, 246, 0.06);
  transform: translateX(4px);
}

.attribute-desc:last-child {
  margin-bottom: 0;
}

.attribute-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.attribute-icon-small {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.attribute-name {
  font-size: 12px;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
}

/* 价格信息 */
.price-info {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
  padding: 14px 18px;
  border-radius: 14px;
  box-shadow: 0 8px 28px rgba(37, 99, 235, 0.4);
  position: relative;
  overflow: hidden;
}

.price-info::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
  transition: left 0.85s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.price-info:hover::before {
  left: 100%;
}

.price-icon {
  font-size: 32px;
  filter: drop-shadow(0 2px 10px rgba(15, 23, 42, 0.25));
  position: relative;
  z-index: 1;
}

.price-text-wrapper {
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.price-label {
  font-size: 12px;
  font-weight: 700;
  color: rgba(219, 234, 254, 0.95);
  margin-bottom: 2px;
  letter-spacing: 0.6px;
}

.price-value-large {
  font-size: 28px;
  font-weight: 900;
  color: white;
  line-height: 1;
  text-shadow: 0 2px 12px rgba(15, 23, 42, 0.2);
}

/* 右侧信息区 */
.pet-info-section {
  flex: 1;
  min-width: 240px;
  overflow: hidden;
}

.pet-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.pet-name-large {
  font-size: 26px;
  font-weight: 900;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: 1px;
}

.group-badge {
  color: white;
  padding: 7px 18px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.6px;
  box-shadow: 0 7px 24px rgba(15, 23, 42, 0.25);
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.group-badge:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 12px 34px rgba(15, 23, 42, 0.35);
}

.abilities-section,
.description-section {
  margin-bottom: 16px;
}

.abilities-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.abilities-list li {
  padding: 9px 0;
  padding-left: 24px;
  position: relative;
  color: #334155;
  font-size: 13px;
  line-height: 1.6;
  border-radius: 10px;
  margin-bottom: 2px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.abilities-list li:hover {
  background: rgba(59, 130, 246, 0.06);
  padding-left: 28px;
}

.abilities-list li::before {
  content: '✦';
  position: absolute;
  left: 6px;
  color: #3b82f6;
  font-weight: bold;
  font-size: 12px;
}

.description-text {
  font-size: 13px;
  color: #334155;
  line-height: 1.75;
  margin: 0;
  padding: 16px;
  background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.05);
}

/* 页码指示器 */
.page-indicator {
  font-size: 12px;
  font-weight: 700;
  color: #93c5fd;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 58, 95, 0.85) 100%);
  padding: 10px 24px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  margin-top: 16px;
  border: 1px solid rgba(96, 165, 250, 0.25);
  backdrop-filter: blur(10px);
}
</style>
