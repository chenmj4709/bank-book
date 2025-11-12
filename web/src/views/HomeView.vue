<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import anime from 'animejs'
import { getDashboard } from '@/api/home'

const router = useRouter()
const userStore = useUserStore()

// 退出登录
const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    await userStore.logout()

    router.push('/login')
  }
}

const cards = ref([])

// 计算属性
const totalLimit = computed(() => cards.value.reduce((sum, card) => sum + card.limit, 0))
const totalUsed = computed(() => cards.value.reduce((sum, card) => sum + card.used, 0))
const totalAvailable = computed(() => totalLimit.value - totalUsed.value)

// 图表配置
const chartOption = ref({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: ¥{c} ({d}%)',
    // 关闭交互触发，避免额外监听器
    triggerOn: 'none'
  },
  legend: {
    bottom: '0',
    textStyle: { color: '#666' }
  },
  series: [
    {
      name: '刷卡类型',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: [],
      // 禁用该系列的交互
      silent: true
    }
  ]
})

// 获取首页数据
const fetchDashboard = async () => {
  try {
    const res = await getDashboard()
    cards.value = (res.cards || []).map(c => ({
      id: c.id,
      bank: c.bank,
      color: c.color,
      lastFour: c.lastFour,
      limit: c.limit,
      used: c.used,
      billDate: c.billDate,
      paymentDate: c.paymentDate,
      lastPaymentDate: c.lastPaymentDate,
      usedBySwipeTypes: c.usedBySwipeTypes || []
    }))

    const pieData = (res.consumption || []).map(item => ({
      value: item.amount,
      name: item.name,
      itemStyle: { color: item.color }
    }))
    if (pieData.length) {
      chartOption.value.series[0].data = pieData
    }
  } catch (e) {
    console.error('获取首页数据失败:', e)
  }
}

const navigateTo = (path) => {
  router.push(path)
}

onMounted(async () => {
  await fetchDashboard()
  // 页面进入动画
  anime.timeline()
    .add({
      targets: '.home-header',
      translateY: [-30, 0],
      opacity: [0, 1],
      duration: 600,
      easing: 'easeOutQuart'
    })
    .add({
      targets: '.stats-card',
      translateY: [40, 0],
      opacity: [0, 1],
      duration: 500,
      delay: anime.stagger(100),
      easing: 'easeOutQuart'
    }, '-=300')
    .add({
      targets: '.bento-header',
      scale: [0.9, 1],
      opacity: [0, 1],
      duration: 400,
      delay: anime.stagger(90),
      easing: 'easeOutBack'
    }, '-=300')
    .add({
      targets: '.bento-item',
      scale: [0.9, 1],
      opacity: [0, 1],
      duration: 400,
      delay: anime.stagger(80),
      easing: 'easeOutBack'
    }, '-=200')
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="home-header bg-white px-6 py-6 opacity-0">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 font-body">
            信用卡管理
          </h1>
          <p class="text-sm text-gray-500">CREDIT MANAGEMENT</p>
        </div>
        <div class="flex items-center space-x-2">
          <button @click="handleLogout" class="p-3 bg-red-100 rounded-full hover:bg-red-200 transition-colors">
            <i class="fas fa-sign-out-alt text-red-600"></i>
          </button>
          <button @click="navigateTo('/manage')" class="p-3 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors">
            <i class="fas fa-cog text-gray-600"></i>
          </button>
        </div>
      </div>

      <!-- 总览统计 -->
      <div class="grid grid-cols-2 gap-4">
        <div class="stats-card text-center opacity-0">
          <div class="text-2xl font-black text-gray-900 font-display">
            ¥{{ (totalLimit / 10000).toFixed(2) }}W
          </div>
          <p class="text-xs text-gray-500 mt-1">总额度</p>
        </div>
        <div class="stats-card text-center opacity-0">
          <div class="text-2xl font-black text-green-600 font-display">
            ¥{{ (totalAvailable / 10000).toFixed(2) }}W
          </div>
          <p class="text-xs text-gray-500 mt-1">可用额度</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="px-6 pb-24">
      <!-- Bento Grid Layout -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <!-- 消费分析图表 -->
        <div class="bento-item col-span-2 py-6 opacity-0">
          <div class="flex items-center justify-between mb-4 px-2">
            <h3 class="text-lg font-bold text-gray-900 font-body">消费分析</h3>
            <span class="text-xs text-gray-500">按类型</span>
          </div>
          <div class="h-48">
            <v-chart :option="chartOption" class="w-full h-full chart-touch" />
          </div>
        </div>

        <!-- 快速记录 -->
        <div class="bento-item opacity-0" @click="navigateTo('/record')">
          <div class="text-center">
            <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <i class="fas fa-plus text-purple-600 text-xl"></i>
            </div>
            <p class="text-sm font-medium text-gray-900">快速记录</p>
            <p class="text-xs text-gray-500 mt-1">QUICK ADD</p>
          </div>
        </div>

        <!-- 本月消费 -->
        <div class="bento-item opacity-0">
          <div class="text-center">
            <div class="text-3xl font-black text-gray-900 font-display flex items-center justify-center min-h-12 mb-3">
              ¥{{ (totalUsed / 1000).toFixed(1) }}K
            </div>
            <p class="text-sm font-medium text-gray-500">本月消费</p>
            <p class="text-xs text-gray-400 mt-1">MONTHLY</p>
          </div>
        </div>
      </div>

      <!-- 信用卡列表 -->
      <div class="space-y-4">
        <h3 class="bento-header text-lg font-bold text-gray-900 font-body px-2 opacity-0">我的信用卡</h3>

        <div v-for="card in cards" :key="card.id" class="bento-item card p-5 opacity-0">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <div :class="`w-10 h-10 bg-gradient-to-br ${card.color} rounded-lg flex items-center justify-center mr-3`">
                <i class="fas fa-credit-card text-white"></i>
              </div>
              <div>
                <h4 class="font-bold text-gray-900">{{ card.bank }}</h4>
                <p class="text-sm text-gray-500">**** {{ card.lastFour }}</p>
              </div>
            </div>
            <div class="text-right">
              <div class="text-lg font-black text-gray-900 font-display">
                ¥{{ ((card.limit - card.used) / 1000).toFixed(1) }}K
              </div>
              <p class="text-xs text-gray-500">可用额度</p>
            </div>
          </div>

          <!-- 进度条 -->
          <div class="mb-1">
            <div class="flex justify-between text-xs text-gray-500 mb-1">
              <span>已用 ¥{{ (card.used / 1000).toFixed(1) }}K</span>
              <span>总额 ¥{{ (card.limit / 1000).toFixed(1) }}K</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                class="flex h-2 transition-all duration-500"
                :style="{ width: `${Math.min(100, ((card.used || 0) / (card.limit || 1)) * 100)}%` }"
              >
                <div
                  v-for="(seg, idx) in card.usedBySwipeTypes || []"
                  :key="idx"
                  class="h-2"
                  :style="{
                    width: `${((seg.amount || 0) / (card.used || 1)) * 100}%`,
                    backgroundColor: colorForType(seg.name, idx)
                  }"
                ></div>
              </div>
            </div>
          </div>

          <!-- 新增：各刷卡类型占用 -->
          <div class="grid grid-cols-2 gap-3 mt-1">
            <div
              v-for="item in card.usedBySwipeTypes"
              :key="`${card.id}-${item.name}`"
              class="flex justify-between text-xs bg-gray-100 rounded py-1"
            >
              <span class="text-gray-600">{{ item.name }}</span>
              <span class="text-gray-900 font-medium">¥{{ (item.amount / 1000).toFixed(1) }}K</span>
            </div>
          </div>

          <div class="flex items-center justify-between text-xs text-gray-500 mt-1 space-x-2">
            <span>
              本月账单
              <span class="text-gray-900 font-medium">¥{{ Number(card.monthlyBill || 0).toFixed(2) }}</span>
            </span>
            <span>•</span>
            <span>
              本月待还
              <span class="text-gray-900 font-medium">¥{{ Number(card.monthlyOutstanding || 0).toFixed(2) }}</span>
            </span>
            <span>•</span>
            <span>
              还款剩余
              <span class="text-gray-900 font-medium">{{ card.daysToPayment ?? '-' }}</span>
              天
            </span>
          </div>

          <!-- 重要日期 -->
          <div class="grid grid-cols-2 gap-4 text-xs mt-3">
            <div class="text-center p-2 bg-gray-200/50 rounded-lg">
              <p class="text-gray-500">账单日</p>
              <p class="font-bold text-gray-900">{{ card.billDate }}号</p>
            </div>
            <div class="text-center p-2 bg-red-50 rounded-lg">
              <p class="text-red-500">还款日</p>
              <p class="font-bold text-red-600">{{ card.paymentDate }}号</p>
              <p v-if="card.lastPaymentDate && card.lastPaymentDate != card.paymentDate" class="text-xs text-red-500 mt-1">
                最迟还款日 {{ card.lastPaymentDate }}号
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <div class="fixed bottom-0 left-1/2 transform -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-200 px-6 py-4">
      <div class="flex justify-around">
        <button class="flex flex-col items-center text-purple-600">
          <i class="fas fa-home text-xl mb-1"></i>
          <span class="text-xs">首页</span>
        </button>
        <button @click="navigateTo('/record')" class="flex flex-col items-center text-gray-400">
          <i class="fas fa-plus-circle text-xl mb-1"></i>
          <span class="text-xs">记录</span>
        </button>
        <button @click="navigateTo('/manage')" class="flex flex-col items-center text-gray-400">
          <i class="fas fa-cog text-xl mb-1"></i>
          <span class="text-xs">管理</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bento-item {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.bento-item:hover {
  transform: translateY(-2px);
}

.chart-touch {
  /* 告诉浏览器允许纵向滚动手势，提高滚动性能 */
  touch-action: pan-y;
}
</style>

<script>
const palette = [
  '#5751D5', '#3B82F6', '#22C55E', '#F59E0B', '#EF4444',
  '#A855F7', '#10B981', '#3B82F6', '#84CC16', '#06B6D4',
  '#D946EF', '#F97316', '#EAB308', '#5751D5'
]

function colorForType(name, idx) {
  if (!name) return palette[idx % palette.length]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) >>> 0
  }
  return palette[hash % palette.length]
}
</script>
