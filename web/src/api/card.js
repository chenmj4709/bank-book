import { resource } from './http.js'

// 信用卡管理API
export const getCards = resource('/card/list', { method: 'get' })
export const addCard = resource('/card/add')
export const updateCard = (cardId, data) => {
  return resource(`/card/update/${cardId}`, { method: 'put' })(data)
}
export const deleteCard = (cardId) => {
  return resource(`/card/delete/${cardId}`, { method: 'delete' })()
}
export const getCardDetail = (cardId) => {
  return resource(`/card/detail/${cardId}`, { method: 'get' })()
}
