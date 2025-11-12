import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMessageStore = defineStore('message', () => {
  const visible = ref(false)
  const text = ref('')
  const type = ref('success')
  let timer = null

  const show = (msg, msgType = 'success', duration = 3000) => {
    text.value = msg
    type.value = msgType
    visible.value = true

    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      visible.value = false
      timer = null
    }, duration)
  }

  const success = (msg, duration = 3000) => show(msg, 'success', duration)
  const info = (msg, duration = 3000) => show(msg, 'info', duration)
  const warning = (msg, duration = 3000) => show(msg, 'warning', duration)
  const error = (msg, duration = 3000) => show(msg, 'error', duration)
  const hide = () => {
    visible.value = false
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  return {
    visible,
    text,
    type,
    show,
    success,
    info,
    warning,
    error,
    hide
  }
})
