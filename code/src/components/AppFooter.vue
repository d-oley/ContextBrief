<template>
  <footer class="app-footer">
    <div class="container footer-content">
      <p>ContextBrief</p>
      <p>Аналитика и анализ открытых источников информации</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
}
</script>

<style scoped>
.app-footer {
  width: 100%;
  background: var(--primary);
  padding: 20px 24px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.footer-content p {
  margin: 0;
  color: #fff;
}
</style>

