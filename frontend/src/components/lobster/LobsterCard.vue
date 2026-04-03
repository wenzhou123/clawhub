<template>
  <el-card class="lobster-card" shadow="hover" @click="goToDetail">
    <div class="card-header">
      <div class="lobster-icon">🦞</div>
      <div class="lobster-info">
        <h3 class="lobster-name">{{ lobster.full_name }}</h3>
        <p class="lobster-description" :title="lobster.description">
          {{ truncatedDescription }}
        </p>
      </div>
    </div>
    
    <div class="card-footer">
      <div class="stats">
        <span class="stat">
          <el-icon><Star /></el-icon>
          {{ formatNumber(lobster.star_count) }}
        </span>
        <span class="stat">
          <el-icon><Download /></el-icon>
          {{ formatNumber(lobster.download_count) }}
        </span>
      </div>
      <div v-if="lobster.tags?.length" class="tags">
        <el-tag
          v-for="tag in lobster.tags.slice(0, 2)"
          :key="tag"
          size="small"
          effect="plain"
        >
          {{ tag }}
        </el-tag>
      </div>
    </div>
    
    <div v-if="lobster.latest_version" class="version-badge">
      v{{ lobster.latest_version }}
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Star, Download } from '@element-plus/icons-vue'
import type { Lobster } from '@/types'
import { formatNumber } from '@/utils/format'

const props = defineProps<{
  lobster: Lobster
}>()

const router = useRouter()

const truncatedDescription = computed(() => {
  const desc = props.lobster.description || ''
  return desc.length > 60 ? desc.slice(0, 60) + '...' : desc
})

const goToDetail = () => {
  router.push(`/lobsters/${props.lobster.namespace}/${props.lobster.name}`)
}
</script>

<style scoped lang="scss">
.lobster-card {
  cursor: pointer;
  position: relative;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-4px);
  }

  :deep(.el-card__body) {
    padding: 16px;
  }
}

.card-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.lobster-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.lobster-info {
  min-width: 0;
}

.lobster-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--el-color-primary);
}

.lobster-description {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin: 0;
  line-height: 1.4;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats {
  display: flex;
  gap: 12px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.tags {
  display: flex;
  gap: 4px;
}

.version-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 11px;
  padding: 2px 6px;
  background: var(--el-color-success-light-9);
  color: var(--el-color-success);
  border-radius: 4px;
}
</style>
