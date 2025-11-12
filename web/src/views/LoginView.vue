<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import anime from 'animejs'

const router = useRouter()
const userStore = useUserStore()
const mobile = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!mobile.value || !password.value) {
    errorMessage.value = '请输入手机号和密码'
    return
  }

  // 简单的手机号格式验证
  // const mobileRegex = /^1[3-9]\d{9}$/
  // if (!mobileRegex.test(mobile.value)) {
  //   errorMessage.value = '请输入正确的手机号格式'
  //   return
  // }

  isLoading.value = true
  errorMessage.value = ''

  try {
    await userStore.login(mobile.value, password.value)

    // 登录成功动画
    anime({
      targets: '.login-form',
      scale: [1, 1.05, 1],
      duration: 300,
      complete: () => {
        router.push('/home')
      }
    })
  } catch (error) {
    errorMessage.value = error.message || '登录失败，请检查手机号和密码'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  // 页面进入动画
  anime.timeline()
    .add({
      targets: '.login-header',
      translateY: [-50, 0],
      opacity: [0, 1],
      duration: 800,
      easing: 'easeOutQuart'
    })
    .add({
      targets: '.login-form',
      translateY: [30, 0],
      opacity: [0, 1],
      duration: 600,
      easing: 'easeOutQuart'
    }, '-=400')
    .add({
      targets: '.login-footer',
      opacity: [0, 1],
      duration: 400,
      easing: 'easeOutQuart'
    }, '-=200')
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-white to-gray-50 flex flex-col">
    <!-- Header -->
    <div class="login-header pt-16 pb-8 px-6 text-center opacity-0">
      <div class="relative">
        <h1 class="text-6xl font-black text-gray-900 mb-2 font-display">
          Bank
        </h1>
        <div class="text-4xl font-black text-gradient mb-4 font-display">
          Book
        </div>
        <p class="text-sm text-gray-500 font-light tracking-wide">
          CREDIT CARD MANAGEMENT
        </p>
      </div>

      <!-- 装饰性图形 -->
      <div class="absolute top-20 right-8 w-24 h-24 bg-gradient-to-br from-purple-100 to-purple-200 rounded-full opacity-60"></div>
      <div class="absolute top-32 left-6 w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full opacity-40"></div>
    </div>

    <!-- Login Form -->
    <div class="login-form flex-1 px-6 opacity-0">
      <div class="p-8 mb-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 font-body">
          登录账户
        </h2>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- 错误提示 -->
          <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600 flex items-center">
              <i class="fas fa-exclamation-circle mr-2"></i>
              {{ errorMessage }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              手机号码
            </label>
            <div class="relative">
              <i class="fas fa-phone absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
              <input
                v-model="mobile"
                type="tel"
                placeholder="请输入手机号码"
                class="input-field pl-12 border-0 outline-none focus:outline-none focus:ring-0 focus:border-transparent"
                maxlength="11"
                @input="errorMessage = ''"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              登录密码
            </label>
            <div class="relative">
              <i class="fas fa-lock absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
              <input
                v-model="password"
                type="password"
                placeholder="请输入登录密码"
                class="input-field pl-12 border-0 outline-none focus:outline-none focus:ring-0 focus:border-transparent"
                @input="errorMessage = ''"
              />
            </div>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full btn-primary py-4 text-lg font-semibold relative overflow-hidden"
            :class="{ 'opacity-70 cursor-not-allowed': isLoading }"
          >
            <span v-if="!isLoading">登录</span>
            <span v-else class="flex items-center justify-center">
              <i class="fas fa-spinner fa-spin mr-2"></i>
              登录中...
            </span>
          </button>
        </form>

        <div class="mt-6 text-center">
          <a href="#" class="text-sm text-purple-600 hover:text-purple-700">
            忘记密码？
          </a>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="login-footer px-6 pb-8 text-center opacity-0">
      <p class="text-xs text-gray-400">
        © 2025 Bank Book. All rights reserved.
      </p>
    </div>
  </div>
</template>

<style scoped>
.text-gradient {
  background: linear-gradient(135deg, #161615 0%, #5751D5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
