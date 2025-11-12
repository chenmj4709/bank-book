<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import anime from 'animejs'
import BaseModal from '@/components/BaseModal.vue'
import { useCategoryStore } from '@/stores/category'
import { useCardStore } from '@/stores/card'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const categoryStore = useCategoryStore()
const cardStore = useCardStore()
const messageStore = useMessageStore()

// 响应式数据
const swipeTypes = computed(() => categoryStore.swipeTypes)
const consumptionTypes = computed(() => categoryStore.consumptionTypes)
const creditCards = computed(() => cardStore.cards)

const activeTab = ref('swipeTypes')
const loading = ref(false)
const submitted = ref(false)

// 模态框状态
const modalVisible = ref(false)
const modalTitle = ref('')
const modalMode = ref('add') // 'add' | 'edit'
const currentItem = ref(null)

// 表单数据
const formData = ref({
  // 刷卡类型
  name: '',
  description: '',
  // 消费类型
  // name: '', // 复用
  // 信用卡
  bank: '',
  card_number: '',
  credit_limit: '',
  bill_day: '',
  payment_day: '',
  last_payment_day: '',
  color: 'from-purple-500 to-purple-600'
})

const tabs = [
  { key: 'swipeTypes', name: '刷卡类型', icon: 'fas fa-credit-card' },
  { key: 'consumptionTypes', name: '消费类型', icon: 'fas fa-tags' },
  { key: 'creditCards', name: '信用卡', icon: 'fas fa-wallet' }
]

// 信用卡颜色选项
const cardColors = [
  { name: '紫色', value: 'from-purple-500 to-purple-600' },
  { name: '蓝色', value: 'from-blue-500 to-blue-600' },
  { name: '红色', value: 'from-red-500 to-red-600' },
  { name: '绿色', value: 'from-green-500 to-green-600' },
  { name: '橙色', value: 'from-orange-500 to-orange-600' },
  { name: '粉色', value: 'from-pink-500 to-pink-600' }
]

const switchTab = (tabKey) => {
  activeTab.value = tabKey

  // 切换动画
  anime({
    targets: '.tab-content',
    opacity: [0, 1],
    translateY: [20, 0],
    duration: 400,
    easing: 'easeOutQuart'
  })
}

// 重置表单
const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    bank: '',
    card_number: '',
    credit_limit: '',
    bill_day: '',
    payment_day: '',
    last_payment_day: '',
    color: 'from-purple-500 to-purple-600'
  }
}

// 打开添加弹窗
const addNewItem = () => {
  modalMode.value = 'add'
  resetForm()

  const currentTabData = tabs.find(t => t.key === activeTab.value)
  modalTitle.value = `添加${currentTabData?.name}`
  modalVisible.value = true
}

// 打开编辑弹窗
const editItem = (item) => {
  modalMode.value = 'edit'
  currentItem.value = item

  // 填充表单数据
  if (activeTab.value === 'swipeTypes') {
    formData.value.name = item.name
    formData.value.description = item.description
  } else if (activeTab.value === 'consumptionTypes') {
    formData.value.name = item.name
  } else if (activeTab.value === 'creditCards') {
    formData.value.bank = item.bank
    formData.value.card_number = item.card_number
    formData.value.credit_limit = item.credit_limit
    formData.value.bill_day = item.bill_day
    formData.value.payment_day = item.payment_day
    formData.value.last_payment_day = item.last_payment_day
    formData.value.color = item.color
  }

  const currentTabData = tabs.find(t => t.key === activeTab.value)
  modalTitle.value = `编辑${currentTabData?.name}`
  modalVisible.value = true
}

// 删除项目
const deleteItem = async (item) => {
  if (!confirm(`确定删除 ${item.name || item.bank} 吗？`)) {
    return
  }

  try {
    submitted.value = true

    if (activeTab.value === 'swipeTypes') {
      await categoryStore.deleteSwipeType(item.id)
    } else if (activeTab.value === 'consumptionTypes') {
      await categoryStore.deleteConsumptionType(item.id)
    } else if (activeTab.value === 'creditCards') {
      await cardStore.deleteCard(item.id)
    }

    // 显示成功消息
    messageStore.success('删除成功')
  } catch (error) {
    messageStore.error(error || '删除失败')
  } finally {
    submitted.value = false
  }
}

// 保存数据
const handleSave = async () => {
  try {
    submitted.value = true

    if (activeTab.value === 'swipeTypes') {
      const data = {
        name: formData.value.name,
        description: formData.value.description
      }

      if (modalMode.value === 'add') {
        await categoryStore.addSwipeType(data)
      } else {
        await categoryStore.updateSwipeType(currentItem.value.id, data)
      }
    } else if (activeTab.value === 'consumptionTypes') {
      const data = {
        name: formData.value.name
      }

      if (modalMode.value === 'add') {
        await categoryStore.addConsumptionType(data)
      } else {
        await categoryStore.updateConsumptionType(currentItem.value.id, data)
      }
    } else if (activeTab.value === 'creditCards') {
      const data = {
        bank: formData.value.bank,
        card_number: formData.value.card_number,
        credit_limit: parseInt(formData.value.credit_limit),
        bill_day: parseInt(formData.value.bill_day),
        payment_day: parseInt(formData.value.payment_day),
        last_payment_day: parseInt(formData.value.last_payment_day),
        color: formData.value.color
      }

      if (modalMode.value === 'add') {
        await cardStore.addCard(data)
      } else {
        await cardStore.updateCard(currentItem.value.id, data)
      }
    }

    modalVisible.value = false
    messageStore.success(modalMode.value === 'add' ? '添加成功' : '更新成功')
  } catch (error) {
    messageStore.error(error || '操作失败')
  } finally {
    submitted.value = false
  }
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    await Promise.all([
      categoryStore.fetchSwipeTypes(),
      categoryStore.fetchConsumptionTypes(),
      cardStore.fetchCards()
    ])
  } catch (error) {
    console.error('加载数据错误:', error)
    messageStore.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // 加载数据
  await loadData()

  // 页面进入动画
  anime.timeline()
    .add({
      targets: '.manage-header',
      translateY: [-30, 0],
      opacity: [0, 1],
      duration: 600,
      easing: 'easeOutQuart'
    })
    .add({
      targets: '.tab-nav',
      translateY: [20, 0],
      opacity: [0, 1],
      duration: 500,
      easing: 'easeOutQuart'
    }, '-=300')
    .add({
      targets: '.tab-content',
      opacity: [0, 1],
      duration: 400,
      easing: 'easeOutQuart'
    }, '-=200')
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="manage-header bg-white px-6 py-6 opacity-0">
      <div class="flex items-center justify-between">
        <button @click="router.back()" class="p-2 -ml-2">
          <i class="fas fa-arrow-left text-gray-600 text-xl"></i>
        </button>
        <div class="text-center">
          <h1 class="text-xl font-bold text-gray-900 font-body">管理中心</h1>
          <p class="text-xs text-gray-500">MANAGEMENT</p>
        </div>
        <button @click="addNewItem" class="p-2 bg-purple-100 rounded-full">
          <i class="fas fa-plus text-purple-600"></i>
        </button>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="tab-nav mb-6 opacity-0">
      <div class="flex bg-white rounded-b-2xl p-2">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="switchTab(tab.key)"
          class="flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-300"
          :class="activeTab === tab.key
            ? 'bg-purple-600 text-white shadow-lg'
            : 'text-gray-600 hover:text-gray-900'"
        >
          <i :class="tab.icon" class="mr-2"></i>
          {{ tab.name }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-8">
      <i class="fas fa-spinner fa-spin text-2xl text-purple-600"></i>
    </div>

    <!-- Tab Content -->
    <div v-else class="tab-content px-6 pb-24">
      <!-- 刷卡类型 -->
      <div v-if="activeTab === 'swipeTypes'" class="space-y-4">
        <div
          v-for="type in swipeTypes"
          :key="type.id"
          class="card"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mr-4">
                <i class="fas fa-credit-card text-white text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900 font-body">{{ type.name }}</h3>
                <p class="text-sm text-gray-500">{{ type.description }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ type.count || 0 }} 笔记录</p>
              </div>
            </div>
            <div class="flex space-x-2">
              <button @click="editItem(type)" class="p-2 text-gray-400 hover:text-purple-600">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="deleteItem(type)" class="p-2 text-gray-400 hover:text-red-600">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="swipeTypes.length === 0" class="text-center py-12">
          <i class="fas fa-credit-card text-4xl text-gray-300 mb-4"></i>
          <p class="text-gray-500">暂无刷卡类型</p>
          <button @click="addNewItem" class="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg">
            添加第一个
          </button>
        </div>
      </div>

      <!-- 消费类型 -->
      <div v-if="activeTab === 'consumptionTypes'" class="grid grid-cols-2 gap-4">
        <div
          v-for="type in consumptionTypes"
          :key="type.id"
          class="card"
        >
          <div class="text-center mb-3">
            <div class="w-10 h-10 bg-gradient-to-br from-gray-500 to-gray-600 rounded-lg mx-auto mb-2 flex items-center justify-center">
              <i class="fas fa-tag text-white"></i>
            </div>
            <h3 class="font-bold text-gray-900">{{ type.name }}</h3>
            <p class="text-xs text-gray-500">{{ type.count || 0 }} 次使用</p>
          </div>
          <div class="flex justify-center space-x-3">
            <button @click="editItem(type)" class="text-gray-400 hover:text-purple-600">
              <i class="fas fa-edit text-sm"></i>
            </button>
            <button @click="deleteItem(type)" class="text-gray-400 hover:text-red-600">
              <i class="fas fa-trash text-sm"></i>
            </button>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="consumptionTypes.length === 0" class="col-span-2 text-center py-12">
          <i class="fas fa-tags text-4xl text-gray-300 mb-4"></i>
          <p class="text-gray-500">暂无消费类型</p>
          <button @click="addNewItem" class="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg">
            添加第一个
          </button>
        </div>
      </div>

      <!-- 信用卡列表 -->
      <div v-if="activeTab === 'creditCards'" class="space-y-4">
        <div
          v-for="card in creditCards"
          :key="card.id"
          class="card"
        >
          <!-- 卡片头部 -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <div :class="`w-12 h-12 bg-gradient-to-br ${card.color} rounded-xl flex items-center justify-center mr-4`">
                <i class="fas fa-credit-card text-white text-lg"></i>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900 font-body">{{ card.bank }}</h3>
                <p class="text-sm text-gray-500">**** **** **** {{ card.card_number }}</p>
              </div>
            </div>
            <div class="flex space-x-2">
              <button @click="editItem(card)" class="p-2 text-gray-400 hover:text-purple-600">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="deleteItem(card)" class="p-2 text-gray-400 hover:text-red-600">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>

          <!-- 卡片信息 -->
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="text-center p-3 bg-gray-200/50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">信用额度</p>
              <p class="text-lg font-black text-gray-900 font-display">
                ¥{{ (card.credit_limit / 10000).toFixed(2) }}W
              </p>
            </div>
            <div class="text-center p-3 bg-purple-50 rounded-lg">
              <p class="text-xs text-purple-600 mb-1">账单日</p>
              <p class="text-lg font-black text-purple-600 font-display">
                {{ card.bill_day }}号
              </p>
            </div>
          </div>

          <!-- 重要日期 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="text-center p-2 bg-blue-50 rounded-lg">
              <p class="text-xs text-blue-600">还款日</p>
              <p class="font-bold text-blue-600">{{ card.payment_day }}号</p>
            </div>
            <div class="text-center p-2 bg-red-50 rounded-lg">
              <p class="text-xs text-red-600">最迟还款日</p>
              <p class="font-bold text-red-600">{{ card.last_payment_day }}号</p>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="creditCards.length === 0" class="text-center py-12">
          <i class="fas fa-wallet text-4xl text-gray-300 mb-4"></i>
          <p class="text-gray-500">暂无信用卡</p>
          <button @click="addNewItem" class="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg">
            添加第一张
          </button>
        </div>
      </div>
    </div>

    <!-- 模态框 -->
    <BaseModal
      :visible="modalVisible"
      :title="modalTitle"
      :loading="submitted"
      @close="modalVisible = false"
      @confirm="handleSave"
    >
      <!-- 刷卡类型表单 -->
      <div v-if="activeTab === 'swipeTypes'" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">类型名称</label>
          <input
            v-model="formData.name"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="请输入类型名称"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">描述</label>
          <input
            v-model="formData.description"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="请输入描述"
          />
        </div>
      </div>

      <!-- 消费类型表单 -->
      <div v-if="activeTab === 'consumptionTypes'" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">类型名称</label>
          <input
            v-model="formData.name"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="请输入类型名称"
          />
        </div>
      </div>

      <!-- 信用卡表单 -->
      <div v-if="activeTab === 'creditCards'" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">银行名称</label>
          <input
            v-model="formData.bank"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="请输入银行名称"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">卡号后四位</label>
          <input
            v-model="formData.card_number"
            type="text"
            maxlength="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="请输入卡号后四位"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">信用额度</label>
          <input
            v-model="formData.credit_limit"
            type="number"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="请输入信用额度"
          />
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">账单日</label>
            <input
              v-model="formData.bill_day"
              type="number"
              min="1"
              max="31"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="日"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">还款日</label>
            <input
              v-model="formData.payment_day"
              type="number"
              min="1"
              max="31"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="日"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">最迟还款日</label>
            <input
              v-model="formData.last_payment_day"
              type="number"
              min="1"
              max="31"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="日"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">卡片颜色</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="color in cardColors"
              :key="color.value"
              @click="formData.color = color.value"
              :class="`w-full h-10 rounded-lg bg-gradient-to-br ${color.value} flex items-center justify-center text-white text-sm font-medium ${
                formData.color === color.value ? 'ring-2 ring-purple-500 ring-offset-2' : ''
              }`"
            >
              {{ color.name }}
            </button>
          </div>
        </div>
      </div>
    </BaseModal>

    <!-- Bottom Navigation -->
    <div class="fixed bottom-0 left-1/2 transform -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-200 px-6 py-4">
      <div class="flex justify-around">
        <button @click="router.push('/home')" class="flex flex-col items-center text-gray-400">
          <i class="fas fa-home text-xl mb-1"></i>
          <span class="text-xs">首页</span>
        </button>
        <button @click="router.push('/record')" class="flex flex-col items-center text-gray-400">
          <i class="fas fa-plus-circle text-xl mb-1"></i>
          <span class="text-xs">记录</span>
        </button>
        <button class="flex flex-col items-center text-purple-600">
          <i class="fas fa-cog text-xl mb-1"></i>
          <span class="text-xs">管理</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tab-content {
  min-height: 400px;
}
</style>
