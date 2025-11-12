// 针对滚动阻塞事件默认设置 passive: true（不覆盖显式 passive:false）
const passiveEvents = ['touchstart', 'touchmove', 'wheel', 'mousewheel']

const originalAddEventListener = EventTarget.prototype.addEventListener

EventTarget.prototype.addEventListener = function (type, listener, options) {
  let opts = options

  if (passiveEvents.includes(type)) {
    if (typeof options === 'undefined') {
      opts = { passive: true }
    } else if (typeof options === 'boolean') {
      // boolean 表示 capture
      opts = { capture: options, passive: true }
    } else if (typeof options === 'object' && options !== null && !('passive' in options)) {
      // 仅在未显式声明 passive 时补齐
      opts = { ...options, passive: true }
    }
  }

  return originalAddEventListener.call(this, type, listener, opts)
}