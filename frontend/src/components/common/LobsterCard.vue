<template>
  <div class="lobster-card" @click="goToDetail">
    <div class="card-header">
      <div class="lobster-icon">
        <el-icon :size="32"><Box /></el-icon>
      </div>
      <div class="lobster-badges">
        <el-tag v-if="lobster.isOfficial" type="success" size="small">Official</el-tag>
        <el-tag v-if="lobster.isVerified" type="primary" size="small">Verified</el-tag>
      </div>
    </div>

    <h3 class="lobster-name">
      <span class="namespace">{{ lobster.author.username }}</span>
      <span class="separator">/</span>
      <span class="name">{{ lobster.name }}</span>
    </h3>

    <p class="lobster-description">{{ truncatedDescription }}</p>

    <div class="lobster-tags" v-if="lobster.tags.length > 0">
      <el-tag
        v-for="tag in displayedTags"
        :key="tag"
        size="small"
        effect="plain"
        @click.stop="goToTag(tag)"
      >
        {{ tag }}
      </el-tag>
      <el-tag v-if="lobster.tags.length > 3" size="small" effect="plain">
        +{{ lobster.tags.length - 3 }}
      </el-tag>
    </div>

    <div class="card-footer">
      <div class="stats">
        <span class="stat">
          <el-icon><Download /></el-icon>
          {{ formatNumber(lobster.downloads) }}
        </span>
        <span class="stat">
          <el-icon><Star /></el-icon>
          {{ formatNumber(lobster.stars) }}
        </span>
      </div>
      <span class="updated">{{ formatRelativeTime(lobster.updatedAt) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Box, Download, Star } from '@element-plus/icons-vue'
import type { Lobster } from '@/types'
import { formatNumber, formatRelativeTime, truncateText } from '@/utils/format'

interface Props {
  lobster: Lobster
}

const props = defineProps<Props>()
const router = useRouter()

const truncatedDescription = computed(() => {
  return truncateText(props.lobster.description || '', 100)
})

const displayedTags = computed(() => {
  return props.lobster.tags.slice(0, 3)
})

const goToDetail = () => {
  router.push(`/lobsters/${props.lobster.author.username}/${props.lobster.name}`)
}

const goToTag = (tag: string) => {
  router.push(`/tags/${tag}`)
}
</script>

<style scoped lang="scss">
.lobster-card {
  @include card;
  padding: var(--claw-spacing-md);
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;

  &:hover {
    .lobster-name .name {
      color: var(--claw-primary);
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--claw-spacing);
}

.lobster-icon {
  width: 48px;
  height: 48px;
  @include flex-center;
  background: linear-gradient(135deg, var(--claw-primary) 0%, var(--claw-secondary) 100%);
  border-radius: var(--claw-radius);
  color: white;
}

.lobster-badges {
  display: flex;
  gap: var(--claw-spacing-xs);
}

.lobster-name {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: var(--claw-spacing-sm);
  display: flex;
  align-items: center;
  gap: 2px;
  flex-wrap: wrap;

  .namespace {
    color: var(--claw-text-secondary);
    font-weight: 400;
  }

  .separator {
    color: var(--claw-text-tertiary);
  }

  .name {
    color: var(--claw-text-primary);
    transition: color 0.2s;
  }
}

.lobster-description {
  color: var(--claw-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: var(--claw-spacing);
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.lobster-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--claw-spacing-xs);
  margin-bottom: var(--claw-spacing);

  .el-tag {
    cursor: pointer;

    &:hover {
      color: var(--claw-primary);
      border-color: var(--claw-primary);
    }
  }
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--claw-spacing);
  border-top: 1px solid var(--claw-border-light);
}

.stats {
  display: flex;
  gap: var(--claw-spacing);
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--claw-text-tertiary);
  font-size: 0.875rem;

  .el-icon {
    font-size: 14px;
  }
}

.updated {
  font-size: 0.75rem;
  color: var(--claw-text-tertiary);
}
</style>
