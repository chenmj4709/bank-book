import { resource } from './http.js'

// 刷卡类型管理API
export const getSwipeTypes = resource('/category/swipe-types', { method: 'get' })
export const addSwipeType = resource('/category/swipe-type')
export const updateSwipeType = (typeId, data) => {
  return resource(`/category/swipe-type/${typeId}`, { method: 'put' })(data)
}
export const deleteSwipeType = (typeId) => {
  return resource(`/category/swipe-type/${typeId}`, { method: 'delete' })()
}

// 消费类型管理API
export const getConsumptionTypes = resource('/category/consumption-types', { method: 'get' })
export const addConsumptionType = resource('/category/consumption-type')
export const updateConsumptionType = (typeId, data) => {
  return resource(`/category/consumption-type/${typeId}`, { method: 'put' })(data)
}
export const deleteConsumptionType = (typeId) => {
  return resource(`/category/consumption-type/${typeId}`, { method: 'delete' })()
}
