# Claude 设计风格实施指南

## 📋 概述

本项目前端已全面采用 **Claude (Anthropic) 设计风格**，营造温暖、人文、编辑级的用户体验。本指南详细说明设计系统的实施情况和使用方法。

---

## 🎨 核心设计理念

### 设计哲学
- **温暖的文学沙龙**而非冷峻的科技产品
- **羊皮纸质感**的页面背景（`#f5f4ed`）
- **编辑级排版** - 衬线字体标题 + 无衬线UI文字
- **有机视觉语言** - 手绘感插图替代科技图标
- ** exclusively 暖色调** - 所有灰色都带黄棕底色

### 关键特征
✅ 暖色调羊皮纸画布  
✅ Anthropic Serif 衬线字体用于标题  
✅ 赤陶色品牌主色（`#c96442`）  
✅ 杂志级排版节奏  
✅ 环状阴影系统（非传统投影）  

---

## 📁 文件结构

```
frontend/src/
├── styles/
│   └── claude-design.css          # Claude设计系统CSS变量和基础类
├── App.vue                         # 应用根组件（含导航栏样式）
├── views/
│   ├── SqlExportTasks.vue         # 任务管理页面（已重构）
│   └── SqlExportLogs.vue          # 执行日志页面（待重构）
└── ...
```

---

## 🎯 已完成的工作

### 1. 规范文档更新 ✅

**文件**: `doc/need.md`

新增 **3.2节 UI设计规范**，包含：
- 设计风格定位与核心理念
- 完整色彩系统（主色、辅助色、语义色）
- 字体层级规范（Georgia衬线 + Inter无衬线）
- 组件样式规范（按钮、卡片、输入框）
- 布局原则（间距、圆角、阴影）
- 响应式行为定义
- Do's and Don'ts 清单

### 2. CSS设计系统实现 ✅

**文件**: `frontend/src/styles/claude-design.css`

实现了完整的Claude设计令牌：

#### 色彩变量
```css
--color-parchment: #f5f4ed;        /* 页面背景 */
--color-ivory: #faf9f5;            /* 卡片表面 */
--color-near-black: #141413;       /* 主要文字 */
--color-terracotta: #c96442;       /* 品牌CTA */
--color-warm-sand: #e8e6dc;        /* 次要按钮 */
...
```

#### 字体变量
```css
--font-serif: 'Georgia', serif;    /* 标题字体 */
--font-sans: 'Inter', sans-serif;  /* UI字体 */
--text-display: 4rem;              /* Hero标题 */
--text-section: 3.25rem;           /* 区块标题 */
--leading-relaxed: 1.60;           /* 正文字高 */
```

#### 间距与圆角
```css
--space-base: 8px;                 /* 基础单位 */
--radius-comfortable: 8px;         /* 标准圆角 */
--radius-generous: 12px;           /* 慷慨圆角 */
--radius-maximum: 32px;            /* 最大圆角 */
```

#### 阴影系统
```css
--shadow-contained-light: 0 0 0 1px var(--color-border-cream);
--shadow-ring-warm: 0 0 0 1px var(--color-ring-warm);
--shadow-whisper: 0 4px 24px rgba(0, 0, 0, 0.05);
```

### 3. 全局样式类 ✅

提供了可直接使用的CSS类：

#### 排版类
```html
<h1 class="claude-heading claude-heading--display">Hero标题</h1>
<h2 class="claude-heading claude-heading--section">区块标题</h2>
<p class="claude-body claude-body--large">大正文</p>
<span class="claude-caption">说明文字</span>
<code class="claude-code">代码片段</code>
```

#### 按钮类
```html
<button class="claude-btn claude-btn--primary">主要CTA</button>
<button class="claude-btn claude-btn--secondary">次要按钮</button>
<button class="claude-btn claude-btn--dark">深色按钮</button>
<button class="claude-btn claude-btn--ghost">幽灵按钮</button>
```

#### 布局类
```html
<div class="claude-container">居中容器（max-width: 1200px）</div>
<div class="claude-card">标准卡片</div>
<div class="claude-card claude-card--featured">特色卡片</div>
```

### 4. Element Plus 组件覆盖 ✅

**文件**: `frontend/src/App.vue`

全面覆盖Element Plus组件样式，使其符合Claude风格：

| 组件 | 改造要点 |
|------|---------|
| `.el-card` | Ivory背景 + Cream边框 + Whisper阴影 |
| `.el-button--primary` | Terracotta背景 + Generous圆角 |
| `.el-button--default` | Warm Sand背景 + Comfortable圆角 |
| `.el-input__wrapper` | Ivory背景 + Generous圆角 + Focus Blue焦点 |
| `.el-table th` | Warm Sand表头 + Charcoal文字 + Medium字重 |
| `.el-dialog` | Very圆角 + Cream边框 + Serif标题 |
| `.el-pagination` | Ivory按钮 + Terracotta激活态 |
| `.el-tag` | Highly圆角 + 柔和背景色 |

### 5. 任务管理页面重构 ✅

**文件**: `frontend/src/views/SqlExportTasks.vue`

完全按照Claude风格重新设计：

#### 页面结构
```vue
<div class="claude-page">
  <!-- 页面标题区 -->
  <div class="page-header">
    <h2 class="claude-heading claude-heading--section">SQL导出任务管理</h2>
    <p class="claude-body claude-body--secondary">副标题描述</p>
    <button class="claude-btn claude-btn--primary">+ 新建任务</button>
  </div>
  
  <!-- 搜索栏卡片 -->
  <div class="claude-card mt-4">...</div>
  
  <!-- 任务列表卡片 -->
  <div class="claude-card mt-4">...</div>
</div>
```

#### 关键改进
- ✅ 使用 `claude-heading` 类渲染页面标题（Georgia字体）
- ✅ 按钮替换为原生 `<button>` + Claude类（移除el-button）
- ✅ Cron表达式使用 `<code class="claude-code">` 展示
- ✅ 表单提示使用 `claude-caption` + emoji图标
- ✅ 表格行悬停变为Warm Sand背景
- ✅ 分页器简化布局，突出记录数统计
- ✅ 对话框使用Serif标题 + Generous圆角

---

## 🚀 使用方法

### 1. 在新页面中应用Claude风格

```vue
<template>
  <div class="claude-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="claude-heading claude-heading--section">页面标题</h2>
      <p class="claude-body claude-body--secondary mt-1">页面描述</p>
    </div>
    
    <!-- 内容卡片 -->
    <div class="claude-card mt-4">
      <!-- 内容 -->
    </div>
  </div>
</template>

<style scoped>
/* 页面特定样式 */
</style>
```

### 2. 使用Claude按钮

```vue
<!-- 主要操作 -->
<button class="claude-btn claude-btn--primary" @click="handlePrimary">
  主要操作
</button>

<!-- 次要操作 -->
<button class="claude-btn claude-btn--secondary" @click="handleSecondary">
  次要操作
</button>

<!-- 危险操作 -->
<button class="claude-btn claude-btn--danger" @click="handleDanger">
  删除
</button>

<!-- 小尺寸按钮 -->
<button class="claude-btn claude-btn--primary claude-btn--sm">
  小按钮
</button>
```

### 3. 使用Claude排版

```vue
<template>
  <div>
    <!-- 大标题 -->
    <h1 class="claude-heading claude-heading--display">Display标题</h1>
    
    <!-- 区块标题 -->
    <h2 class="claude-heading claude-heading--section">Section标题</h2>
    
    <!-- 副标题 -->
    <h3 class="claude-heading claude-heading--sub">Sub标题</h3>
    
    <!-- 标准正文 -->
    <p class="claude-body">标准正文内容</p>
    
    <!-- 大正文 -->
    <p class="claude-body claude-body--large">介绍性段落</p>
    
    <!-- 次要文字 -->
    <p class="claude-body claude-body--secondary">次要信息</p>
    
    <!-- 说明文字 -->
    <span class="claude-caption">元数据、时间戳等</span>
    
    <!-- 代码 -->
    <code class="claude-code">SELECT * FROM table</code>
  </div>
</template>
```

### 4. 使用Claude布局工具类

```vue
<template>
  <div>
    <!-- 间距 -->
    <div class="mt-1">Margin Top 1x</div>
    <div class="mt-2">Margin Top 2x</div>
    <div class="mb-3">Margin Bottom 3x</div>
    <div class="p-4">Padding 4x</div>
    
    <!-- Flex布局 -->
    <div class="flex items-center justify-between gap-2">
      <span>左侧内容</span>
      <button class="claude-btn claude-btn--primary">右侧按钮</button>
    </div>
  </div>
</template>
```

---

## ⚠️ 注意事项

### Do's ✅

1. **始终使用Parchment背景** (`#f5f4ed`)
2. **标题使用Georgia字体** + 字重500
3. **Terracotta仅用于主要CTA**
4. **所有中性色保持暖色调**
5. **使用环状阴影** (`0px 0px 0px 1px`) 替代投影
6. ** generous 圆角** (8-32px)
7. ** generous 字高** (1.60 for body)

### Don'ts ❌

1. ❌ 不使用冷蓝灰色系
2. ❌ 不对衬线字体使用粗体(700+)
3. ❌ 不引入饱和度过高的颜色
4. ❌ 不使用锐角 (<6px圆角)
5. ❌ 不使用重投影
6. ❌ 不用纯白作为页面背景
7. ❌ 不使用几何/科技风格插图

---

## 📊 待完成工作

### 1. 执行日志页面重构 ⏳

**文件**: `frontend/src/views/SqlExportLogs.vue`

需要应用相同的Claude风格：
- [ ] 页面标题区使用 `claude-heading`
- [ ] 卡片使用 `claude-card` 类
- [ ] 按钮替换为Claude按钮
- [ ] 表格样式优化
- [ ] 时间戳使用 `claude-caption`

### 2. 响应式优化 ⏳

当前断点：
- Small Mobile: <479px
- Mobile: 479-640px
- Tablet: 768-991px
- Desktop: 992px+

需要测试并优化：
- [ ] 移动端导航折叠
- [ ] 表格横向滚动
- [ ] 表单堆叠布局
- [ ] 字体大小渐进缩放

### 3. 暗色主题支持 ⏳

已在CSS变量中定义暗色主题：
```css
[data-theme='dark'] {
  --color-bg-primary: var(--color-deep-dark);
  --color-text-primary: var(--color-ivory);
  ...
}
```

需要实现：
- [ ] 主题切换开关
- [ ] localStorage持久化
- [ ] 系统偏好检测

### 4. 动画与过渡 ⏳

添加微妙的交互动画：
- [ ] 按钮悬停过渡
- [ ] 卡片悬浮效果
- [ ] 页面切换动画
- [ ] 加载骨架屏

---

## 🔗 相关资源

- [Claude设计系统原文档](通用文档/ClaudeDESIGN.md)
- [项目开发规范 - UI设计章节](../need.md#32-ui设计规范)
- [CSS设计系统源文件](../src/styles/claude-design.css)
- [App.vue全局样式](../src/App.vue)

---

## 📝 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v1.0 | 2026-04-20 | 初始实施：CSS设计系统、全局样式、任务管理页面重构 |

---

**最后更新**: 2026-04-20  
**维护者**: AI Agent  
**状态**: 🟡 进行中（核心功能已完成，待完善细节）
