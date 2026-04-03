<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-main">
        <div class="footer-brand">
          <span class="logo-icon">🦞</span>
          <span class="brand-name">ClawHub</span>
          <p class="brand-desc">OpenClaw 的容器注册中心</p>
        </div>
        
        <div class="footer-links">
          <div class="link-group">
            <h4>产品</h4>
            <a href="#">功能特性</a>
            <a href="#">定价</a>
            <a href="#">更新日志</a>
          </div>
          <div class="link-group">
            <h4>资源</h4>
            <a href="#">文档</a>
            <a href="#">API</a>
            <a href="#">CLI</a>
          </div>
          <div class="link-group">
            <h4>社区</h4>
            <a href="#">GitHub</a>
            <a href="#">Discord</a>
            <a href="#">Twitter</a>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>© 2024 ClawHub. Open source under MIT License.</p>
      </div>
    </div>
  </footer>
</template>

<style scoped lang="scss">
.app-footer {
  background: var(--el-fill-color-light);
  border-top: 1px solid var(--el-border-color);
  padding: 48px 24px 24px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-main {
  display: flex;
  justify-content: space-between;
  margin-bottom: 48px;
}

.footer-brand {
  .logo-icon {
    font-size: 40px;
    margin-right: 8px;
  }
  
  .brand-name {
    font-size: 20px;
    font-weight: 700;
  }
  
  .brand-desc {
    color: var(--el-text-color-secondary);
    margin: 8px 0 0;
  }
}

.footer-links {
  display: flex;
  gap: 64px;
}

.link-group {
  h4 {
    font-size: 14px;
    font-weight: 600;
    margin: 0 0 16px;
  }
  
  a {
    display: block;
    color: var(--el-text-color-secondary);
    text-decoration: none;
    margin-bottom: 8px;
    
    &:hover {
      color: var(--el-color-primary);
    }
  }
}

.footer-bottom {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color);
  color: var(--el-text-color-secondary);
  font-size: 14px;
}
</style>
