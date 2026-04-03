import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Lobster, LobsterDetail, CreateLobsterRequest, PaginatedResponse } from '@/types'
import { lobsterApi } from '@/api/lobster'
import { ElMessage } from 'element-plus'

export const useLobsterStore = defineStore('lobster', () => {
  // State
  const lobsters = ref<Lobster[]>([])
  const currentLobster = ref<LobsterDetail | null>(null)
  const popularLobsters = ref<Lobster[]>([])
  const officialLobsters = ref<Lobster[]>([])
  const starredLobsters = ref<Lobster[]>([])
  const loading = ref(false)
  const pagination = ref({
    total: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  })

  // Getters
  const hasMore = computed(() => pagination.value.page < pagination.value.totalPages)
  
  // Actions
  const fetchLobsters = async (params: {
    page?: number
    pageSize?: number
    sort?: string
    type?: string
  } = {}) => {
    loading.value = true
    try {
      const response = await lobsterApi.getLobsters(params)
      lobsters.value = response.items
      pagination.value = {
        total: response.total,
        page: response.page,
        pageSize: response.pageSize,
        totalPages: response.totalPages
      }
      return response
    } finally {
      loading.value = false
    }
  }

  const fetchLobsterDetail = async (namespace: string, name: string) => {
    loading.value = true
    try {
      const response = await lobsterApi.getLobster(namespace, name)
      currentLobster.value = response
      return response
    } finally {
      loading.value = false
    }
  }

  const fetchPopularLobsters = async (limit: number = 10) => {
    try {
      const response = await lobsterApi.getPopularLobsters(limit)
      popularLobsters.value = response
      return response
    } catch (error) {
      return []
    }
  }

  const fetchOfficialLobsters = async (params: { page?: number; pageSize?: number } = {}) => {
    try {
      const response = await lobsterApi.getOfficialLobsters(params)
      officialLobsters.value = response.items
      return response
    } catch (error) {
      return null
    }
  }

  const fetchStarredLobsters = async (params: { page?: number; pageSize?: number } = {}) => {
    try {
      const response = await lobsterApi.getStarredLobsters(params)
      starredLobsters.value = response.items
      return response
    } catch (error) {
      return null
    }
  }

  const createLobster = async (data: CreateLobsterRequest) => {
    loading.value = true
    try {
      const response = await lobsterApi.createLobster(data)
      ElMessage.success('Lobster created successfully')
      return response
    } finally {
      loading.value = false
    }
  }

  const updateLobster = async (id: string, data: Partial<CreateLobsterRequest>) => {
    loading.value = true
    try {
      const response = await lobsterApi.updateLobster(id, data)
      if (currentLobster.value?.id === id) {
        currentLobster.value = { ...currentLobster.value, ...response }
      }
      ElMessage.success('Lobster updated successfully')
      return response
    } finally {
      loading.value = false
    }
  }

  const deleteLobster = async (id: string) => {
    loading.value = true
    try {
      await lobsterApi.deleteLobster(id)
      lobsters.value = lobsters.value.filter(l => l.id !== id)
      if (currentLobster.value?.id === id) {
        currentLobster.value = null
      }
      ElMessage.success('Lobster deleted successfully')
      return true
    } finally {
      loading.value = false
    }
  }

  const toggleStar = async (namespace: string, name: string) => {
    try {
      const response = await lobsterApi.toggleStar(namespace, name)
      
      // Update current lobster if matches
      if (currentLobster.value?.author.username === namespace && currentLobster.value?.name === name) {
        currentLobster.value.stars = response.stars
      }
      
      // Update in lists
      const updateInList = (list: Lobster[]) => {
        const item = list.find(l => l.author.username === namespace && l.name === name)
        if (item) {
          item.stars = response.stars
        }
      }
      
      updateInList(lobsters.value)
      updateInList(popularLobsters.value)
      updateInList(officialLobsters.value)
      
      ElMessage.success(response.starred ? 'Starred' : 'Unstarred')
      return response
    } catch (error) {
      return null
    }
  }

  const clearCurrentLobster = () => {
    currentLobster.value = null
  }

  return {
    lobsters,
    currentLobster,
    popularLobsters,
    officialLobsters,
    starredLobsters,
    loading,
    pagination,
    hasMore,
    fetchLobsters,
    fetchLobsterDetail,
    fetchPopularLobsters,
    fetchOfficialLobsters,
    fetchStarredLobsters,
    createLobster,
    updateLobster,
    deleteLobster,
    toggleStar,
    clearCurrentLobster
  }
})
