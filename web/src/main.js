// 顶部引入补丁，确保在任何库初始化前生效
import './utils/patchPassiveEvents'
import './assets/main.css'
import '@fortawesome/fontawesome-free/css/all.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
])

import App from './App.vue'
import router from './router'
import { useUserStore } from './stores/user'

const app = createApp(App)

app.component('v-chart', ECharts)
app.use(createPinia())
app.use(router)

// 初始化用户状态
const userStore = useUserStore()
userStore.initUser()

app.mount('#app')
