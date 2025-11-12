<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import anime from 'animejs'

import { useCategoryStore } from '@/stores/category'
import { useCardStore } from '@/stores/card'
import { useRecordStore } from '@/stores/record'
import { useMessageStore } from '@/stores/message'

const router = useRouter()

// 表单数据
const form = ref({
  card_id: '',
  swipe_type_id: '',
  consumption_type_id: '',
  amount: '',
  trade_date: '',
  record_type: '支付', // 新增：记录类型
  description: ''      // 新增：消费描述
})

// 使用 store 获取数据（替代原来的模拟数据）
const cardStore = useCardStore()
const categoryStore = useCategoryStore()
const recordStore = useRecordStore()
const messageStore = useMessageStore()

const recordTypes = [
  { label: '支付', value: '支付' },
  { label: '还款', value: '还款' }
]

const isPay = computed(() => {
  return form.value.record_type == '支付'
})

// 信用卡：兼容模板的 bank/lastFour 结构
const cards = computed(() => {
  const today = new Date()
  const day = today.getDate()

  const arr = (cardStore.cards || []).map(c => {
    const billDay = Number(c.bill_day || 0)
    const creditLimit = Number(c.credit_limit || 0)
    const highBalance = creditLimit >= 10000
    const pastBill = billDay > 0 && day >= billDay
    const diffToBill = billDay > 0 ? Math.abs(day - billDay) : Number.POSITIVE_INFINITY

    return {
      id: c.id,
      bank: c.bank,
      color: c.color,
      lastFour: c.card_number ? String(c.card_number).slice(-4) : '',
      billDay,
      creditLimit,
      _highBalance: highBalance,
      _pastBill: pastBill,
      _diffToBill: diffToBill
    }
  })

  // 先余额≥1万，其次过账单日；同组内按与账单日的绝对差值升序
  arr.sort((a, b) => {
    if (a._highBalance !== b._highBalance) return a._highBalance ? -1 : 1
    if (a._pastBill !== b._pastBill) return a._pastBill ? -1 : 1
    return a._diffToBill - b._diffToBill
  })

  return arr
})

// 选择信用卡“更多/收起”切换
const showAllCards = ref(false)
const displayedCardsForCards = computed(() => {
  return showAllCards.value ? cards.value : cards.value.slice(0, 2)
})

// 刷卡类型
const swipeTypes = computed(() =>
  (categoryStore.swipeTypes || []).map(t => ({
    id: t.id,
    name: t.name
  }))
)

// 消费类型
const allConsumptionTypes = computed(() =>
  (categoryStore.consumptionTypes || []).map(t => ({
    id: t.id,
    name: t.name
  }))
)

// 最近3次：先取前3个类型（如需基于记录计算可后续改造）
const recentConsumptionTypes = computed(() => allConsumptionTypes.value.slice(0, 3))

const showAllTypes = ref(false)

const displayedTypes = computed(() => {
  return showAllTypes.value ? allConsumptionTypes.value : recentConsumptionTypes.value
})

const loading = ref(false)
const handleSubmit = async () => {
  if (!form.value.card_id || !form.value.swipe_type_id || !form.value.consumption_type_id || !form.value.amount) {
    messageStore.warning('请填写完整信息')
    return
  }

  try {
    loading.value = true

    await recordStore.addRecord(form.value)
    messageStore.success('添加成功')

    // 重置表单
    form.value = {
      card_id: '',
      swipe_type_id: '',
      consumption_type_id: '',
      amount: '',
      trade_date: '',
      record_type: '支付', // 保持默认
      description: ''      // 重置描述
    }
  } catch (error) {
    console.error('添加记录错误:', error)
    messageStore.error(error || '操作失败')
  } finally {
    loading.value = false
  }
}

const selectConsumptionType = (type) => {
  form.value.consumption_type_id = type.id

  // 添加选中动画
  anime({
    targets: `[data-type="${type.id}"]`,
    scale: [1, 1.1, 1],
    duration: 300,
    easing: 'easeOutBack'
  })
}

const navigateTo = (path) => {
  router.push(path)
}

onMounted(async () => {
  // 先加载数据
  await Promise.all([
    cardStore.fetchCards(),
    categoryStore.fetchSwipeTypes(),
    categoryStore.fetchConsumptionTypes()
  ])

  // 页面进入动画
  anime.timeline()
    .add({
      targets: '.record-header',
      translateY: [-30, 0],
      opacity: [0, 1],
      duration: 600,
      easing: 'easeOutQuart'
    })
    .add({
      targets: '.form-section',
      translateY: [40, 0],
      opacity: [0, 1],
      duration: 500,
      delay: anime.stagger(100),
      easing: 'easeOutQuart'
    }, '-=300')
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="record-header bg-white px-6 py-6 opacity-0">
      <div class="flex items-center justify-between">
        <button @click="router.back()" class="p-2 -ml-2">
          <i class="fas fa-arrow-left text-gray-600 text-xl"></i>
        </button>
        <div class="text-center">
          <h1 class="text-xl font-bold text-gray-900 font-body">消费记录</h1>
          <p class="text-xs text-gray-500">EXPENSE RECORD</p>
        </div>
        <button @click="navigateTo('/records')" class="p-2 -ml-2">
          <i class="fas fa-list text-gray-600 text-xl"></i>
        </button>
      </div>
    </div>

    <!-- Form -->
    <div class="px-6 pb-24 space-y-6">
      <!-- 金额输入 -->
      <div class="form-section p-6 mb-0 opacity-0">
        <div class="text-center mb-6">
          <label class="block text-sm text-gray-500 mb-2">消费金额</label>
          <div class="relative">
            <span class="absolute left-0 top-1/2 transform -translate-y-1/2 text-4xl font-black text-gray-300 font-display">¥</span>
            <input
              v-model="form.amount"
              type="number"
              placeholder="0.00"
              class="w-full text-5xl font-black text-gray-900 font-display text-center bg-transparent border-none outline-none"
              step="0.01"
            />
          </div>
        </div>
      </div>

      <!-- 交易时间 -->
      <div class="form-section px-6 opacity-0">
        <div class="mb-2 px-2 flex items-center justify-between">
          <label class="block text-sm text-gray-500">交易时间</label>
          <span class="text-xs text-gray-400">不填默认当前时间</span>
        </div>
        <input
          v-model="form.trade_date"
          type="datetime-local"
          class="w-full px-3 py-2 bg-white rounded-lg border border-gray-200 text-gray-900"
          placeholder="不填则为当前时间"
        />
      </div>

      <!-- 记录类型 -->
      <div class="form-section opacity-0">
        <h3 class="text-lg font-bold text-gray-900 font-body mb-4 px-2">记录类型</h3>
        <div class="grid grid-cols-2 gap-3">
          <button
            v-for="t in recordTypes"
            :key="t.value"
            @click="form.record_type = t.value"
            class="card"
            :class="{ 'ring-2 ring-purple-500 bg-purple-50': form.record_type === t.value }"
          >
            <div class="text-sm font-medium text-gray-900">{{ t.label }}</div>
          </button>
        </div>
      </div>

      <!-- 信用卡选择 -->
      <div class="form-section opacity-0">
        <div class="flex items-center justify-between mb-4 px-2">
          <h3 class="text-lg font-bold text-gray-900 font-body">选择信用卡</h3>
          <button
            @click="showAllCards = !showAllCards"
            class="text-sm text-purple-600 hover:text-purple-700"
          >
            {{ showAllCards ? '收起' : '更多' }}
          </button>
        </div>
        <div class="grid grid-cols-1 gap-3">
          <div
            v-for="card in displayedCardsForCards"
            :key="card.id"
            @click="form.card_id = card.id"
            class="card"
            :class="{ 'ring-2 ring-purple-500 bg-purple-50': form.card_id === card.id }"
          >
            <div class="flex items-center">
              <div :class="`w-10 h-10 bg-gradient-to-br ${card.color} rounded-lg flex items-center justify-center mr-3`">
                <i class="fas fa-credit-card text-white text-lg"></i>
              </div>
              <div>
                <h4 class="font-bold text-gray-900">{{ card.bank }}</h4>
                <p class="text-sm text-gray-500">
                  **** {{ card.lastFour }}
                  <span class="text-purple-600 pl-4">账单日 {{ card.billDay }}号</span>
                </p>
              </div>
              <div class="ml-auto">
                <i
                  class="fas fa-check-circle text-xl transition-colors duration-300"
                  :class="form.card_id === card.id ? 'text-purple-500' : 'text-gray-300'"
                ></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 消费描述 -->
      <div v-show="isPay" class="form-section opacity-0">
        <h3 class="text-lg font-bold text-gray-900 font-body mb-4 px-2">消费描述</h3>
        <input
          v-model="form.description"
          type="text"
          class="w-full px-3 py-2 bg-white rounded-lg border border-gray-200 text-gray-900"
          placeholder="请输入消费描述，如商户、用途等"
        />
      </div>

      <!-- 刷卡类型 -->
      <div class="form-section opacity-0">
        <h3 class="text-lg font-bold text-gray-900 font-body mb-4 px-2">刷卡类型</h3>
        <div class="grid grid-cols-2 gap-3">
          <button
            v-for="type in swipeTypes"
            :key="type.id"
            @click="form.swipe_type_id = type.id"
            class="card"
            :class="{ 'ring-2 ring-purple-500 bg-purple-50': form.swipe_type_id === type.id }"
          >
            <div class="text-lg font-bold text-gray-900">{{ type.name }}</div>
            <p class="text-xs text-gray-500 mt-1">
              {{ type.name === '消费' ? 'CONSUMPTION' : 'DAILY' }}
            </p>
          </button>
        </div>
      </div>

      <!-- 消费类型 -->
      <div v-show="isPay" class="form-section opacity-0">
        <div class="flex items-center justify-between mb-4 px-2">
          <h3 class="text-lg font-bold text-gray-900 font-body">消费类型</h3>
          <button
            @click="showAllTypes = !showAllTypes"
            class="text-sm text-purple-600 hover:text-purple-700"
          >
            {{ showAllTypes ? '收起' : '更多' }}
          </button>
        </div>

        <div class="grid grid-cols-3 gap-3">
          <button
            v-for="type in displayedTypes"
            :key="type.id"
            :data-type="type.id"
            @click="selectConsumptionType(type)"
            class="card"
            :class="{ 'ring-2 ring-purple-500 bg-purple-50': form.consumption_type_id === type.id }"
          >
            <div class="text-sm font-medium text-gray-900">{{ type.name }}</div>
          </button>
        </div>

        <!-- 前3次提示 -->
        <div v-if="!showAllTypes" class="mt-3 px-2">
          <p class="text-xs text-gray-500">
            <i class="fas fa-lightbulb mr-1"></i>
            显示最近3次消费类型
          </p>
        </div>
      </div>

      <!-- 提交按钮 -->
      <button
        @click="handleSubmit"
        class="submit-btn w-full btn-primary py-4 text-lg font-semibold"
      >
        <i class="fas fa-plus mr-2"></i>
        添加记录
      </button>
    </div>

    <!-- Bottom Navigation -->
    <div class="fixed bottom-0 left-1/2 transform -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-200 px-6 py-4">
      <div class="flex justify-around">
        <button @click="router.push('/home')" class="flex flex-col items-center text-gray-400">
          <i class="fas fa-home text-xl mb-1"></i>
          <span class="text-xs">首页</span>
        </button>
        <button class="flex flex-col items-center text-purple-600">
          <i class="fas fa-plus-circle text-xl mb-1"></i>
          <span class="text-xs">记录</span>
        </button>
        <button @click="router.push('/manage')" class="flex flex-col items-center text-gray-400">
          <i class="fas fa-cog text-xl mb-1"></i>
          <span class="text-xs">管理</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 隐藏数字输入框的箭头 */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style>
