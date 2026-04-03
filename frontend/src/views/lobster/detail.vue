<template>
  <div v-if="lobster" class="lobster-detail-page">
    <!-- Header -->
    <div class="detail-header">
      <div class="header-main">
        <div class="lobster-icon">🦞</div>
        <div class="lobster-info">
          <h1 class="lobster-name">
            <router-link :to="`/user/${lobster.namespace}`">{{ lobster.namespace }}</router-link>
            <span class="separator">/</span>
            <span>{{ lobster.name }}</span>
          </h1>
          <p class="lobster-description">{{ lobster.description }}</p>
          <div class="lobster-meta">
            <el-tag v-for="tag in lobster.tags" :key="tag" size="small">
              {{ tag }}
            </el-tag>
            <span class="meta-item">
              <el-icon><Star /></el-icon>
              {{ formatNumber(lobster.star_count) }}
            </span>
            <span class="meta-item">
              <el-icon><Download /></el-icon>
              {{ formatNumber(lobster.download_count) }}
            </span>
            <span class="meta-item">
              <el-icon><Timer /></el-icon>
              {{ formatDate(lobster.updated_at) }}
            </span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-button
          :type="lobster.is_starred ? 'warning' : 'default'"
          @click="toggleStar"
        >
          <el-icon><Star /></el-icon>
          {{ lobster.is_starred ? '已 Star' : 'Star' }}
        </el-button>
        <el-button type="primary">
          <el-icon><Download /></el-icon>
          Pull
        </el-button>
      </div>
    </div>

    <el-row :gutter="24">
      <!-- Main Content -->
      <el-col :xs="24" :lg="18">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="README" name="readme">
            <div class="readme-content" v-html="renderedReadme"></div>
          </el-tab-pane>
          <el-tab-pane label="版本" name="versions">
            <el-table :data="versions" style="width: 100%">
              <el-table-column prop="version" label="版本" width="120" />
              <el-table-column prop="description" label="描述" />
              <el-table-column prop="created_at" label="发布时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button type="primary" link>
                    <el-icon><Download /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="文件" name="files">
            <div class="files-list">
              <div class="file-item">
                <el-icon><Document /></el-icon>
                <span>SOUL.md</span>
              </div>
              <div class="file-item">
                <el-icon><Document /></el-icon>
                <span>AGENTS.md</span>
              </div>
              <div class="file-item">
                <el-icon><Document /></el-icon>
                <span>IDENTITY.md</span>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- Pull Command -->
        <div class="pull-section">
          <div class="pull-label">快速拉取</div>
          <div class="pull-command">
            <code>claw pull {{ lobster.full_name }}:{{ lobster.latest_version }}</code>
            <el-button type="primary" link @click="copyPullCommand">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
        </div>
      </el-col>

      <!-- Sidebar -->
      <el-col :xs="24" :lg="6">
        <div class="sidebar">
          <el-card>
            <template #header>
              <span>所有者</span>
            </template>
            <div class="owner-info">
              <el-avatar :size="48" :src="lobster.owner_avatar" />
              <div class="owner-details">
                <router-link :to="`/user/${lobster.owner_username}`">
                  {{ lobster.owner_username }}
                </router-link>
              </div>
            </div>
          </el-card>

          <el-card style="margin-top: 16px">
            <template #header>
              <span>统计</span>
            </template>
            <div class="stats-list">
              <div class="stat-row">
                <span>版本数</span>
                <strong>{{ lobster.version_count }}</strong>
              </div>
              <div class="stat-row">
                <span>Stars</span>
                <strong>{{ lobster.star_count }}</strong>
              </div>
              <div class="stat-row">
                <span>下载</span>
                <strong>{{ lobster.download_count }}</strong>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, Download, Timer, Document, CopyDocument } from '@element-plus/icons-vue'
import type { Lobster, LobsterVersion } from '@/types'
import { formatNumber, formatDate } from '@/utils/format'

const route = useRoute()
const activeTab = ref('readme')
const lobster = ref<Lobster | null>(null)
const versions = ref<LobsterVersion[]>([])

const renderedReadme = computed(() => {
  // TODO: Render markdown
  return '<p>README content will be rendered here...</p>'
})

const toggleStar = () => {
  if (lobster.value) {
    lobster.value.is_starred = !lobster.value.is_starred
    lobster.value.star_count += lobster.value.is_starred ? 1 : -1
    ElMessage.success(lobster.value.is_starred ? '已 Star' : '已取消 Star')
  }
}

const copyPullCommand = () => {
  const cmd = `claw pull ${lobster.value?.full_name}:${lobster.value?.latest_version}`
  navigator.clipboard.writeText(cmd)
  ElMessage.success('已复制')
}

onMounted(() => {
  const { namespace, name } = route.params
  // TODO: Fetch from API
  lobster.value = {
    id: '1',
    namespace: namespace as string,
    name: name as string,
    full_name: `${namespace}/${name}`,
    description: '这是一个功能强大的 AI Agent 配置，可以帮助你完成各种任务。',
    readme: '# README',
    is_public: true,
    tags: ['engineering', 'ai', 'assistant'],
    star_count: 128,
    download_count: 1024,
    version_count: 5,
    latest_version: '1.2.0',
    owner_id: 'user-1',
    owner_username: namespace as string,
    owner_avatar: '',
    is_starred: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  
  versions.value = [
    { id: 'v1', version: '1.2.0', description: 'Latest release', created_at: new Date().toISOString() },
    { id: 'v2', version: '1.1.0', description: 'Bug fixes', created_at: new Date(Date.now() - 86400000).toISOString() },
    { id: 'v3', version: '1.0.0', description: 'Initial release', created_at: new Date(Date.now() - 172800000).toISOString() },
  ]
})
</script>

<style scoped lang="scss">
.lobster-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--el-border-color);
}

.header-main {
  display: flex;
  gap: 16px;
}

.lobster-icon {
  font-size: 48px;
}

.lobster-name {
  font-size: 24px;
  margin: 0 0 8px;
  
  a {
    color: var(--el-color-primary);
    text-decoration: none;
  }
  
  .separator {
    margin: 0 4px;
    color: var(--el-text-color-secondary);
  }
}

.lobster-description {
  color: var(--el-text-color-regular);
  margin: 0 0 12px;
}

.lobster-meta {
  display: flex;
  gap: 16px;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.pull-section {
  margin-top: 24px;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.pull-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.pull-command {
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  code {
    font-family: monospace;
    font-size: 14px;
  }
}

.sidebar {
  .owner-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .stats-list {
    .stat-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid var(--el-border-color-lighter);
      
      &:last-child {
        border-bottom: none;
      }
    }
  }
}

.files-list {
  .file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    
    &:hover {
      background: var(--el-fill-color-light);
    }
  }
}
</style>
