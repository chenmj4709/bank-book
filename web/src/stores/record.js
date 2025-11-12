import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getRecords,
  addRecord as addRecordApi,
  updateRecord as updateRecordApi,
  deleteRecord as deleteRecordApi,
  getStats
 } from '@/api/record'

export const useRecordStore = defineStore('record', () => {
  const records = ref([])
  const stats = ref({})
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0
  })

  // 获取消费记录列表
  const fetchRecords = async (filters = {}, { append = false } = {}) => {
    loading.value = true
    try {
      const params = {
        page: pagination.value.page,
        page_size: pagination.value.limit,
        ...filters
      }
      const response = await getRecords({ params })
      const list = response.list || []
      if (append) {
        records.value = [...records.value, ...list]
      } else {
        records.value = list
      }
      pagination.value.total = response.total || 0
      return { success: true, data: response }
    } catch (error) {
      console.error('获取消费记录列表错误:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 添加消费记录
  const addRecord = async (recordData) => {
    try {
      const response = await addRecordApi(recordData)
      await fetchRecords() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('添加消费记录错误:', error)
      throw error
    }
  }

  // 更新消费记录
  const updateRecord = async (recordId, recordData) => {
    try {
      const response = await updateRecordApi(recordId, recordData)
      await fetchRecords() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('更新消费记录错误:', error)
      throw error
    }
  }

  // 删除消费记录
  const deleteRecord = async (recordId) => {
    try {
      const response = await deleteRecordApi(recordId)
      return { success: true, data: response }
    } catch (error) {
      console.error('删除消费记录错误:', error)
      throw error
    }
  }

  // 获取消费统计
  const fetchStats = async (filters = {}) => {
    try {
      const response = await getStats({ params: filters })
      stats.value = response
      return { success: true, data: response }
    } catch (error) {
      console.error('获取消费统计错误:', error)
      throw error
    }
  }

  // 设置分页
  const setPagination = (page, limit) => {
    pagination.value.page = page
    pagination.value.limit = limit
  }

  const resetRecords = () => {
    records.value = []
    pagination.value.page = 1
    pagination.value.total = 0
  }

  const loadMoreRecords = async (filters = {}) => {
    if (loading.value) return
    const loaded = records.value.length
    const hasMore = loaded < pagination.value.total
    if (!hasMore) return
    pagination.value.page += 1
    return fetchRecords(filters, { append: true })
  }

  return {
    records,
    stats,
    loading,
    pagination,
    fetchRecords,
    addRecord,
    updateRecord,
    deleteRecord,
    fetchStats,
    setPagination,
    resetRecords,
    loadMoreRecords
  }
})
