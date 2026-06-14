<template>
  <div class="app-shell">
    <app-header :theme="theme" @toggle-theme="toggleTheme" />

    <main class="app-main">
      <router-view />
    </main>

    <app-footer />
  </div>
</template>

<script>
import AppFooter from './components/AppFooter.vue'
import AppHeader from './components/AppHeader.vue'

export default {
  name: 'App',
  components: { AppFooter, AppHeader },
  data() {
    return {
      theme: localStorage.getItem('theme') || 'light',
    }
  },
  created() {
    document.title = 'ContextBrief'
    document.documentElement.setAttribute('data-theme', this.theme)
  },
  methods: {
    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      document.documentElement.setAttribute('data-theme', this.theme)
      localStorage.setItem('theme', this.theme)
    },
  },
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  padding: clamp(12px, 3vw, 24px) 0;
  background:
    radial-gradient(circle at top right, var(--bg-accent), transparent 35%),
    linear-gradient(160deg, var(--bg-main) 0%, var(--bg-main-mid) 50%, var(--bg-main-end) 100%);
}
</style>
