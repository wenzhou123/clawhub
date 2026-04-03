<template>
  <div class="loading-state" :class="{ 'fullscreen': fullscreen }">
    <el-icon class="loading-icon" :size="iconSize"><Loading /></el-icon>
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

interface Props {
  text?: string
  fullscreen?: boolean
  size?: 'small' | 'default' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  fullscreen: false,
  size: 'default'
})

const iconSize = {
  small: 24,
  default: 40,
  large: 64
}[props.size]
</script>

<style scoped lang="scss">
.loading-state {
  @include flex-center;
  flex-direction: column;
  padding: var(--claw-spacing-xl);

  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(var(--claw-bg-primary), 0.9);
    z-index: 2000;
  }
}

.loading-icon {
  color: var(--claw-primary);
  animation: rotate 1s linear infinite;
}

.loading-text {
  margin-top: var(--claw-spacing);
  color: var(--claw-text-secondary);
  font-size: 0.875rem;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
