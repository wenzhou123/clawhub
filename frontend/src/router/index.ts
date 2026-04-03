import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// Configure NProgress
NProgress.configure({ showSpinner: false })

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/home/index.vue'),
      meta: { title: 'Home' }
    },
    {
      path: '/explore',
      name: 'Explore',
      component: () => import('@/views/home/index.vue'),
      meta: { title: 'Explore' }
    },
    {
      path: '/lobsters',
      name: 'LobsterList',
      component: () => import('@/views/lobster/list.vue'),
      meta: { title: 'Lobsters' }
    },
    {
      path: '/lobsters/:namespace/:name',
      name: 'LobsterDetail',
      component: () => import('@/views/lobster/detail.vue'),
      meta: { title: 'Lobster Detail' }
    },
    {
      path: '/tags/:tag',
      name: 'TagDetail',
      component: () => import('@/views/search/tag.vue'),
      meta: { title: 'Tag' }
    },
    {
      path: '/search',
      name: 'Search',
      component: () => import('@/views/search/index.vue'),
      meta: { title: 'Search' }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/user/login.vue'),
      meta: { title: 'Login', guestOnly: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/user/register.vue'),
      meta: { title: 'Register', guestOnly: true }
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: () => import('@/views/user/forgot-password.vue'),
      meta: { title: 'Forgot Password', guestOnly: true }
    },
    {
      path: '/upload',
      name: 'Upload',
      component: () => import('@/views/upload/index.vue'),
      meta: { title: 'Upload Lobster', requiresAuth: true }
    },
    {
      path: '/user/:username',
      name: 'UserProfile',
      component: () => import('@/views/user/profile.vue'),
      meta: { title: 'User Profile' }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/user/settings.vue'),
      meta: { title: 'Settings', requiresAuth: true }
    },
    {
      path: '/stars',
      name: 'MyStars',
      component: () => import('@/views/user/stars.vue'),
      meta: { title: 'My Stars', requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/error/404.vue'),
      meta: { title: 'Page Not Found' }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0, behavior: 'smooth' }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  // Start progress bar
  NProgress.start()

  const userStore = useUserStore()

  // Fetch user info if token exists but user is not loaded
  if (userStore.token && !userStore.user) {
    await userStore.fetchUserInfo()
  }

  // Check auth requirements
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
    return
  }

  // Check guest only pages (login, register)
  if (to.meta.guestOnly && userStore.isLoggedIn) {
    next('/')
    return
  }

  // Set page title
  const appTitle = import.meta.env.VITE_APP_TITLE || 'ClawHub'
  document.title = to.meta.title ? `${to.meta.title} - ${appTitle}` : appTitle

  next()
})

router.afterEach(() => {
  // Finish progress bar
  NProgress.done()
})

export default router
