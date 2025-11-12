<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import anime from 'animejs'
import GlobalMessage from '@/components/GlobalMessage.vue'

onMounted(() => {
  // 页面加载动画
  anime({
    targets: '.mobile-container',
    opacity: [0, 1],
    duration: 800,
    easing: 'easeOutQuart'
  })
})
</script>

<template>
  <div class="mobile-container safe-area">
    <RouterView />
    <GlobalMessage />
  </div>
</template>

<style scoped>
.mobile-container {
  opacity: 0;
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
