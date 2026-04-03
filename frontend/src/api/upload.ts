import request from '@/utils/request'
import type { AxiosProgressEvent } from 'axios'

export const uploadApi = {
  // Upload lobster package
  uploadLobster(
    file: File,
    data: {
      name: string
      description: string
      readme: string
      tags: string[]
      version: string
    },
    onProgress?: (progress: { loaded: number; total: number; percentage: number }) => void
  ): Promise<{ id: string; url: string }> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('data', JSON.stringify(data))

    return request.post('/upload/lobster', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (onProgress && progressEvent.total) {
          const loaded = progressEvent.loaded
          const total = progressEvent.total
          const percentage = Math.round((loaded * 100) / total)
          onProgress({ loaded, total, percentage })
        }
      }
    })
  },

  // Validate lobster config
  validateConfig(configFile: string): Promise<{
    valid: boolean
    errors?: string[]
    warnings?: string[]
  }> {
    return request.post('/upload/validate', { config: configFile })
  },

  // Get upload URL for large files (presigned URL)
  getUploadUrl(filename: string, contentType: string): Promise<{
    uploadUrl: string
    downloadUrl: string
  }> {
    return request.post('/upload/url', { filename, contentType })
  }
}
