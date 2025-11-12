<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRecordStore } from '@/stores/record'

const router = useRouter()
const recordStore = useRecordStore()
const loadMoreRef = ref(null)
let observer = null

const hasMore = computed(() => {
  return recordStore.records.length < recordStore.pagination.total
})

const initList = async () => {
  recordStore.resetRecords()
  await recordStore.fetchRecords()
}

const loadMore = async () => {
  if (recordStore.loading) return
  if (!hasMore.value) return
  await recordStore.loadMoreRecords()
}

const handleDelete = async (recordId, index) => {
  if (!confirm('确认删除该记录吗？')) return
  const res = await recordStore.deleteRecord(recordId)
  if (res.success) {
    recordStore.records.splice(index, 1)
    recordStore.pagination.total = Math.max(0, recordStore.pagination.total - 1)
  } else {
    alert(res.message || '删除失败')
  }
}

onMounted(async () => {
  await initList()

  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) loadMore()
    })
  }, { root: null, rootMargin: '0px', threshold: 1.0 })

  if (loadMoreRef.value) observer.observe(loadMoreRef.value)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <button @click="router.back()" class="p-2 -ml-2">
            <i class="fas fa-arrow-left text-gray-600 text-xl"></i>
          </button>
          <h1 class="text-lg font-bold text-gray-900 font-body">消费记录</h1>
        </div>
        <button @click="router.push('/record')" class="p-2 rounded-lg bg-purple-100 hover:bg-purple-200">
          <i class="fas fa-plus text-purple-700"></i>
        </button>
      </div>
    </div>

    <div class="px-6 py-4 space-y-3">
      <div
        v-for="(item, idx) in recordStore.records"
        :key="item.id"
        class="p-4 bg-white rounded-lg shadow-sm flex items-start justify-between"
      >
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-900">{{ item.consumption_type_name || '未知类型' }}</span>
            <span class="text-xs text-gray-400">
              {{ (item.trade_date || item.created_at) ? new Date(item.trade_date || item.created_at).toLocaleString() : '' }}
            </span>
          </div>
          <div class="text-xs text-gray-500 mt-1">
            <span>{{ item.card_bank || '' }}</span>
            <span v-if="item.card_number"> • **** {{ String(item.card_number).slice(-4) }}</span>
          </div>
        </div>
        <div class="text-right">
          <div class="text-base font-bold text-gray-900">¥{{ Number(item.amount || 0).toFixed(2) }}</div>
          <button
            class="mt-2 text-xs text-red-600 hover:text-red-700"
            @click="handleDelete(item.id, idx)"
          >
            删除
          </button>
        </div>
      </div>

      <div ref="loadMoreRef" class="py-6 text-center text-xs text-gray-400">
        <span v-if="recordStore.loading">加载中...</span>
        <span v-else-if="hasMore">上滑加载更多</span>
        <span v-else>没有更多了</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
