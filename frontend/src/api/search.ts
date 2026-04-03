import request from '@/utils/request'
import type { Lobster, SearchResult, SearchFilters } from '@/types'

export const searchApi = {
  // Search lobsters
  search(
    query: string,
    filters: SearchFilters = {},
    params: { page?: number; pageSize?: number } = {}
  ): Promise<SearchResult> {
    return request.get('/search', {
      params: {
        q: query,
        ...filters,
        ...params
      }
    })
  },

  // Get search suggestions
  getSuggestions(query: string, limit: number = 5): Promise<string[]> {
    return request.get('/search/suggestions', {
      params: { q: query, limit },
      headers: { 'X-Silent': 'true' }
    })
  },

  // Get popular tags
  getPopularTags(limit: number = 20): Promise<{ name: string; count: number }[]> {
    return request.get('/tags/popular', { params: { limit } })
  },

  // Get lobsters by tag
  getLobstersByTag(
    tag: string,
    params: { page?: number; pageSize?: number } = {}
  ): Promise<SearchResult> {
    return request.get(`/tags/${tag}/lobsters`, { params })
  },

  // Get trending searches
  getTrendingSearches(): Promise<string[]> {
    return request.get('/search/trending')
  }
}
