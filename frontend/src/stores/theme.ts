import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import type { Theme } from '@/types'

export const useThemeStore = defineStore('theme', () => {
  // State
  const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'auto')
  const systemDark = ref(false)

  // Getters
  const isDark = computed(() => {
    if (theme.value === 'auto') {
      return systemDark.value
    }
    return theme.value === 'dark'
  })

  const currentTheme = computed(() => {
    if (theme.value === 'auto') {
      return systemDark.value ? 'dark' : 'light'
    }
    return theme.value
  })

  // Actions
  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  const toggleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'auto']
    const currentIndex = themes.indexOf(theme.value)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex])
  }

  const applyTheme = () => {
    const html = document.documentElement
    const isDarkMode = isDark.value

    if (isDarkMode) {
      html.classList.add('dark')
      html.setAttribute('data-theme', 'dark')
    } else {
      html.classList.remove('dark')
      html.setAttribute('data-theme', 'light')
    }
  }

  const initSystemListener = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    systemDark.value = mediaQuery.matches

    mediaQuery.addEventListener('change', (e) => {
      systemDark.value = e.matches
      if (theme.value === 'auto') {
        applyTheme()
      }
    })
  }

  const init = () => {
    initSystemListener()
    applyTheme()
  }

  // Watch for theme changes
  watch(theme, applyTheme)

  return {
    theme,
    isDark,
    currentTheme,
    setTheme,
    toggleTheme,
    init
  }
})
