import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { User, LoginCredentials, RegisterCredentials } from '@/types'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)
  const loading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const username = computed(() => user.value?.username || '')
  const avatar = computed(() => user.value?.avatar || '')

  // Actions
  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    try {
      const response = await authApi.login(credentials)
      setToken(response.token)
      user.value = response.user
      ElMessage.success('Login successful')
      return true
    } catch (error) {
      return false
    } finally {
      loading.value = false
    }
  }

  const register = async (credentials: RegisterCredentials) => {
    loading.value = true
    try {
      const response = await authApi.register(credentials)
      setToken(response.token)
      user.value = response.user
      ElMessage.success('Registration successful')
      return true
    } catch (error) {
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      clearToken()
      ElMessage.success('Logged out')
    }
  }

  const fetchUserInfo = async () => {
    if (!token.value) return
    
    try {
      const userInfo = await authApi.getCurrentUser()
      user.value = userInfo
    } catch (error) {
      clearToken()
    }
  }

  const updateProfile = async (data: { bio?: string; avatar?: string }) => {
    try {
      const updated = await authApi.getCurrentUser()
      user.value = updated
      ElMessage.success('Profile updated')
      return true
    } catch (error) {
      return false
    }
  }

  return {
    token,
    user,
    loading,
    isLoggedIn,
    username,
    avatar,
    login,
    register,
    logout,
    fetchUserInfo,
    updateProfile,
    clearToken
  }
})
