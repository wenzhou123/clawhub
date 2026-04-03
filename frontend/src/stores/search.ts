import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Lobster, SearchFilters, SearchResult } from '@/types'
import { searchApi } from '@/api/search'

export const useSearchStore = defineStore('search', () => {
  // State
  const query = ref('')
  const results = ref<Lobster[]>([])
  const suggestions = ref<string[]>([])
  const popularTags = ref<{ name: string; count: number }[]>([])
  const trendingSearches = ref<string[]>([])
  const loading = ref(false)
  const filters = ref<SearchFilters>({
    sortBy: 'relevance',
    type: 'all',
    tags: []
  })
  const pagination = ref({
    total: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  })
  const searchHistory = ref<string[]>(JSON.parse(localStorage.getItem('searchHistory') || '[]'))

  // Getters
  const hasResults = computed(() => results.value.length > 0)
  const hasMore = computed(() => pagination.value.page < pagination.value.totalPages)

  // Actions
  const search = async (searchQuery: string, newFilters?: SearchFilters, page: number = 1) => {
    if (!searchQuery.trim()) {
      results.value = []
      return null
    }

    loading.value = true
    query.value = searchQuery
    
    if (newFilters) {
      filters.value = { ...filters.value, ...newFilters }
    }

    try {
      const response = await searchApi.search(
        searchQuery,
        filters.value,
        { page, pageSize: pagination.value.pageSize }
      )
      
      if (page === 1) {
        results.value = response.lobsters
      } else {
        results.value.push(...response.lobsters)
      }
      
      pagination.value = {
        total: response.total,
        page: response.page,
        pageSize: response.pageSize,
        totalPages: Math.ceil(response.total / response.pageSize)
      }

      // Add to search history
      addToHistory(searchQuery)

      return response
    } finally {
      loading.value = false
    }
  }

  const loadMore = async () => {
    if (!hasMore.value || loading.value) return
    await search(query.value, undefined, pagination.value.page + 1)
  }

  const fetchSuggestions = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      suggestions.value = []
      return
    }

    try {
      const response = await searchApi.getSuggestions(searchQuery)
      suggestions.value = response
    } catch (error) {
      suggestions.value = []
    }
  }

  const fetchPopularTags = async (limit: number = 20) => {
    try {
      const response = await searchApi.getPopularTags(limit)
      popularTags.value = response
    } catch (error) {
      popularTags.value = []
    }
  }

  const fetchTrendingSearches = async () => {
    try {
      const response = await searchApi.getTrendingSearches()
      trendingSearches.value = response
    } catch (error) {
      trendingSearches.value = []
    }
  }

  const addToHistory = (searchQuery: string) => {
    // Remove if exists
    searchHistory.value = searchHistory.value.filter(h => h !== searchQuery)
    // Add to front
    searchHistory.value.unshift(searchQuery)
    // Keep only last 10
    searchHistory.value = searchHistory.value.slice(0, 10)
    // Save to localStorage
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
  }

  const removeFromHistory = (searchQuery: string) => {
    searchHistory.value = searchHistory.value.filter(h => h !== searchQuery)
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
  }

  const clearHistory = () => {
    searchHistory.value = []
    localStorage.removeItem('searchHistory')
  }

  const setFilters = (newFilters: SearchFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {
      sortBy: 'relevance',
      type: 'all',
      tags: []
    }
  }

  const clearResults = () => {
    results.value = []
    query.value = ''
  }

  return {
    query,
    results,
    suggestions,
    popularTags,
    trendingSearches,
    loading,
    filters,
    pagination,
    searchHistory,
    hasResults,
    hasMore,
    search,
    loadMore,
    fetchSuggestions,
    fetchPopularTags,
    fetchTrendingSearches,
    addToHistory,
    removeFromHistory,
    clearHistory,
    setFilters,
    clearFilters,
    clearResults
  }
})
