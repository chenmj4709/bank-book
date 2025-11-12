import { resource } from './http.js'

// 消费记录管理API
export const getRecords = resource('/record/list', { method: 'get' })
export const addRecord = resource('/record/add')
export const updateRecord = (recordId, data) => {
  return resource(`/record/update/${recordId}`, { method: 'put' })(data)
}
export const deleteRecord = (recordId) => {
  return resource(`/record/delete/${recordId}`, { method: 'delete' })()
}
export const getStats = resource('/record/stats', { method: 'get' })
export const getRecentConsumptions = resource('/record/recent-consumptions', { method: 'get' })
