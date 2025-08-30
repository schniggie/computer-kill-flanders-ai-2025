<template>
  <div class="warning-component" :class="[`warning-${type}`, { 'animated': animated }]">
    <!-- Warning header -->
    <div class="warning-header">
      <div class="flex items-center space-x-3">
        <!-- Icon based on type -->
        <div class="warning-icon">
          <div v-if="type === 'nuclear'" class="nuclear-symbol">☢️</div>
          <div v-else-if="type === 'danger'" class="danger-symbol">⚠️</div>
          <div v-else-if="type === 'security'" class="security-symbol">🔒</div>
          <div v-else-if="type === 'hack'" class="hack-symbol">💀</div>
          <div v-else-if="type === 'info'" class="info-symbol">ℹ️</div>
          <div v-else class="default-symbol">⚡</div>
        </div>
        
        <!-- Title -->
        <div class="warning-title">
          <span class="title-text">{{ title || getDefaultTitle() }}</span>
          <span v-if="classified" class="classified-badge">[CLASSIFIED]</span>
        </div>
        
        <!-- Alert level -->
        <div v-if="level" class="alert-level">
          LEVEL {{ level }}
        </div>
      </div>
    </div>
    
    <!-- Warning body -->
    <div class="warning-body">
      <!-- Content slot -->
      <div class="warning-content">
        <slot />
      </div>
      
      <!-- Additional info -->
      <div v-if="timestamp || author" class="warning-footer">
        <div class="flex justify-between text-xs">
          <span v-if="author">{{ author }}</span>
          <span v-if="timestamp">{{ formatTimestamp() }}</span>
        </div>
      </div>
    </div>
    
    <!-- Blinking alert indicator -->
    <div v-if="blinking" class="blink-indicator"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'nuclear' | 'danger' | 'security' | 'hack' | 'info' | 'warning'
  title?: string
  level?: number
  classified?: boolean
  animated?: boolean
  blinking?: boolean
  timestamp?: boolean
  author?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'warning',
  classified: false,
  animated: true,
  blinking: false,
  timestamp: false
})

const getDefaultTitle = () => {
  const titles = {
    nuclear: 'NUCLEAR ALERT',
    danger: 'DANGER',
    security: 'SECURITY BREACH',
    hack: 'CYBER ATTACK DETECTED',
    info: 'INFORMATION',
    warning: 'WARNING'
  }
  return titles[props.type]
}

const formatTimestamp = () => {
  return new Date().toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}
</script>

<style scoped>
.warning-component {
  @apply rounded-lg overflow-hidden shadow-xl mb-6;
  background: rgba(0, 0, 0, 0.9);
  border: 2px solid;
  font-family: 'Fira Code', 'Courier New', monospace;
  position: relative;
}

/* Nuclear warning */
.warning-nuclear {
  border-color: #39ff14;
  box-shadow: 
    0 0 30px rgba(57, 255, 20, 0.4),
    inset 0 0 20px rgba(57, 255, 20, 0.1);
}

.warning-nuclear .warning-header {
  background: linear-gradient(90deg, rgba(57, 255, 20, 0.2) 0%, rgba(57, 255, 20, 0.1) 100%);
}

/* Danger warning */
.warning-danger {
  border-color: #ff073a;
  box-shadow: 
    0 0 30px rgba(255, 7, 58, 0.4),
    inset 0 0 20px rgba(255, 7, 58, 0.1);
}

.warning-danger .warning-header {
  background: linear-gradient(90deg, rgba(255, 7, 58, 0.2) 0%, rgba(255, 7, 58, 0.1) 100%);
}

/* Security warning */
.warning-security {
  border-color: #ffd90f;
  box-shadow: 
    0 0 30px rgba(255, 217, 15, 0.4),
    inset 0 0 20px rgba(255, 217, 15, 0.1);
}

.warning-security .warning-header {
  background: linear-gradient(90deg, rgba(255, 217, 15, 0.2) 0%, rgba(255, 217, 15, 0.1) 100%);
}

/* Hack warning */
.warning-hack {
  border-color: #8b00ff;
  box-shadow: 
    0 0 30px rgba(139, 0, 255, 0.4),
    inset 0 0 20px rgba(139, 0, 255, 0.1);
}

.warning-hack .warning-header {
  background: linear-gradient(90deg, rgba(139, 0, 255, 0.2) 0%, rgba(139, 0, 255, 0.1) 100%);
}

/* Info warning */
.warning-info {
  border-color: #00bfff;
  box-shadow: 
    0 0 30px rgba(0, 191, 255, 0.4),
    inset 0 0 20px rgba(0, 191, 255, 0.1);
}

.warning-info .warning-header {
  background: linear-gradient(90deg, rgba(0, 191, 255, 0.2) 0%, rgba(0, 191, 255, 0.1) 100%);
}

/* Default warning */
.warning-warning {
  border-color: #ffa500;
  box-shadow: 
    0 0 30px rgba(255, 165, 0, 0.4),
    inset 0 0 20px rgba(255, 165, 0, 0.1);
}

.warning-warning .warning-header {
  background: linear-gradient(90deg, rgba(255, 165, 0, 0.2) 0%, rgba(255, 165, 0, 0.1) 100%);
}

/* Header styling */
.warning-header {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.warning-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 0 8px currentColor);
}

.warning-title {
  display: flex;
  align-items: center;
  space-x: 2;
}

.title-text {
  font-weight: bold;
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.classified-badge {
  @apply ml-3 px-2 py-1 text-xs rounded;
  background: rgba(255, 0, 0, 0.8);
  color: white;
  font-weight: bold;
  animation: pulse 2s infinite;
}

.alert-level {
  @apply ml-auto px-3 py-1 text-xs rounded;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid currentColor;
  font-weight: bold;
}

/* Body styling */
.warning-body {
  padding: 16px;
}

.warning-content {
  line-height: 1.6;
  color: #e0e0e0;
}

.warning-content :deep(p) {
  margin-bottom: 1rem;
}

.warning-content :deep(strong) {
  color: inherit;
  font-weight: bold;
  text-shadow: 0 0 5px currentColor;
}

.warning-content :deep(code) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: inherit !important;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid currentColor;
  box-shadow: 0 0 5px currentColor;
}

.warning-footer {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  opacity: 0.7;
}

/* Animation effects */
.animated {
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Blinking indicator */
.blink-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 12px;
  height: 12px;
  background: #ff073a;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}
</style>