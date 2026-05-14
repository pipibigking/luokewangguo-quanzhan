<template>
  <div class="app-shell">
    <router-view />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans SC', 'Ma Shan Zheng', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
  background: linear-gradient(180deg, #0a0f25 0%, #1e293b 50%, #0f172a 100%);
}

.app-shell {
  min-height: 100vh;
}
</style>
