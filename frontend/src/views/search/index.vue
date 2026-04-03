<template>
  <div class="search-page">
    <h1>搜索结果</h1>
    <p v-if="query">搜索: {{ query }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const query = computed(() => route.query.q)
</script>
