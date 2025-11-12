import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import RecordView from '../views/RecordView.vue'
import ManageView from '../views/ManageView.vue'
import RecordListView from '../views/RecordListView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView
    },
    {
      path: '/record',
      name: 'record',
      component: RecordView
    },
    {
      path: '/records',
      name: 'records',
      component: RecordListView
    },
    {
      path: '/manage',
      name: 'manage',
      component: ManageView
    }
  ]
})

export default router
