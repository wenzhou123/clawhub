<template>
  <div class="pagination-container">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="pageSizes"
      :total="total"
      :layout="layout"
      :background="background"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: number
  pageSize: number
  total: number
  pageSizes?: number[]
  layout?: string
  background?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  pageSizes: () => [10, 20, 50, 100],
  layout: 'total, sizes, prev, pager, next, jumper',
  background: true
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
  'update:pageSize': [value: number]
  'change': [page: number, pageSize: number]
}>()

const currentPage = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleSizeChange = (size: number) => {
  emit('update:pageSize', size)
  emit('change', 1, size)
}

const handleCurrentChange = (page: number) => {
  emit('change', page, pageSize.value)
}
</script>

<style scoped lang="scss">
.pagination-container {
  display: flex;
  justify-content: center;
  padding: var(--claw-spacing-md) 0;
}
</style>
