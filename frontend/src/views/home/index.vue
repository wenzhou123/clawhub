<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="logo-icon">🦞</span>
          ClawHub
        </h1>
        <p class="hero-subtitle">
          OpenClaw 的容器注册中心 - 发现、分享和分发你的 AI Agent 配置
        </p>
        <div class="hero-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索 Lobsters..."
            size="large"
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-value">{{ stats.lobsters }}</span>
            <span class="stat-label">Lobsters</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.downloads }}</span>
            <span class="stat-label">下载</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.users }}</span>
            <span class="stat-label">用户</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Trending Section -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><TrendCharts /></el-icon>
          趋势
        </h2>
        <el-link type="primary" @click="$router.push('/explore')">
          查看更多
        </el-link>
      </div>
      <LobsterCardList :lobsters="trending" :loading="loading" />
    </section>

    <!-- Popular Section -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><Star /></el-icon>
          热门
        </h2>
        <el-link type="primary" @click="$router.push('/explore')">
          查看更多
        </el-link>
      </div>
      <LobsterCardList :lobsters="popular" :loading="loading" />
    </section>

    <!-- Categories -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><Collection /></el-icon>
          分类
        </h2>
      </div>
      <div class="categories">
        <el-card
          v-for="cat in categories"
          :key="cat.name"
          class="category-card"
          shadow="hover"
          @click="handleCategoryClick(cat.tag)"
        >
          <div class="category-icon">{{ cat.icon }}</div>
          <div class="category-name">{{ cat.name }}</div>
          <div class="category-count">{{ cat.count }} 个</div>
        </el-card>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, TrendCharts, Star, Collection } from '@element-plus/icons-vue'
import LobsterCardList from '@/components/lobster/LobsterCardList.vue'
import type { Lobster } from '@/types'

const router = useRouter()
const searchQuery = ref('')
const loading = ref(false)
const trending = ref<Lobster[]>([])
const popular = ref<Lobster[]>([])

const stats = ref({
  lobsters: '1.2k',
  downloads: '50k',
  users: '500+',
})

const categories = [
  { name: '工程开发', icon: '💻', tag: 'engineering', count: 350 },
  { name: '设计创意', icon: '🎨', tag: 'design', count: 180 },
  { name: '营销推广', icon: '📢', tag: 'marketing', count: 220 },
  { name: '产品设计', icon: '📊', tag: 'product', count: 120 },
  { name: '游戏开发', icon: '🎮', tag: 'game', count: 150 },
  { name: '学术研究', icon: '📚', tag: 'academic', count: 80 },
]

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      path: '/search',
      query: { q: searchQuery.value },
    })
  }
}

const handleCategoryClick = (tag: string) => {
  router.push({
    path: '/search',
    query: { tags: tag },
  })
}

// Mock data for demo
onMounted(() => {
  loading.value = true
  setTimeout(() => {
    trending.value = Array(4).fill(null).map((_, i) => ({
      id: `trend-${i}`,
      namespace: 'demo',
      name: `trending-lobster-${i}`,
      full_name: `demo/trending-lobster-${i}`,
      description: '这是一个示例 Lobster 描述',
      star_count: 100 - i * 10,
      download_count: 500 - i * 50,
      version_count: 5,
      latest_version: '1.0.0',
      tags: ['engineering', 'ai'],
      owner_username: 'demo-user',
      created_at: new Date().toISOString(),
    }))
    
    popular.value = Array(4).fill(null).map((_, i) => ({
      id: `pop-${i}`,
      namespace: 'demo',
      name: `popular-lobster-${i}`,
      full_name: `demo/popular-lobster-${i}`,
      description: '这是一个热门的 Lobster',
      star_count: 200 - i * 20,
      download_count: 1000 - i * 100,
      version_count: 10,
      latest_version: '2.0.0',
      tags: ['design', 'ux'],
      owner_username: 'demo-user',
      created_at: new Date().toISOString(),
    }))
    loading.value = false
  }, 500)
})
</script>

<style scoped lang="scss">
.home-page {
  padding-bottom: 40px;
}

.hero {
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
  margin-bottom: 40px;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.logo-icon {
  font-size: 56px;
}

.hero-subtitle {
  font-size: 20px;
  opacity: 0.9;
  margin-bottom: 32px;
}

.hero-actions {
  max-width: 600px;
  margin: 0 auto 32px;
}

.search-input {
  :deep(.el-input__wrapper) {
    background: white;
    border-radius: 8px;
    padding: 4px;
  }
  
  :deep(.el-input__inner) {
    font-size: 16px;
    height: 48px;
  }
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.section {
  max-width: 1200px;
  margin: 0 auto 40px;
  padding: 0 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.category-card {
  cursor: pointer;
  text-align: center;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-4px);
  }
}

.category-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.category-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.category-count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
