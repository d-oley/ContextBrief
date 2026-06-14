<template>
  <div class="home-page">
    <section class="hero-band">
      <div class="container hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">Сбор аналитики по открытым источникам</p>
          <h1>Ищите тему и получайте выжимку</h1>
          <p class="lead">
            Введите запрос, и система соберёт открытые источники, уберёт шум и вернёт краткий
            аналитический ответ с тезисами, источниками и рекомендациями.
          </p>
        </div>

        <div class="hero-panel">
          <div class="panel-topline">
            <span>Рабочая панель</span>
            <span class="panel-badge">Анализ темы</span>
          </div>

          <form class="search-form" @submit.prevent="startAnalysis">
            <label class="search-label" for="topic-search">Тема анализа</label>
            <textarea
              id="topic-search"
              v-model.trim="searchQuery"
              class="search-input"
              rows="4"
              placeholder="Например: Применение CLTV в иностранных банках"
            />

            <div class="chip-row">
              <button
                v-for="preset in presets"
                :key="preset"
                type="button"
                class="chip"
                @click="fillPreset(preset)"
              >
                {{ preset }}
              </button>
            </div>

            <button class="submit-btn" type="submit" :disabled="!searchQuery">
              Запустить анализ
            </button>
          </form>
        </div>
      </div>
    </section>

    <section class="container quick-grid">
      <p class="quick-line"><strong>Поиск</strong> — Система подбирает релевантные формулировки и ищет открытые источники.</p>
      <p class="quick-line"><strong>Синтез</strong> — Результаты сводятся в краткую выжимку с ключевыми тезисами.</p>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data() {
    return {
      searchQuery: '',
      presets: [
        'Применение CLTV в иностранных банках',
        'Как банки используют customer segmentation',
        'Подходы к удержанию клиентов в digital banking',
      ],
    }
  },
  methods: {
    fillPreset(value) {
      this.searchQuery = value
    },
    startAnalysis() {
      const topic = String(this.searchQuery || '').trim()
      if (!topic) return
      this.$router.push({ path: '/analysis', query: { q: topic } })
    },
  },
}
</script>

<style scoped>
.home-page {
  display: grid;
  gap: 28px;
  padding-bottom: 56px;
}

.hero-band {
  padding: 32px 0 8px;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 24px;
  align-items: stretch;
}

.hero-copy {
  display: grid;
  align-content: center;
  gap: 18px;
  min-height: 100%;
}

.eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(2.8rem, 6vw, 4.7rem);
  line-height: 0.98;
  letter-spacing: -0.04em;
}

.lead {
  margin: 0;
  max-width: 62ch;
  color: var(--text-muted);
  font-size: 1.08rem;
  line-height: 1.7;
}

.hero-panel {
  display: grid;
  gap: 18px;
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: 28px;
  background: var(--surface-strong);
  box-shadow: var(--shadow-lg);
}

.panel-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.panel-badge {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(244, 77, 77, 0.12);
  color: var(--accent);
  font-weight: 700;
}

.search-form {
  display: grid;
  gap: 16px;
}

.search-label {
  font-weight: 700;
}

.search-input {
  width: 100%;
  min-height: 120px;
  padding: 16px 18px;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: var(--input-bg);
  color: var(--text-main);
  resize: vertical;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  background: transparent;
  color: var(--text-main);
  padding: 9px 14px;
  font-size: 0.9rem;
  cursor: pointer;
}

.submit-btn {
  border: none;
  border-radius: 14px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #f44d4d 0%, #ff7a59 100%);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.quick-grid {
  display: grid;
  gap: 10px;
  margin-top: 24px;
}

.quick-line {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.6;
}

strong {
  color: var(--text-main);
}

@media (max-width: 980px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }
}
</style>
