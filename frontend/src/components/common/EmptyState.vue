<template>
  <div class="empty-state" :class="{ 'compact': compact }">
    <div class="empty-icon">
      <slot name="icon">
        <el-icon :size="iconSize"><SearchEmpty /></el-icon>
      </slot>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-description">{{ description }}</p>
    <div class="empty-action" v-if="$slots.action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Search } from '@element-plus/icons-vue'

interface Props {
  title: string
  description?: string
  icon?: any
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  description: '',
  compact: false
})

const SearchEmpty = props.icon || Search
const iconSize = props.compact ? 32 : 64
</script>

<style scoped lang="scss">
.empty-state {
  @include flex-center;
  flex-direction: column;
  padding: var(--claw-spacing-xl);
  text-align: center;

  &.compact {
    padding: var(--claw-spacing-md);

    .empty-icon {
      margin-bottom: var(--claw-spacing-sm);
    }

    .empty-title {
      font-size: 1rem;
    }

    .empty-description {
      font-size: 0.875rem;
    }
  }
}

.empty-icon {
  @include flex-center;
  width: 100px;
  height: 100px;
  background: var(--claw-bg-tertiary);
  border-radius: 50%;
  margin-bottom: var(--claw-spacing-md);
  color: var(--claw-text-tertiary);
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--claw-text-primary);
  margin-bottom: var(--claw-spacing-sm);
}

.empty-description {
  font-size: 1rem;
  color: var(--claw-text-secondary);
  margin-bottom: var(--claw-spacing-md);
  max-width: 400px;
}

.empty-action {
  margin-top: var(--claw-spacing);
}
</style>
