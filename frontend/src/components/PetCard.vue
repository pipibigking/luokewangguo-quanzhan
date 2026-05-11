<script setup lang="ts">
import type { Pet } from '@/types'
import { getGroupColor } from '@/utils/groupColors'
import { getAttributeIconPath } from '@/utils/attributeIcons'

interface Props {
  pet: Pet
  index: number
}

const props = defineProps<Props>()
const emit = defineEmits<{ click: [pet: Pet] }>()

const handleClick = () => {
  emit('click', props.pet)
}
</script>

<template>
  <div class="pet-card" :style="{ animationDelay: (index * 60) + 'ms' }" @click="handleClick">
    <div class="card-badge" :style="{ background: getGroupColor(pet.group) }">
      {{ pet.group }}
    </div>
    <div class="card-glow"></div>
    <div class="card-image-wrapper">
      <img :src="pet.image_url" :alt="pet.name" class="pet-image" />
      <div class="image-overlay"></div>
      <div class="image-shine"></div>
    </div>
    <div class="card-content">
      <h3 class="pet-name">{{ pet.name }}</h3>
      <div v-if="pet.attributes && pet.attributes.length > 0" class="pet-attributes">
        <img
          v-for="attr in pet.attributes.slice(0, 3)"
          :key="attr"
          :src="getAttributeIconPath(attr)"
          :alt="attr"
          class="attr-icon"
        />
      </div>
      <div class="pet-price">
        <span class="price-label">价格</span>
        <span class="price-value">{{ pet.price }}</span>
      </div>
    </div>
    <div class="card-click-hint">查看详情 →</div>
  </div>
</template>

<style scoped>
.pet-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.9) 100%);
  border-radius: 28px;
  padding: 18px;
  box-shadow: 0 10px 40px rgba(15, 23, 42, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.95);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  border: 2px solid rgba(96, 165, 250, 0.35);
  display: flex;
  flex-direction: column;
  opacity: 0;
  transform: translateY(40px) scale(0.9);
  animation: cardEntry 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes cardEntry {
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.pet-card:hover {
  transform: translateY(-12px) scale(1.03);
  box-shadow: 0 24px 60px rgba(59, 130, 246, 0.25);
  border-color: rgba(96, 165, 250, 0.6);
}

.pet-card:active {
  transform: translateY(-12px) scale(0.98);
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(96, 165, 250, 0.12) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.pet-card:hover .card-glow {
  opacity: 1;
}

.card-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  color: white;
  padding: 7px 16px;
  border-radius: 22px;
  font-size: 11px;
  font-weight: 800;
  z-index: 10;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.25);
  backdrop-filter: blur(10px);
}

.card-image-wrapper {
  position: relative;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #e0f2fe 100%);
  border-radius: 22px;
  padding: 0;
  margin-bottom: 18px;
  overflow: hidden;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.8) 0%, transparent 50%),
              radial-gradient(circle at 70% 80%, rgba(255, 255, 255, 0.5) 0%, transparent 50%);
  pointer-events: none;
}

.image-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.8s ease;
}

.pet-card:hover .image-shine {
  left: 100%;
}

.pet-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 10px 20px rgba(15, 23, 42, 0.15));
}

.pet-card:hover .pet-image {
  transform: scale(1.18) rotate(3deg);
  filter: drop-shadow(0 16px 32px rgba(15, 23, 42, 0.25));
}

.card-content {
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.pet-name {
  font-size: 19px;
  font-weight: 900;
  color: #1e293b;
  margin: 0;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
}

.pet-attributes {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin: 6px 0;
}

.attr-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  background: white;
  box-shadow: 0 3px 12px rgba(15, 23, 42, 0.12);
  border: 2px solid transparent;
}

.pet-card:hover .attr-icon {
  transform: scale(1.25) rotate(10deg);
  border-color: rgba(96, 165, 250, 0.5);
}

.pet-price {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: auto;
}

.price-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.price-value {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 9px 26px;
  border-radius: 24px;
  font-weight: 900;
  font-size: 17px;
  box-shadow: 0 5px 16px rgba(59, 130, 246, 0.4);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.pet-card:hover .price-value {
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.55);
}

.card-click-hint {
  margin-top: 14px;
  font-size: 13px;
  color: #64748b;
  text-align: center;
  opacity: 0;
  transform: translateY(6px);
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.pet-card:hover .card-click-hint {
  opacity: 1;
  transform: translateY(0);
  color: #3b82f6;
}
</style>
