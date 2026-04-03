<template>
  <div class="lobster-list-page">
    <div class="page-header">
      <h1>Lobsters</h1>
      <el-button type="primary" @click="$router.push('/upload')">
        <el-icon><Plus /></el-icon>
        发布 Lobster
      </el-button>
    </div>

    <div class="filter-bar">
      <el-input
        v-model="filters.query"
        placeholder="搜索..."
        clearable
        style="width: 300px"
        @keyup.enter="handleSearch"
      />
      <el-select v-model="filters.sort" placeholder="排序" @change="handleSearch">
        <el-option label="最近更新" value="updated_at" />
        <el-option label="最多 Star" value="stars" />
        <el-option label="最多下载" value="downloads" />
        <el-option label="名称" value="name" />
      </el-select>
      <el-select v-model="filters.order" placeholder="顺序" @change="handleSearch">
        <el-option label="降序" value="desc" />
        <el-option label="升序" value="asc" />
      </el-select>
    </div>

    <LobsterCardList :lobsters="lobsters" :loading="loading" />

    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import LobsterCardList from '@/components/lobster/LobsterCardList.vue'
import type { Lobster } from '@/types'

const loading = ref(false)
const lobsters = ref<Lobster[]>([])

const filters = ref({
  query: '',
  sort: 'updated_at',
  order: 'desc',
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
})

const handleSearch = () => {
  loading.value = true
  // TODO: Call API
  setTimeout(() => {
    lobsters.value = Array(8).fill(null).map((_, i) => ({
      id: `lobster-${i}`,
      namespace: 'demo',
      name: `lobster-${i}`,
      full_name: `demo/lobster-${i}`,
      description: '这是一个示例 Lobster 描述',
      star_count: Math.floor(Math.random() * 100),
      download_count: Math.floor(Math.random() * 1000),
      version_count: Math.floor(Math.random() * 10) + 1,
      latest_version: '1.0.0',
      tags: ['engineering'],
      owner_username: 'demo-user',
      created_at: new Date().toISOString(),
    }))
    pagination.value.total = 100
    loading.value = false
  }, 500)
}

onMounted(handleSearch)
</script>

<style scoped lang="scss">
.lobster-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.pagination {
  margin-top: 32px;
  display: flex;
  justify-content: center;
}
</style>
