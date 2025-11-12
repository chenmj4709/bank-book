import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  login as loginApi,
  logout as logoutApi,
  getUser as getUserApi
} from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)

  // 登录
  const login = async (mobile, password) => {
    try {
      const response = await loginApi({ mobile, password })

      user.value = response
      isLoggedIn.value = true

      return { success: true, data: response }
    } catch (error) {
      console.error('登录错误:', error)
      throw error
    }
  }

  // 退出登录
  const logout = async () => {
    try {
      await logoutApi()
    } catch (error) {
      console.error('退出登录错误:', error)
    } finally {
      // 清除本地数据
      user.value = null
      isLoggedIn.value = false
    }
  }

  // 获取用户信息
  const initUser = async () => {
    try {
      const response = await getUserApi()
      user.value = response
      isLoggedIn.value = true
    } catch (error) {
      console.error('获取用户信息错误:', error)
      throw error
    }
  }

  return {
    user,
    isLoggedIn,
    login,
    logout,
    initUser
  }
})
