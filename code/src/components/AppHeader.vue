<template>
  <header class="header">
    <div class="container header-inner">
      <router-link class="brand" to="/">
        <img class="brand-logo" :src="logoSrc" alt="Логотип ContextBrief" />
        <div class="brand-copy">
          <span class="brand-text">ContextBrief</span>
          <span class="brand-subtitle">Аналитика открытых источников</span>
        </div>
      </router-link>

      <nav class="nav">
        <router-link class="nav-link" to="/">Главная</router-link>
      </nav>

      <div class="header-controls">
        <button
          class="theme-toggle"
          type="button"
          :aria-label="themeToggleLabel"
          :title="themeToggleLabel"
          @click="$emit('toggle-theme')"
        >
          <svg
            v-if="theme === 'dark'"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.8" />
            <path
              d="M12 2.8V5.2M12 18.8V21.2M21.2 12H18.8M5.2 12H2.8M18.5 5.5L16.8 7.2M7.2 16.8L5.5 18.5M18.5 18.5L16.8 16.8M7.2 7.2L5.5 5.5"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />
          </svg>
          <svg
            v-else
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              d="M20 14.7C19.2 15 18.4 15.2 17.5 15.2C13.8 15.2 10.8 12.2 10.8 8.5C10.8 7.6 11 6.8 11.3 6C8.1 6.4 5.6 9.1 5.6 12.4C5.6 16 8.6 19 12.2 19C15.5 19 18.2 16.5 18.6 13.3C18.9 13.8 19.4 14.3 20 14.7Z"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script>
import logoSrc from '@/assets/logo.png'

export default {
  name: 'AppHeader',
  props: {
    theme: {
      type: String,
      default: 'light',
    },
  },
  emits: ['toggle-theme'],
  data() {
    return {
      logoSrc,
    }
  },
  computed: {
    themeToggleLabel() {
      return this.theme === 'dark' ? 'Переключить на светлую тему' : 'Переключить на темную тему'
    },
  },
}
</script>

<style scoped>
.header {
  border-bottom: 1px solid var(--border);
  background: var(--header-bg);
  backdrop-filter: blur(10px);
}

.header-inner {
  min-height: 80px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.brand-logo {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 10px;
}

.brand-copy {
  display: grid;
  gap: 2px;
}

.brand-text {
  font-weight: 800;
  font-size: 1rem;
  color: var(--text-main);
}

.brand-subtitle {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav {
  display: flex;
  align-items: center;
  gap: 18px;
}

.nav-link {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 700;
}

.nav-link.router-link-exact-active {
  color: var(--text-main);
}

.theme-toggle {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--input-bg);
  color: var(--text-main);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.theme-toggle svg {
  width: 20px;
  height: 20px;
}

@media (max-width: 700px) {
  .header-inner {
    flex-wrap: wrap;
    padding-top: 10px;
    padding-bottom: 10px;
  }

  .nav {
    order: 3;
    width: 100%;
  }

  .header-controls {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
