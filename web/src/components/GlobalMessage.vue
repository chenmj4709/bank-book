<script setup>
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useMessageStore } from '@/stores/message'

const messageStore = useMessageStore()
const { visible, text, type } = storeToRefs(messageStore)

const bgColorMap = {
  success: 'bg-green-500',
  info: 'bg-blue-500',
  warning: 'bg-yellow-500',
  error: 'bg-red-500'
}

const iconMap = {
  success: 'fa-check',
  info: 'fa-info-circle',
  warning: 'fa-exclamation-triangle',
  error: 'fa-exclamation-circle'
}

const containerClass = computed(() =>
  `fixed top-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-lg text-white z-50 ${
    bgColorMap[type.value]
  }`
)

const iconClass = computed(() =>
  `fas ${iconMap[type.value]} mr-2`
)
</script>

<template>
  <div v-if="visible" :class="containerClass">
    <i :class="iconClass"></i>
    {{ text }}
  </div>
</template>
