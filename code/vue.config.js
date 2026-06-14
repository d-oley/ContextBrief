const { defineConfig } = require('@vue/cli-service')

const mlProxyTarget = process.env.VUE_APP_ML_PROXY_TARGET || 'http://localhost:5000'

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: Number(process.env.PORT || 8081),
    proxy: {
      '^/evaluate': {
        target: mlProxyTarget,
        changeOrigin: true,
      },
    },
  },
})
