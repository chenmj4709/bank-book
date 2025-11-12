<template>
  <div v-if="visible" class="fixed inset-0 bg-black/65 backdrop-blur-xs z-50 flex items-center justify-center">
    <!-- 背景遮罩 -->
    <div
      class="absolute inset-0"
      @click="handleClose"
    ></div>

    <!-- 模态框内容 -->
    <div class="relative bg-white rounded-2xl shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-hidden">
      <!-- 头部 -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h3 class="text-lg font-bold text-gray-900">{{ title }}</h3>
        <button
          @click="handleClose"
          class="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- 内容区域 -->
      <div class="p-6 overflow-y-auto">
        <slot></slot>
      </div>

      <!-- 底部按钮 -->
      <div v-if="showFooter" class="flex justify-end space-x-3 p-6 border-t border-gray-200">
        <button
          @click="handleClose"
          class="px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          取消
        </button>
        <button
          @click="handleConfirm"
          :disabled="loading"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
        >
          <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>
          确定
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '标题'
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'confirm'])

const handleClose = () => {
  emit('close')
}

const handleConfirm = () => {
  emit('confirm')
}

// 监听visible变化，控制body滚动
watch(() => props.visible, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
/* 动画效果 */
.fixed {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.relative {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
