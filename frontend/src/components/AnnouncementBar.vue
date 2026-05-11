<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAnnouncement } from '@/api'
import type { Announcement } from '@/types'

const announcement = ref<Announcement | null>(null)

onMounted(async () => {
    try {
        const data = await getAnnouncement()
        if (data && data.content) {
            announcement.value = data
        }
    } catch (err) {
        console.error('加载公告失败:', err)
    }
})
</script>

<template>
    <div v-if="announcement" class="announcement-bar">
        <div class="announcement-icon">
            <span class="icon-bell">📢</span>
        </div>
        <div class="announcement-content">
            <span class="announcement-label">公告</span>
            <span class="announcement-divider"></span>
            <span class="announcement-text">{{ announcement.content }}</span>
        </div>
        <div class="announcement-sparkle"></div>
    </div>
</template>

<style scoped>
.announcement-bar {
    position: relative;
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 18px 28px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(15, 23, 42, 0.25), 0 2px 8px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    max-width: 900px;
    margin: 0 auto 32px auto;
    z-index: 1;
    animation: announceSlideIn 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.announcement-bar::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 18px;
    padding: 2px;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #3b82f6 100%);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
}

.announcement-bar:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(59, 130, 246, 0.2), 0 4px 16px rgba(139, 92, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

@keyframes announceSlideIn {
    from {
        opacity: 0;
        transform: translateY(-24px) scale(0.96);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.announcement-icon {
    flex-shrink: 0;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
    position: relative;
    overflow: hidden;
}

.announcement-icon::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.25) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.4s ease;
}

.announcement-bar:hover .announcement-icon::after {
    opacity: 1;
}

.icon-bell {
    font-size: 24px;
    line-height: 1;
    position: relative;
    z-index: 1;
    animation: bellRing 3s ease-in-out infinite;
}

@keyframes bellRing {
    0%, 100% { transform: rotate(0); }
    5% { transform: rotate(12deg); }
    10% { transform: rotate(-10deg); }
    15% { transform: rotate(6deg); }
    20% { transform: rotate(-4deg); }
    25% { transform: rotate(0); }
}

.announcement-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}

.announcement-label {
    flex-shrink: 0;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #93c5fd;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 18px;
    background: rgba(59, 130, 246, 0.18);
    border: 1px solid rgba(59, 130, 246, 0.3);
    transition: all 0.3s ease;
}

.announcement-bar:hover .announcement-label {
    background: rgba(59, 130, 246, 0.28);
    border-color: rgba(96, 165, 250, 0.5);
}

.announcement-divider {
    flex-shrink: 0;
    width: 1px;
    height: 20px;
    background: linear-gradient(180deg, transparent, rgba(147, 197, 253, 0.4), transparent);
}

.announcement-text {
    font-size: 16px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.6;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: color 0.3s ease;
}

.announcement-bar:hover .announcement-text {
    color: rgba(255, 255, 255, 1);
}

.announcement-sparkle {
    position: absolute;
    top: 6px;
    right: 16px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #93c5fd;
    box-shadow: 0 0 8px #60a5fa, 0 0 16px #3b82f6;
    opacity: 0;
    transition: opacity 0.5s ease;
}

.announcement-bar:hover .announcement-sparkle {
    opacity: 1;
}
</style>
