import request from '@/utils/request'
import type { 
  Lobster, 
  LobsterDetail, 
  CreateLobsterRequest, 
  PaginatedResponse,
  SearchFilters 
} from '@/types'

export const lobsterApi = {
  // Get lobster list
  getLobsters(params: {
    page?: number
    pageSize?: number
    sort?: string
    type?: string
  } = {}): Promise<PaginatedResponse<Lobster>> {
    return request.get('/lobsters', { params })
  },

  // Get lobster detail
  getLobster(namespace: string, name: string): Promise<LobsterDetail> {
    return request.get(`/lobsters/${namespace}/${name}`)
  },

  // Create lobster
  createLobster(data: CreateLobsterRequest): Promise<Lobster> {
    return request.post('/lobsters', data)
  },

  // Update lobster
  updateLobster(id: string, data: Partial<CreateLobsterRequest>): Promise<Lobster> {
    return request.put(`/lobsters/${id}`, data)
  },

  // Delete lobster
  deleteLobster(id: string): Promise<void> {
    return request.delete(`/lobsters/${id}`)
  },

  // Star/Unstar lobster
  toggleStar(namespace: string, name: string): Promise<{ starred: boolean; stars: number }> {
    return request.post(`/lobsters/${namespace}/${name}/star`)
  },

  // Get user's starred lobsters
  getStarredLobsters(params: {
    page?: number
    pageSize?: number
  } = {}): Promise<PaginatedResponse<Lobster>> {
    return request.get('/lobsters/starred', { params })
  },

  // Get popular lobsters
  getPopularLobsters(limit: number = 10): Promise<Lobster[]> {
    return request.get('/lobsters/popular', { params: { limit } })
  },

  // Get official lobsters
  getOfficialLobsters(params: {
    page?: number
    pageSize?: number
  } = {}): Promise<PaginatedResponse<Lobster>> {
    return request.get('/lobsters/official', { params })
  },

  // Get lobster readme
  getReadme(namespace: string, name: string, version?: string): Promise<string> {
    return request.get(`/lobsters/${namespace}/${name}/readme`, {
      params: { version },
      headers: { 'X-Silent': 'true' }
    })
  },

  // Get lobster config
  getConfig(namespace: string, name: string, version?: string): Promise<string> {
    return request.get(`/lobsters/${namespace}/${name}/config`, {
      params: { version },
      headers: { 'X-Silent': 'true' }
    })
  },

  // Download lobster
  downloadLobster(namespace: string, name: string, version?: string): Promise<Blob> {
    return request.get(`/lobsters/${namespace}/${name}/download`, {
      params: { version },
      responseType: 'blob'
    })
  }
}
