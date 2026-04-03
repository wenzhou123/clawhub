<template>
  <div v-if="loading" class="loading-container">
    <el-skeleton v-for="i in 4" :key="i" animated>
      <template #template>
        <el-skeleton-item variant="card" style="height: 140px" />
      </template>
    </el-skeleton>
  </div>
  
  <div v-else-if="lobsters.length === 0" class="empty-container">
    <el-empty description="暂无数据" />
  </div>
  
  <div v-else class="lobster-grid">
    <LobsterCard
      v-for="lobster in lobsters"
      :key="lobster.id"
      :lobster="lobster"
    />
  </div>
</template>

<script setup lang="ts">
import LobsterCard from './LobsterCard.vue'
import type { Lobster } from '@/types'

defineProps<{
  lobsters: Lobster[]
  loading?: boolean
}>()
</script>

<style scoped lang="scss">
.loading-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.empty-container {
  padding: 60px 0;
}

.lobster-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
</style>
