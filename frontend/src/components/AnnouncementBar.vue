<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getAnnouncement } from '@/api'
import type { Announcement } from '@/types'

const announcement = ref<Announcement | null>(null)
const expanded = ref(false)
const needExpand = ref(false)

const displayContent = computed(() => {
    if (!announcement.value?.content) return ''
    return announcement.value.content
})

function toggleExpand() {
    expanded.value = !expanded.value
}

onMounted(async () => {
    try {
        const data = await getAnnouncement()
        if (data && data.content) {
            announcement.value = data
            if (data.content.length > 60 || data.content.includes('\n')) {
                needExpand.value = true
            }
        }
    } catch (err) {
        console.error('加载公告失败:', err)
    }
})
</script>

<template>
    <div v-if="announcement" class="announcement-bar" :class="{ 'is-expanded': expanded }">
        <div class="bar-bg"></div>
        <div class="bar-grid"></div>
        <div class="bar-glow"></div>

        <div class="bar-corner top-left"></div>
        <div class="bar-corner top-right"></div>
        <div class="bar-corner bottom-left"></div>
        <div class="bar-corner bottom-right"></div>

        <div class="bar-dot dot-1"></div>
        <div class="bar-dot dot-2"></div>
        <div class="bar-dot dot-3"></div>
        <div class="bar-dot dot-4"></div>

        <div class="bar-header">
            <div class="bar-icon-box">
                <svg class="bar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="3" />
                    <path d="M9 9h6v6H9z" />
                    <path d="M12 3v3M12 18v3M3 12h3M18 12h3" />
                </svg>
            </div>
            <span class="bar-label">系统公告</span>
            <div class="bar-badge">LIVE</div>
            <div class="bar-pulse"></div>
        </div>

        <div class="bar-body">
            <div
                ref="textRef"
                class="bar-text"
                :class="{ 'is-collapsed': !expanded && needExpand }"
            >{{ displayContent }}</div>
            <button
                v-if="needExpand"
                class="bar-toggle"
                @click="toggleExpand"
            >
                <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline v-if="!expanded" points="6 9 12 15 18 9" />
                    <polyline v-else points="18 15 12 9 6 15" />
                </svg>
                <span>{{ expanded ? '收起' : '展开全文' }}</span>
            </button>
        </div>
    </div>
</template>

<style scoped>
.announcement-bar {
    position: relative;
    padding: 24px 28px;
    border-radius: 14px;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    max-width: 900px;
    margin: 0 auto 32px auto;
    z-index: 1;
    animation: barIn 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
    border: 1px solid rgba(6, 182, 212, 0.3);
    box-shadow: 0 4px 24px rgba(6, 182, 212, 0.12), inset 0 1px 0 rgba(6, 182, 212, 0.1);
}

.announcement-bar:hover {
    border-color: rgba(6, 182, 212, 0.5);
    box-shadow: 0 8px 40px rgba(6, 182, 212, 0.2), inset 0 1px 0 rgba(6, 182, 212, 0.15);
}

@keyframes barIn {
    from {
        opacity: 0;
        transform: translateY(-24px) scale(0.96);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.bar-bg {
    position: absolute;
    inset: 0;
    background: url('/images/bg/机械方方青色星星.jpg') center center / cover no-repeat;
    z-index: -2;
}

.bar-bg::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg,
        rgba(8, 30, 50, 0.85) 0%,
        rgba(8, 145, 178, 0.25) 50%,
        rgba(8, 30, 50, 0.85) 100%
    );
}

.bar-grid {
    position: absolute;
    inset: 0;
    z-index: -1;
    background-image:
        linear-gradient(rgba(6, 182, 212, 0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(6, 182, 212, 0.06) 1px, transparent 1px);
    background-size: 24px 24px;
}

.bar-glow {
    position: absolute;
    top: -50%;
    left: 50%;
    width: 60%;
    height: 100%;
    background: radial-gradient(ellipse, rgba(6, 182, 212, 0.15) 0%, transparent 70%);
    transform: translateX(-50%);
    pointer-events: none;
    z-index: -1;
}

.bar-corner {
    position: absolute;
    width: 16px;
    height: 16px;
    border-color: rgba(6, 182, 212, 0.4);
    transition: border-color 0.3s ease;
}

.announcement-bar:hover .bar-corner {
    border-color: rgba(6, 182, 212, 0.7);
}

.bar-corner.top-left {
    top: 6px;
    left: 6px;
    border-top: 2px solid;
    border-left: 2px solid;
}

.bar-corner.top-right {
    top: 6px;
    right: 6px;
    border-top: 2px solid;
    border-right: 2px solid;
}

.bar-corner.bottom-left {
    bottom: 6px;
    left: 6px;
    border-bottom: 2px solid;
    border-left: 2px solid;
}

.bar-corner.bottom-right {
    bottom: 6px;
    right: 6px;
    border-bottom: 2px solid;
    border-right: 2px solid;
}

.bar-dot {
    position: absolute;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: rgba(6, 182, 212, 0.5);
    animation: dotPulse 2s ease-in-out infinite;
}

.bar-dot.dot-1 { top: 10px; left: 50%; animation-delay: 0s; }
.bar-dot.dot-2 { top: 50%; right: 10px; animation-delay: 0.5s; }
.bar-dot.dot-3 { bottom: 10px; left: 60%; animation-delay: 1s; }
.bar-dot.dot-4 { top: 40%; left: 10px; animation-delay: 1.5s; }

@keyframes dotPulse {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 1; transform: scale(2); }
}

.bar-header {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.bar-icon-box {
    flex-shrink: 0;
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(6, 182, 212, 0.15);
    border: 1px solid rgba(6, 182, 212, 0.3);
    color: #22d3ee;
}

.bar-icon-svg {
    width: 20px;
    height: 20px;
}

.bar-label {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #22d3ee;
    text-transform: uppercase;
    text-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
}

.bar-badge {
    flex-shrink: 0;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #0c4a6e;
    padding: 2px 8px;
    border-radius: 4px;
    background: #22d3ee;
    animation: badgeBlink 2s ease-in-out infinite;
}

@keyframes badgeBlink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.bar-pulse {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22d3ee;
    box-shadow: 0 0 8px #06b6d4, 0 0 16px #0891b2;
    animation: pulseRing 2s ease-in-out infinite;
}

@keyframes pulseRing {
    0%, 100% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.3); }
}

.bar-body {
    margin-top: 16px;
    position: relative;
    z-index: 1;
    padding-top: 16px;
    border-top: 1px solid rgba(6, 182, 212, 0.15);
}

.bar-text {
    font-size: 15px;
    font-weight: 400;
    color: rgba(226, 232, 240, 0.92);
    line-height: 1.8;
    word-break: break-word;
    white-space: pre-wrap;
    transition: all 0.3s ease;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.bar-text.is-collapsed {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
}

.bar-toggle {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-top: 10px;
    padding: 6px 14px;
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 6px;
    background: rgba(6, 182, 212, 0.08);
    color: #22d3ee;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s ease;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.bar-toggle:hover {
    background: rgba(6, 182, 212, 0.2);
    border-color: rgba(6, 182, 212, 0.5);
    transform: translateY(-1px);
}

.bar-toggle:active {
    transform: scale(0.96);
}

.toggle-icon {
    width: 16px;
    height: 16px;
}
</style>
