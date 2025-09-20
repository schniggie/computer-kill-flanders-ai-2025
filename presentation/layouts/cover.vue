<template>
  <div class="slidev-layout cover relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 opacity-20">
      <div class="matrix-rain"></div>
    </div>
    
    <!-- Nuclear power plant silhouette -->
    <div class="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-gray-900 to-transparent opacity-60"></div>
    
    <!-- Logo in top-right corner -->
    <div class="absolute top-4 right-4 w-32 h-32 z-10">
      <img 
        src="/assets/drehergroup-logo_enhanced.png" 
        alt="Dreher Group" 
        class="w-full h-full object-contain drop-shadow-lg"
        style="filter: drop-shadow(0 0 10px rgba(57, 255, 20, 0.5));"
      />
    </div>
    
    <!-- Main content -->
    <div class="flex flex-col justify-center items-center h-full px-16 relative z-10">
      <!-- Terminal-style header -->
      <div class="terminal-header mb-8 w-full max-w-2xl">
        <div class="flex items-center space-x-2 text-sm text-green-400 mb-2">
          <span class="text-red-400">●</span>
          <span class="text-yellow-400">●</span>  
          <span class="text-green-400">●</span>
          <span class="ml-4 font-mono">homer@nuclear-plant:~$</span>
          <span class="cursor">_</span>
        </div>
      </div>
      
      <!-- Main content slot -->
      <div class="text-center space-y-6 max-w-4xl">
        <slot />
      </div>
    </div>
    
    <!-- Bottom status bar -->
    <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-80 text-green-400 text-xs font-mono p-2 flex justify-between">
      <span>STATUS: PWNED</span>
      <span>ATOM CLOCK: {{ new Date().toLocaleTimeString() }}</span>
      <span>USER: HOMER</span>
    </div>
  </div>
</template>

<style scoped>
/* Terminal window styling */
.terminal-header {
  background: #1a1a1a;
  border: 1px solid var(--slidev-theme-primary);
  border-radius: 8px 8px 0 0;
  padding: 8px 12px;
  box-shadow: 0 0 20px rgba(57, 255, 20, 0.2);
}

/* Matrix rain effect */
.matrix-rain {
  background-image: 
    linear-gradient(0deg, transparent 24%, rgba(57, 255, 20, 0.05) 25%, rgba(57, 255, 20, 0.05) 26%, transparent 27%, transparent 74%, rgba(57, 255, 20, 0.05) 75%, rgba(57, 255, 20, 0.05) 76%, transparent 77%, transparent);
  animation: matrix-scroll 20s linear infinite;
  height: 200%;
}

@keyframes matrix-scroll {
  0% { transform: translateY(-50%); }
  100% { transform: translateY(0%); }
}

/* Glowing kbd styling */
kbd {
  box-shadow: 0 0 5px rgba(57, 255, 20, 0.5);
  border: 1px solid var(--slidev-theme-primary);
}
</style>
