<template>
  <div class="tag-page">
    <h1>Tag: {{ tag }}</h1>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const tag = computed(() => route.params.tag)
</script>
