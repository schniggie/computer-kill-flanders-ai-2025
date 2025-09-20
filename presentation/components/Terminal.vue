<template>
  <div class="terminal-component" :class="{ 'fullscreen': fullscreen }">
    <!-- Terminal window header -->
    <div class="terminal-window-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <button class="w-3 h-3 rounded-full bg-red-500 hover:bg-red-400"></button>
          <button class="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-400"></button>
          <button class="w-3 h-3 rounded-full bg-green-500 hover:bg-green-400"></button>
          <span class="ml-4 text-gray-400 text-sm font-mono">{{ title || 'Terminal' }}</span>
        </div>
        <div class="text-xs text-gray-500 font-mono">
          {{ host }}
        </div>
      </div>
    </div>
    
    <!-- Terminal body -->
    <div class="terminal-window-body" :style="{ height: height }">
      <div class="p-4 font-mono text-sm">
        <!-- Command history -->
        <div class="space-y-2">
          <div v-for="(line, index) in displayLines" :key="index" class="flex">
            <div v-if="line.type === 'prompt'" class="flex items-center space-x-1 min-w-0">
              <span class="text-yellow-400">{{ user }}</span>
              <span class="text-gray-400">@</span>
              <span class="text-blue-400">{{ hostname }}</span>
              <span class="text-gray-400">:</span>
              <span class="text-green-400">{{ workdir }}</span>
              <span class="text-gray-400">$</span>
              <span class="text-green-400 ml-2">{{ line.command }}</span>
              <span v-if="index === displayLines.length - 1 && typing" class="cursor text-green-400">_</span>
            </div>
            <div v-else-if="line.type === 'output'" class="text-green-400 whitespace-pre-wrap">{{ line.text }}</div>
            <div v-else-if="line.type === 'error'" class="text-red-400 whitespace-pre-wrap">{{ line.text }}</div>
            <div v-else-if="line.type === 'warning'" class="text-yellow-400 whitespace-pre-wrap">{{ line.text }}</div>
          </div>
          
          <!-- Current prompt (if not typing) -->
          <div v-if="!typing && ready" class="flex items-center space-x-1">
            <span class="text-yellow-400">{{ user }}</span>
            <span class="text-gray-400">@</span>
            <span class="text-blue-400">{{ hostname }}</span>
            <span class="text-gray-400">:</span>
            <span class="text-green-400">{{ workdir }}</span>
            <span class="text-gray-400">$</span>
            <span class="cursor text-green-400 ml-2">_</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

interface TerminalLine {
  type: 'prompt' | 'output' | 'error' | 'warning'
  command?: string
  text?: string
}

interface Props {
  commands?: Array<{ command: string; output?: string; delay?: number; error?: boolean; warning?: boolean }>
  autoplay?: boolean
  typeSpeed?: number
  user?: string
  hostname?: string
  workdir?: string
  host?: string
  title?: string
  height?: string
  fullscreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  commands: () => [],
  autoplay: true,
  typeSpeed: 50,
  user: 'homer',
  hostname: 'nuclear-plant',
  workdir: '~/offensive-ai',
  host: 'root@nuclear-plant',
  title: 'Terminal — Security Research',
  height: '400px',
  fullscreen: false
})

const lines = ref<TerminalLine[]>([])
const currentCommandIndex = ref(0)
const typing = ref(false)
const ready = ref(false)

const displayLines = computed(() => lines.value)

let typeTimeout: NodeJS.Timeout

const typeCommand = async (command: string, output?: string, error?: boolean, warning?: boolean) => {
  typing.value = true
  
  // Type command character by character
  const promptLine: TerminalLine = { type: 'prompt', command: '' }
  lines.value.push(promptLine)
  
  for (let i = 0; i <= command.length; i++) {
    promptLine.command = command.slice(0, i)
    await new Promise(resolve => {
      typeTimeout = setTimeout(resolve, props.typeSpeed)
    })
  }
  
  // Add output if provided
  if (output) {
    await new Promise(resolve => setTimeout(resolve, 200))
    lines.value.push({
      type: error ? 'error' : warning ? 'warning' : 'output',
      text: output
    })
  }
  
  typing.value = false
  currentCommandIndex.value++
}

const runCommands = async () => {
  if (!props.autoplay) return
  
  for (const cmd of props.commands) {
    await new Promise(resolve => setTimeout(resolve, cmd.delay || 1000))
    await typeCommand(cmd.command, cmd.output, cmd.error, cmd.warning)
  }
  
  ready.value = true
}

onMounted(() => {
  if (props.commands.length > 0) {
    runCommands()
  } else {
    ready.value = true
  }
})

// Expose methods for manual control
defineExpose({
  executeCommand: typeCommand,
  clear: () => {
    lines.value = []
    currentCommandIndex.value = 0
    ready.value = true
  }
})
</script>

<style scoped>
.terminal-component {
  @apply rounded-lg overflow-hidden shadow-xl;
  background: #0a0a0a;
  border: 2px solid #39ff14;
  box-shadow: 
    0 0 30px rgba(57, 255, 20, 0.3),
    inset 0 0 30px rgba(57, 255, 20, 0.05);
  font-family: 'Fira Code', 'Monaco', 'Courier New', monospace;
}

.terminal-component.fullscreen {
  @apply fixed inset-4 z-50;
}

.terminal-window-header {
  background: #1a1a1a;
  border-bottom: 1px solid #39ff14;
  padding: 8px 16px;
  box-shadow: inset 0 0 10px rgba(57, 255, 20, 0.1);
}

.terminal-window-body {
  background: #0f0f0f;
  position: relative;
  overflow-y: auto;
}

.terminal-window-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(transparent 50%, rgba(0, 255, 0, 0.02) 50%);
  background-size: 100% 2px;
  animation: scanlines 0.1s linear infinite;
  pointer-events: none;
}

@keyframes scanlines {
  0% { transform: translateY(0px); }
  100% { transform: translateY(2px); }
}

/* Scrollbar styling */
.terminal-window-body::-webkit-scrollbar {
  width: 8px;
}

.terminal-window-body::-webkit-scrollbar-track {
  background: #0a0a0a;
}
</style>