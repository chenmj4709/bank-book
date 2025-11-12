import { resource } from './http.js'

// 用户相关API
export const login = resource('/user/login')
export const logout = resource('/user/logout')
export const getUser = resource('/user/get')
