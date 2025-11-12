// src/api/http.js
import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求缓存和限流
const requestCache = new Map()
const requestTimestamps = new Map()

function getCacheKey(config) {
  if (/\/(get|query)$/.test(config.url)) return '';

  const paramsStr = config.params && typeof config.params === 'string' ? config.params : JSON.stringify(config.params || {})
  const dataStr = config.data && typeof config.data === 'string' ? config.data : JSON.stringify(config.data || {})
  return `${config.method}-${config.url}-${paramsStr}-${dataStr}`
}

// 请求拦截器
http.interceptors.request.use(config => {
  // 请求限流 - 3秒内相同请求只发送一次
  const requestKey = getCacheKey(config)
  if (requestKey) {
    const now = Date.now()
    const lastRequestTime = requestTimestamps.get(requestKey) || 0

    if (now - lastRequestTime < 3000 && !config.ignoreRateLimit) {
      const cachedResponse = requestCache.get(requestKey)
      if (cachedResponse) {
        return Promise.reject({
          config,
          response: { data: cachedResponse },
          isRateLimited: true
        })
      }
    }

    requestTimestamps.set(requestKey, now)
  }

  return config
})

// 响应拦截器
http.interceptors.response.use(
  response => {
    if (response.data?.errcode) {
      return Promise.reject(response.data?.errdetail || response.data?.errmsg || new Error('服务器错误'))
    }

    const ret = response.data?.ret || {}

    // 缓存响应
    const config = response.config
    const requestKey = getCacheKey(config)
    requestKey && requestCache.set(requestKey, ret)

    return ret
  },
  error => {
    // 处理被限流的请求
    if (error.isRateLimited) {
      console.log('Rate limited request:', error.config.url)
      return error.response.data
    }

    console.error('API Error:', error)

    // 处理401未授权错误
    if (error.status === 401) {
      // 避免在登录页面时重复跳转导致死循环
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }

    // 处理不同的错误状态码
    if (error.response) {
      return Promise.reject(error.response.data || new Error('服务器错误'))
    }

    // 网络错误
    if (!error.response) {
      return Promise.reject(new Error('网络连接已断开'))
    }

    return Promise.reject(error)
  }
)

// 创建资源请求函数
export function resource(path, options = { method: 'post' }) {
  return function(data = {}) {
    const { method, ...restOptions } = options

    const config = {
      ...restOptions,
      ...data
    }

    return http[method](path, config)
  }
}

export default http
