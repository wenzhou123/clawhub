import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

// Format number with K/M/B suffix
export function formatNumber(num: number): string {
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1) + 'B'
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// Format file size
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Format date to relative time
export function formatRelativeTime(date: string | Date): string {
  return dayjs(date).fromNow()
}

// Format date
export function formatDate(date: string | Date, format = 'YYYY-MM-DD HH:mm'): string {
  return dayjs(date).format(format)
}

// Format version
export function formatVersion(version: string): string {
  return version.startsWith('v') ? version : `v${version}`
}

// Truncate text
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

// Parse DockerHub-style name
export function parseLobsterName(fullName: string): { namespace: string; name: string } {
  const parts = fullName.split('/')
  if (parts.length === 2) {
    return { namespace: parts[0], name: parts[1] }
  }
  return { namespace: 'library', name: parts[0] }
}

// Build DockerHub-style name
export function buildLobsterName(namespace: string, name: string): string {
  if (namespace === 'library') {
    return name
  }
  return `${namespace}/${name}`
}
