import { resource } from './http.js'

export const getDashboard = resource('/home/dashboard', { method: 'get' })