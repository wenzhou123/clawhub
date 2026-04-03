// User Types
export interface User {
  id: string
  username: string
  email: string
  avatar?: string
  bio?: string
  createdAt: string
  updatedAt: string
}

export interface UserProfile extends User {
  lobstersCount: number
  downloadsCount: number
  starsCount: number
}

export interface LoginCredentials {
  email: string
  password: string
  remember?: boolean
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
  confirmPassword: string
}

// Lobster (Agent) Types
export interface Lobster {
  id: string
  name: string
  description: string
  readme?: string
  version: string
  author: User
  tags: string[]
  downloads: number
  stars: number
  isOfficial: boolean
  isVerified: boolean
  configFile: string
  createdAt: string
  updatedAt: string
}

export interface LobsterDetail extends Lobster {
  versions: LobsterVersion[]
  dependencies?: string[]
  usageCount: number
  dockerfile?: string
}

export interface LobsterVersion {
  version: string
  createdAt: string
  changelog?: string
}

export interface CreateLobsterRequest {
  name: string
  description: string
  readme: string
  tags: string[]
  configFile: string
  version: string
}

// Search Types
export interface SearchFilters {
  sortBy?: 'relevance' | 'downloads' | 'stars' | 'updated' | 'newest'
  type?: 'all' | 'official' | 'verified' | 'community'
  tags?: string[]
}

export interface SearchResult {
  lobsters: Lobster[]
  total: number
  page: number
  pageSize: number
}

// API Response Types
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// Upload Types
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

// Theme Types
export type Theme = 'light' | 'dark' | 'auto'
