<template>
  <div class="slidev-layout terminal relative overflow-hidden">
    <!-- Scanline effect -->
    <div class="scanline-overlay"></div>
    
    <!-- Terminal window -->
    <div class="h-full p-8 flex flex-col">
      <!-- Terminal header -->
      <div class="terminal-header">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="text-red-400 text-lg">●</span>
            <span class="text-yellow-400 text-lg">●</span>  
            <span class="text-green-400 text-lg">●</span>
            <span class="ml-4 text-gray-400 text-sm">Terminal — homer@nuclear-plant</span>
          </div>
          <div class="text-xs text-gray-500 font-mono">
            {{ new Date().toLocaleString() }}
          </div>
        </div>
      </div>
      
      <!-- Terminal body -->
      <div class="flex-1 terminal-body p-6 overflow-hidden">

        <!-- Command prompt
        <div class="flex items-center space-x-2 text-green-400 mb-4 font-mono text-sm">
          <span class="text-yellow-400">homer@nuclear-plant</span>
          <span class="text-white">:</span>
          <span class="text-blue-400">~/offensive-ai</span>
          <span class="text-white">$</span>
          <span class="text-gray-400">cat presentation.md</span>
        </div>
        -->
        
        <!-- Content area -->
        <div class="terminal-content text-green-400">
          <slot />
        </div>
        
        <!-- Blinking cursor -->
        <div class="flex items-center mt-4">
          <span class="text-yellow-400 font-mono text-sm">homer@nuclear-plant</span>
          <span class="text-white font-mono text-sm">:</span>
          <span class="text-blue-400 font-mono text-sm">~/offensive-ai</span>
          <span class="text-white font-mono text-sm">$</span>
          <span class="cursor text-green-400 font-mono">_</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.slidev-layout.terminal {
  background: #0a0a0a;
  font-family: 'Fira Code', 'Monaco', 'Courier New', monospace;
  position: relative;
}

/* Scanline CRT effect */
.scanline-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(transparent 50%, rgba(0, 255, 0, 0.03) 50%);
  background-size: 100% 4px;
  animation: scanlines 0.1s linear infinite;
  pointer-events: none;
  z-index: 1000;
}

@keyframes scanlines {
  0% { transform: translateY(0px); }
  100% { transform: translateY(4px); }
}

/* Terminal header styling */
.terminal-header {
  background: #1a1a1a;
  border: 2px solid #39ff14;
  border-bottom: 1px solid #39ff14;
  border-radius: 8px 8px 0 0;
  padding: 8px 16px;
  box-shadow: 
    0 0 20px rgba(57, 255, 20, 0.3),
    inset 0 0 20px rgba(57, 255, 20, 0.1);
}

/* Terminal body styling */
.terminal-body {
  background: #0f0f0f;
  border: 2px solid #39ff14;
  border-top: none;
  border-radius: 0 0 8px 8px;
  box-shadow: 
    0 0 20px rgba(57, 255, 20, 0.3),
    inset 0 0 20px rgba(57, 255, 20, 0.1);
  position: relative;
}

/* Content styling */
.terminal-content {
  line-height: 1.6;
  font-size: 1.1rem;
}

.terminal-content :deep(h1) {
  color: #ffd90f;
  text-shadow: 0 0 10px rgba(255, 217, 15, 0.5);
  font-size: 2rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #39ff14;
  padding-bottom: 0.5rem;
}

.terminal-content :deep(h2) {
  color: #39ff14;
  text-shadow: 0 0 8px rgba(57, 255, 20, 0.4);
  font-size: 1.5rem;
  margin: 1.5rem 0 0.8rem 0;
}

.terminal-content :deep(h3) {
  color: #ff073a;
  text-shadow: 0 0 8px rgba(255, 7, 58, 0.4);
  font-size: 1.2rem;
  margin: 1rem 0 0.5rem 0;
}

.terminal-content :deep(p) {
  color: #e0e0e0;
  margin-bottom: 1rem;
}

.terminal-content :deep(ul) {
  color: #e0e0e0;
  margin-left: 2rem;
}

.terminal-content :deep(li) {
  margin-bottom: 0.5rem;
  position: relative;
}

.terminal-content :deep(li::marker) {
  color: #39ff14;
}

.terminal-content :deep(pre) {
  background: #1a1a1a !important;
  color: #39ff14 !important;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid rgba(57, 255, 20, 0.3);
  box-shadow: 0 0 15px rgba(57, 255, 20, 0.2);
  margin: 1rem 0;
  overflow-x: auto;
}

.terminal-content :deep(strong) {
  color: #ffd90f;
  text-shadow: 0 0 5px rgba(255, 217, 15, 0.4);
}

.terminal-content :deep(em) {
  color: #ff073a;
  font-style: italic;
}

/* Glow effects for emphasis */
.terminal-content :deep(.highlight) {
  color: #ffd90f;
  text-shadow: 0 0 10px rgba(255, 217, 15, 0.6);
  font-weight: bold;
}

.terminal-content :deep(.danger) {
  color: #ff073a;
  text-shadow: 0 0 10px rgba(255, 7, 58, 0.6);
  font-weight: bold;
}

.terminal-content :deep(.success) {
  color: #39ff14;
  text-shadow: 0 0 10px rgba(57, 255, 20, 0.6);
  font-weight: bold;
}
</style>