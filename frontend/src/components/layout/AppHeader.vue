<template>
  <header class="app-header">
    <div class="header-container">
      <!-- Logo -->
      <router-link to="/" class="logo">
        <span class="logo-icon">🦞</span>
        <span class="logo-text">ClawHub</span>
      </router-link>

      <!-- Navigation -->
      <nav class="nav-links">
        <router-link to="/explore">探索</router-link>
        <router-link to="/lobsters">Lobsters</router-link>
        <router-link to="/search">搜索</router-link>
      </nav>

      <!-- Search -->
      <div class="header-search">
        <el-input
          v-model="searchQuery"
          placeholder="搜索..."
          prefix-icon="Search"
          size="small"
          clearable
          @keyup.enter="handleSearch"
        />
      </div>

      <!-- Actions -->
      <div class="header-actions">
        <el-button
          v-if="userStore.isLoggedIn"
          type="primary"
          size="small"
          @click="$router.push('/upload')"
        >
          <el-icon><Plus /></el-icon>
          发布
        </el-button>

        <el-dropdown v-if="userStore.isLoggedIn" trigger="click">
          <el-avatar
            :size="32"
            :src="userStore.user?.avatar_url"
            class="user-avatar"
          >
            {{ userStore.user?.username?.[0]?.toUpperCase() }}
          </el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push(`/user/${userStore.user?.username}`)">
                个人主页
              </el-dropdown-item>
              <el-dropdown-item @click="$router.push('/stars')">
                我的 Star
              </el-dropdown-item>
              <el-dropdown-item @click="$router.push('/settings')">
                设置
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <template v-else>
          <el-button link @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" @click="$router.push('/login')">注册</el-button>
        </template>

        <!-- Theme Toggle -->
        <el-button
          link
          class="theme-toggle"
          @click="themeStore.toggleTheme"
        >
          <el-icon v-if="themeStore.isDark"><Sunny /></el-icon>
          <el-icon v-else><Moon /></el-icon>
        </el-button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Sunny, Moon } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const searchQuery = ref('')

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      path: '/search',
      query: { q: searchQuery.value },
    })
  }
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped lang="scss">
.app-header {
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: inherit;
  
  .logo-icon {
    font-size: 32px;
  }
  
  .logo-text {
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
}

.nav-links {
  display: flex;
  gap: 24px;
  
  a {
    color: var(--el-text-color-regular);
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      color: var(--el-color-primary);
    }
    
    &.router-link-active {
      color: var(--el-color-primary);
    }
  }
}

.header-search {
  flex: 1;
  max-width: 400px;
  
  :deep(.el-input__wrapper) {
    border-radius: 20px;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  cursor: pointer;
  border: 2px solid var(--el-border-color);
  
  &:hover {
    border-color: var(--el-color-primary);
  }
}

.theme-toggle {
  font-size: 18px;
}
</style>
