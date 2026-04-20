<template>
  <div class="claude-app">
    <!-- 顶部导航 -->
    <header class="claude-nav">
      <div class="claude-container claude-nav__inner">
        <div class="claude-nav__brand">
          <h1 class="claude-heading claude-heading--feature">Task Scheduler</h1>
        </div>
        <nav class="claude-nav__links">
          <router-link to="/tasks" class="claude-nav__link" active-class="active">
            SQL任务管理
          </router-link>
          <router-link to="/logs" class="claude-nav__link" active-class="active">
            执行日志
          </router-link>
        </nav>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="claude-main">
      <div class="claude-container">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
// Claude设计风格应用
</script>

<style>
@import './styles/claude-design.css';

/* ===== 应用级样式 ===== */

.claude-app {
  min-height: 100vh;
  background-color: var(--color-parchment);
}

/* ===== 导航栏 ===== */

.claude-nav {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  background-color: var(--color-ivory);
  border-bottom: 1px solid var(--color-border-cream);
  box-shadow: var(--shadow-whisper);
}

.claude-nav__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 var(--space-4xl);
}

.claude-nav__brand h1 {
  margin: 0;
  color: var(--color-near-black);
}

.claude-nav__links {
  display: flex;
  gap: var(--space-3xl);
}

.claude-nav__link {
  font-family: var(--font-sans);
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  color: var(--color-olive-gray);
  text-decoration: none;
  padding: var(--space-base) var(--space-lg);
  border-radius: var(--radius-comfortable);
  transition: all var(--transition-fast);
}

.claude-nav__link:hover {
  color: var(--color-near-black);
  background-color: var(--color-warm-sand);
}

.claude-nav__link.active {
  color: var(--color-near-black);
  background-color: var(--color-warm-sand);
  box-shadow: var(--shadow-ring-warm);
}

/* ===== 主内容区 ===== */

.claude-main {
  padding: var(--space-5xl) 0;
  min-height: calc(100vh - 64px);
}

/* ===== Element Plus 组件覆盖 - Claude风格 ===== */

/* 卡片 */
.el-card {
  background-color: var(--color-ivory) !important;
  border: 1px solid var(--color-border-cream) !important;
  border-radius: var(--radius-comfortable) !important;
  box-shadow: var(--shadow-whisper) !important;
}

.el-card__header {
  border-bottom: 1px solid var(--color-border-cream) !important;
  padding: var(--space-4xl) !important;
}

.el-card__body {
  padding: var(--space-4xl) !important;
}

/* 按钮 */
.el-button--primary {
  background-color: var(--color-terracotta) !important;
  border-color: var(--color-terracotta) !important;
  color: var(--color-ivory) !important;
  border-radius: var(--radius-generous) !important;
}

.el-button--primary:hover {
  background-color: var(--color-coral) !important;
  border-color: var(--color-coral) !important;
}

.el-button--default {
  background-color: var(--color-warm-sand) !important;
  border-color: var(--color-border-cream) !important;
  color: var(--color-charcoal-warm) !important;
  border-radius: var(--radius-comfortable) !important;
}

.el-button--default:hover {
  background-color: var(--color-border-warm) !important;
  border-color: var(--color-ring-warm) !important;
}

.el-button--danger {
  background-color: var(--color-error) !important;
  border-color: var(--color-error) !important;
  border-radius: var(--radius-comfortable) !important;
}

/* 输入框 */
.el-input__wrapper {
  background-color: var(--color-ivory) !important;
  border-radius: var(--radius-generous) !important;
  box-shadow: 0 0 0 1px var(--color-border-cream) inset !important;
}

.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px var(--color-ring-warm) inset !important;
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px var(--color-focus-blue) inset, 0 0 0 3px rgba(56, 152, 236, 0.1) !important;
}

.el-textarea__inner {
  background-color: var(--color-ivory) !important;
  border: 1px solid var(--color-border-cream) !important;
  border-radius: var(--radius-generous) !important;
}

.el-textarea__inner:focus {
  border-color: var(--color-focus-blue) !important;
  box-shadow: 0 0 0 3px rgba(56, 152, 236, 0.1) !important;
}

/* 表格 */
.el-table {
  background-color: var(--color-ivory) !important;
  border-radius: var(--radius-comfortable) !important;
}

.el-table th {
  background-color: var(--color-warm-sand) !important;
  color: var(--color-charcoal-warm) !important;
  font-weight: var(--weight-medium) !important;
}

.el-table td {
  border-bottom: 1px solid var(--color-border-cream) !important;
}

.el-table--striped .el-table__body tr.el-table__row--striped td {
  background-color: var(--color-parchment) !important;
}

.el-table__row:hover > td {
  background-color: var(--color-warm-sand) !important;
}

/* 对话框 */
.el-dialog {
  border-radius: var(--radius-very) !important;
  box-shadow: var(--shadow-whisper), 0 0 0 1px var(--color-border-cream) !important;
}

.el-dialog__header {
  border-bottom: 1px solid var(--color-border-cream) !important;
  padding: var(--space-4xl) !important;
}

.el-dialog__title {
  font-family: var(--font-serif) !important;
  font-weight: var(--weight-medium) !important;
  color: var(--color-near-black) !important;
}

.el-dialog__body {
  padding: var(--space-4xl) !important;
}

.el-dialog__footer {
  border-top: 1px solid var(--color-border-cream) !important;
  padding: var(--space-4xl) !important;
}

/* 分页 */
.el-pagination {
  font-family: var(--font-sans) !important;
}

.el-pagination button {
  background-color: var(--color-ivory) !important;
  border: 1px solid var(--color-border-cream) !important;
  border-radius: var(--radius-comfortable) !important;
  color: var(--color-charcoal-warm) !important;
}

.el-pagination button:hover {
  background-color: var(--color-warm-sand) !important;
  color: var(--color-near-black) !important;
}

.el-pagination .el-pager li {
  background-color: var(--color-ivory) !important;
  border: 1px solid var(--color-border-cream) !important;
  border-radius: var(--radius-comfortable) !important;
  color: var(--color-charcoal-warm) !important;
}

.el-pagination .el-pager li:hover {
  background-color: var(--color-warm-sand) !important;
  color: var(--color-near-black) !important;
}

.el-pagination .el-pager li.is-active {
  background-color: var(--color-terracotta) !important;
  border-color: var(--color-terracotta) !important;
  color: var(--color-ivory) !important;
}

/* 标签 */
.el-tag {
  border-radius: var(--radius-highly) !important;
  font-weight: var(--weight-medium) !important;
}

.el-tag--success {
  background-color: rgba(103, 194, 58, 0.1) !important;
  border-color: rgba(103, 194, 58, 0.2) !important;
  color: #67c23a !important;
}

.el-tag--info {
  background-color: var(--color-warm-sand) !important;
  border-color: var(--color-border-warm) !important;
  color: var(--color-olive-gray) !important;
}

.el-tag--warning {
  background-color: rgba(230, 162, 60, 0.1) !important;
  border-color: rgba(230, 162, 60, 0.2) !important;
  color: #e6a23c !important;
}

/* 表单 */
.el-form-item__label {
  color: var(--color-near-black) !important;
  font-weight: var(--weight-medium) !important;
}

/* 单选/复选 */
.el-radio__input.is-checked + .el-radio__label {
  color: var(--color-near-black) !important;
}

.el-checkbox__input.is-checked + .el-checkbox__label {
  color: var(--color-near-black) !important;
}

/* 开关 */
.el-switch.is-checked .el-switch__core {
  background-color: var(--color-terracotta) !important;
  border-color: var(--color-terracotta) !important;
}

/* 消息提示 */
.el-message {
  border-radius: var(--radius-generous) !important;
  box-shadow: var(--shadow-whisper), 0 0 0 1px var(--color-border-cream) !important;
}

.el-message--success {
  background-color: var(--color-ivory) !important;
  border-color: #67c23a !important;
}

.el-message--error {
  background-color: var(--color-ivory) !important;
  border-color: var(--color-error) !important;
}

.el-message--warning {
  background-color: var(--color-ivory) !important;
  border-color: #e6a23c !important;
}

/* 加载 */
.el-loading-mask {
  background-color: rgba(245, 244, 237, 0.8) !important;
}

/* 下拉菜单 */
.el-dropdown-menu {
  border-radius: var(--radius-comfortable) !important;
  box-shadow: var(--shadow-whisper), 0 0 0 1px var(--color-border-cream) !important;
}

.el-dropdown-menu__item:hover {
  background-color: var(--color-warm-sand) !important;
  color: var(--color-near-black) !important;
}

/* 选择器 */
.el-select-dropdown {
  border-radius: var(--radius-comfortable) !important;
  box-shadow: var(--shadow-whisper), 0 0 0 1px var(--color-border-cream) !important;
}

.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover {
  background-color: var(--color-warm-sand) !important;
}

.el-select-dropdown__item.selected {
  color: var(--color-near-black) !important;
  font-weight: var(--weight-medium) !important;
}
</style>
