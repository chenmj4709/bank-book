import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getCards,
  addCard as addCardApi,
  updateCard as updateCardApi,
  deleteCard as deleteCardApi
} from '@/api/card'

export const useCardStore = defineStore('card', () => {
  const cards = ref([])
  const loading = ref(false)

  // 获取信用卡列表
  const fetchCards = async (params = {}) => {
    loading.value = true
    try {
      const response = await getCards({ params })
      cards.value = response || []
      return { success: true, data: response }
    } catch (error) {
      console.error('获取信用卡列表错误:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 添加信用卡
  const addCard = async (cardData) => {
    try {
      const response = await addCardApi(cardData)
      await fetchCards() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('添加信用卡错误:', error)
      throw error
    }
  }

  // 更新信用卡
  const updateCard = async (cardId, cardData) => {
    try {
      const response = await updateCardApi(cardId, cardData)
      await fetchCards() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('更新信用卡错误:', error)
      throw error
    }
  }

  // 删除信用卡
  const deleteCard = async (cardId) => {
    try {
      const response = await deleteCardApi(cardId)
      await fetchCards() // 重新获取列表
      return { success: true, data: response }
    } catch (error) {
      console.error('删除信用卡错误:', error)
      throw error
    }
  }

  return {
    cards,
    loading,
    fetchCards,
    addCard,
    updateCard,
    deleteCard
  }
})
