import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getSwipeTypes,
  addSwipeType as addSwipeTypeApi,
  updateSwipeType as updateSwipeTypeApi,
  deleteSwipeType as deleteSwipeTypeApi,
  getConsumptionTypes,
  addConsumptionType as addConsumptionTypeApi,
  updateConsumptionType as updateConsumptionTypeApi,
  deleteConsumptionType as deleteConsumptionTypeApi
 } from '@/api/category'

export const useCategoryStore = defineStore('category', () => {
  const swipeTypes = ref([])
  const consumptionTypes = ref([])
  const loading = ref(false)

  // 获取刷卡类型列表
  const fetchSwipeTypes = async () => {
    loading.value = true
    try {
      const response = await getSwipeTypes()
      swipeTypes.value = response || []
      return { success: true, data: response }
    } catch (error) {
      console.error('获取刷卡类型列表错误:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 添加刷卡类型
  const addSwipeType = async (typeData) => {
    try {
      const response = await addSwipeTypeApi(typeData)
      await fetchSwipeTypes() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('添加刷卡类型错误:', error)
      throw error
    }
  }

  // 更新刷卡类型
  const updateSwipeType = async (typeId, typeData) => {
    try {
      const response = await updateSwipeTypeApi(typeId, typeData)
      await fetchSwipeTypes() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('更新刷卡类型错误:', error)
      throw error
    }
  }

  // 删除刷卡类型
  const deleteSwipeType = async (typeId) => {
    try {
      const response = await deleteSwipeTypeApi(typeId)
      await fetchSwipeTypes() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('删除刷卡类型错误:', error)
      throw error
    }
  }

  // 获取消费类型列表
  const fetchConsumptionTypes = async () => {
    loading.value = true
    try {
      const response = await getConsumptionTypes()
      consumptionTypes.value = response || []
      return { success: true, data: response }
    } catch (error) {
      console.error('获取消费类型列表错误:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 添加消费类型
  const addConsumptionType = async (typeData) => {
    try {
      const response = await addConsumptionTypeApi(typeData)
      await fetchConsumptionTypes() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('添加消费类型错误:', error)
      throw error
    }
  }

  // 更新消费类型
  const updateConsumptionType = async (typeId, typeData) => {
    try {
      const response = await updateConsumptionTypeApi(typeId, typeData)
      await fetchConsumptionTypes() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('更新消费类型错误:', error)
      throw error
    }
  }

  // 删除消费类型
  const deleteConsumptionType = async (typeId) => {
    try {
      const response = await deleteConsumptionTypeApi(typeId)
      await fetchConsumptionTypes() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('删除消费类型错误:', error)
      throw error
    }
  }

  return {
    swipeTypes,
    consumptionTypes,
    loading,
    fetchSwipeTypes,
    addSwipeType,
    updateSwipeType,
    deleteSwipeType,
    fetchConsumptionTypes,
    addConsumptionType,
    updateConsumptionType,
    deleteConsumptionType
  }
})
