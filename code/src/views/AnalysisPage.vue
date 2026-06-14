<template>
  <div class="analysis-page">
    <section class="container analysis-shell">
      <div class="top-row">
        <router-link class="back-link" to="/">← Вернуться</router-link>
        <span class="result-kicker">Результат анализа</span>
      </div>

      <section v-if="isLoading" class="card">
        <div class="spinner"></div>
        <p>Ищем источники, отбираем главное и собираем ответ.</p>
      </section>

      <section v-else-if="analysisResult" class="result-layout">
        <div class="result-main">
          <div class="result-header">
            <div>
              <h1>{{ analysisResult.topic }}</h1>
            </div>
            <span class="confidence-pill" v-if="analysisResult.confidence">
              {{ confidenceLabel }}
            </span>
          </div>

          <div class="result-block">
            <p class="block-title">Краткая выжимка</p>
            <p class="block-text">{{ analysisResult.summary }}</p>
          </div>

          <div class="result-block result-response">
            <p class="block-title">Полный ответ</p>
            <div v-if="responseSections.length" class="response-sections">
              <section v-for="section in responseSections" :key="section.title" class="response-section">
                <h3>{{ section.title }}</h3>
                <p
                  v-for="(paragraph, index) in section.paragraphs"
                  :key="index"
                  class="response-paragraph"
                >
                  <template v-for="(part, partIndex) in parseInlineMarkdown(paragraph)" :key="partIndex">
                    <strong v-if="part.bold">{{ part.text }}</strong>
                    <span v-else>{{ part.text }}</span>
                  </template>
                </p>
                <ul v-if="section.items.length" class="response-list">
                  <li v-for="(item, index) in section.items" :key="index">
                    <template v-for="(part, partIndex) in parseInlineMarkdown(item)" :key="partIndex">
                      <strong v-if="part.bold">{{ part.text }}</strong>
                      <span v-else>{{ part.text }}</span>
                    </template>
                  </li>
                </ul>
              </section>
            </div>
            <p v-else class="response-text">
              <template v-for="(part, partIndex) in parseInlineMarkdown(analysisResult.response)" :key="partIndex">
                <strong v-if="part.bold">{{ part.text }}</strong>
                <span v-else>{{ part.text }}</span>
              </template>
            </p>
          </div>

          <div class="result-block" v-if="analysisResult.keyPoints.length">
            <p class="block-title">Ключевые тезисы</p>
            <ul class="bullet-list">
              <li v-for="(point, index) in analysisResult.keyPoints" :key="index">
                <template v-for="(part, partIndex) in parseInlineMarkdown(point)" :key="partIndex">
                  <strong v-if="part.bold">{{ part.text }}</strong>
                  <span v-else>{{ part.text }}</span>
                </template>
              </li>
            </ul>
          </div>

          <div class="result-block" v-if="analysisResult.recommendations.length">
            <p class="block-title">Практические рекомендации</p>
            <ul class="bullet-list bullet-accent">
              <li v-for="(point, index) in analysisResult.recommendations" :key="index">
                <template v-for="(part, partIndex) in parseInlineMarkdown(point)" :key="partIndex">
                  <strong v-if="part.bold">{{ part.text }}</strong>
                  <span v-else>{{ part.text }}</span>
                </template>
              </li>
            </ul>
          </div>

          <div class="result-block" v-if="analysisResult.sources.length">
            <p class="block-title">Источники</p>
            <ul class="source-list">
              <li v-for="(source, index) in analysisResult.sources" :key="index">
                <div v-if="isUrl(source)" class="source-item">
                  <span class="source-name">{{ formatSourceLabel(source) }}</span>
                  <a class="source-link" :href="source" target="_blank" rel="noreferrer">
                    {{ source }}
                  </a>
                </div>
                <span v-else>{{ source }}</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <section v-else-if="error" class="card">
        <p>{{ error }}</p>
      </section>

    </section>

    <div v-if="showCensorModal" class="modal-backdrop" @click.self="closeCensorModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="censor-modal-title">
        <h2 id="censor-modal-title">Запрос отклонён</h2>
        <p>{{ censorModalMessage }}</p>
        <button class="modal-btn" type="button" @click="returnHome">
          простите меня пожалуйста 😭
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { analyzeTopic } from '@/api/analysisApi'

export default {
  name: 'AnalysisPage',
  data() {
    return {
      searchQuery: '',
      isLoading: false,
      error: null,
      analysisResult: null,
      showCensorModal: false,
      censorModalMessage: 'Пользователь, на мой взгляд вы говорите какие-то гадости 😠',
    }
  },
  created() {
    this.syncQueryFromRoute()
  },
  watch: {
    '$route.query.q': {
      handler() {
        this.syncQueryFromRoute()
      },
    },
  },
  computed: {
    confidenceLabel() {
      const value = String(this.analysisResult?.confidence || '').toLowerCase()
      if (value === 'high') return 'Высокая уверенность'
      if (value === 'medium') return 'Средняя уверенность'
      if (value === 'low') return 'Низкая уверенность'
      return this.analysisResult?.confidence
    },
    responseSections() {
      const response = String(this.analysisResult?.response || '').trim()
      if (!response) return []

      const lines = response.split(/\r?\n/)
      const sections = []
      let current = null

      const pushCurrent = () => {
        if (!current) return
        current.paragraphs = current.paragraphs.filter(Boolean)
        current.items = current.items.filter(Boolean)
        if (current.title || current.paragraphs.length || current.items.length) {
          sections.push(current)
        }
      }

      for (const rawLine of lines) {
        const line = rawLine.trim()
        if (!line) continue

        const headingMatch = line.match(/^#{1,6}\s*(.+)$/)
        if (headingMatch) {
          pushCurrent()
          current = {
            title: headingMatch[1].trim(),
            paragraphs: [],
            items: [],
          }
          continue
        }

        if (!current) {
          current = {
            title: 'Результат',
            paragraphs: [],
            items: [],
          }
        }

        if (/^[-*•]\s+/.test(line)) {
          current.items.push(line.replace(/^[-*•]\s+/, '').trim())
        } else {
          current.paragraphs.push(line)
        }
      }

      pushCurrent()
      return sections
    },
  },
  methods: {
    isUrl(value) {
      return /^https?:\/\//i.test(String(value || ''))
    },
    formatSourceLabel(value) {
      try {
        const parsed = new URL(String(value))
        const host = parsed.hostname.replace(/^www\./i, '')
        const path = parsed.pathname.replace(/\/$/, '')
        const lastSegment = path.split('/').filter(Boolean).pop()
        if (lastSegment) {
          return `${host} / ${lastSegment.replace(/[-_]+/g, ' ')}`
        }
        return host
      } catch {
        return String(value || '')
      }
    },
    parseInlineMarkdown(text) {
      const source = String(text || '')
      if (!source) return []

      const parts = []
      const pattern = /(\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|_[^_]+_)/g
      let lastIndex = 0
      let match

      while ((match = pattern.exec(source)) !== null) {
        if (match.index > lastIndex) {
          parts.push({ text: source.slice(lastIndex, match.index).replace(/[*_]/g, ''), bold: false })
        }

        const raw = match[0]
        const boldText = raw.replace(/^(\*\*|__)(.*)(\*\*|__)$/, '$2').replace(/^(\*|_)(.*)(\*|_)$/, '$2')
        parts.push({ text: boldText, bold: true })
        lastIndex = match.index + raw.length
      }

      if (lastIndex < source.length) {
        parts.push({ text: source.slice(lastIndex).replace(/[*_]/g, ''), bold: false })
      }

      return parts.length ? parts : [{ text: source, bold: false }]
    },
    async syncQueryFromRoute() {
      const routeQuery = String(this.$route.query.q || '').trim()
      if (!routeQuery) return
      if (routeQuery === this.searchQuery && this.analysisResult) return

      this.searchQuery = routeQuery
      await this.handleSearch()
    },
    normalizeAnalysis(result) {
      const analysis = result?.analysis || {}
      return {
        topic: analysis.topic || this.searchQuery,
        summary: analysis.summary || 'Краткая выжимка готова.',
        response: String(result?.response || '').trim() || analysis.summary || 'Краткая выжимка готова.',
        keyPoints: Array.isArray(analysis.keyPoints) ? analysis.keyPoints : [],
        recommendations: Array.isArray(analysis.recommendations) ? analysis.recommendations : [],
        sources: Array.isArray(analysis.sources) ? analysis.sources : [],
        confidence: analysis.confidence || '',
      }
    },
    async handleSearch() {
      if (!this.searchQuery) return

      this.isLoading = true
      this.error = null
      this.analysisResult = null
      this.showCensorModal = false

      try {
        const result = await analyzeTopic({ text: this.searchQuery })

        if (result && result.status === 'accepted') {
          this.analysisResult = this.normalizeAnalysis(result)
        } else {
          this.error = result?.message || 'Ошибка при анализе информации'
        }
      } catch (err) {
        const code = err?.body?.code || err?.code
        if (code === 'REQUEST_BLOCKED' || err?.status === 400) {
          this.showCensorModal = true
          this.error = null
        } else {
          this.error = err?.message || 'Ошибка при подключении к сервису анализа'
        }
      } finally {
        this.isLoading = false
      }
    },
    closeCensorModal() {
      this.showCensorModal = false
    },
    returnHome() {
      this.showCensorModal = false
      this.$router.push('/')
    },
  },
}
</script>

<style scoped>
.analysis-page {
  padding-bottom: 56px;
}

.analysis-shell {
  display: grid;
  gap: 20px;
  padding-top: 20px;
}

.top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.back-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 800;
}

.result-kicker {
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
}

.card {
  padding: 28px;
  border: 1px solid var(--border);
  border-radius: 24px;
  background: var(--surface);
}

.result-layout {
  display: grid;
}

.result-main {
  display: grid;
  gap: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.result-header h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.08;
}

.confidence-pill {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(244, 77, 77, 0.12);
  color: var(--accent);
  font-weight: 700;
  white-space: nowrap;
}

.result-block {
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 22px;
  background: var(--surface);
}

.block-title {
  margin: 0 0 10px;
  color: var(--text-muted);
  font-size: 0.84rem;
  font-weight: 700;
  text-transform: uppercase;
}

.block-text,
.response-text {
  margin: 0;
  color: var(--text-main);
  line-height: 1.7;
}

.response-sections,
.bullet-list,
.response-list,
.source-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 10px;
}

.response-section {
  display: grid;
  gap: 8px;
}

.response-section h3 {
  margin: 0;
}

.response-paragraph {
  margin: 0;
  line-height: 1.7;
}

.bullet-accent li::marker {
  color: var(--accent);
}

.source-list a {
  color: var(--accent);
  text-decoration: none;
}

.source-list a:hover {
  text-decoration: underline;
}

.source-item {
  display: grid;
  gap: 4px;
}

.source-name {
  color: var(--text-main);
  font-weight: 700;
}

.source-link {
  word-break: break-all;
}

.spinner {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid rgba(244, 77, 77, 0.16);
  border-top-color: var(--accent);
  animation: spin 1s linear infinite;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 20px;
  background: var(--overlay-bg);
  backdrop-filter: blur(8px);
  z-index: 40;
}

.modal-card {
  width: min(520px, 100%);
  padding: 28px;
  border-radius: 24px;
  border: 1px solid var(--border);
  background: var(--card-bg);
  box-shadow: 0 28px 80px rgba(15, 23, 42, 0.28);
  display: grid;
  gap: 14px;
  text-align: center;
}

.modal-card h2 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.45rem;
}

.modal-card p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.7;
  font-size: 1.02rem;
}

.modal-btn {
  justify-self: center;
  border: none;
  border-radius: 14px;
  padding: 12px 18px;
  background: linear-gradient(135deg, #f44d4d 0%, #ff7a59 100%);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(244, 77, 77, 0.28);
}

.modal-btn:hover {
  transform: translateY(-1px);
}

.modal-btn:active {
  transform: translateY(0);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 720px) {
  .top-row,
  .result-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
