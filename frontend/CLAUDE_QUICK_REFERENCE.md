# Claude 设计风格 - 快速参考

## 🎨 核心色彩

```css
/* 主色 */
--color-parchment: #f5f4ed;   /* 页面背景 */
--color-ivory: #faf9f5;       /* 卡片表面 */
--color-near-black: #141413;  /* 主要文字 */
--color-terracotta: #c96442;  /* 品牌CTA */

/* 辅助色 */
--color-warm-sand: #e8e6dc;   /* 次要按钮 */
--color-olive-gray: #5e5d59;  /* 次要文字 */
--color-dark-surface: #30302e;/* 深色表面 */

/* 边框 */
--color-border-cream: #f0eee6;/* 标准边框 */
```

---

## 🔤 字体层级

| 类名 | 字号 | 用途 |
|------|------|------|
| `.claude-heading--display` | 64px | Hero标题 |
| `.claude-heading--section` | 52px | 区块标题 |
| `.claude-heading--sub` | 32px | 副标题 |
| `.claude-body--large` | 20px | 介绍段落 |
| `.claude-body` | 16px | 标准正文 |
| `.claude-caption` | 14px | 说明文字 |

**字体家族**:
- 标题: `Georgia, serif`
- 正文: `Inter, sans-serif`
- 代码: `JetBrains Mono, monospace`

---

## 🔘 按钮样式

```html
<!-- 主要CTA -->
<button class="claude-btn claude-btn--primary">保存</button>

<!-- 次要操作 -->
<button class="claude-btn claude-btn--secondary">取消</button>

<!-- 危险操作 -->
<button class="claude-btn claude-btn--danger">删除</button>

<!-- 小尺寸 -->
<button class="claude-btn claude-btn--primary claude-btn--sm">小按钮</button>
```

---

## 📦 卡片容器

```html
<!-- 标准卡片 -->
<div class="claude-card">
  内容...
</div>

<!-- 特色卡片（更大圆角） -->
<div class="claude-card claude-card--featured">
  内容...
</div>
```

---

## 📏 间距工具类

```html
<!-- Margin Top -->
<div class="mt-1">8px</div>
<div class="mt-2">16px</div>
<div class="mt-3">24px</div>
<div class="mt-4">30px</div>

<!-- Margin Bottom -->
<div class="mb-1">8px</div>
<div class="mb-2">16px</div>

<!-- Padding -->
<div class="p-1">8px</div>
<div class="p-2">16px</div>
<div class="p-3">24px</div>
<div class="p-4">30px</div>
```

---

## 🎯 Flex布局工具类

```html
<div class="flex items-center justify-between gap-2">
  <span>左侧</span>
  <button>右侧</button>
</div>
```

可用类:
- `flex` - display: flex
- `flex-col` - flex-direction: column
- `items-center` - align-items: center
- `justify-between` - justify-content: space-between
- `gap-1/2/3` - 8/16/24px 间距

---

## 💡 使用示例

### 完整页面结构

```vue
<template>
  <div class="claude-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="claude-heading claude-heading--section">页面标题</h2>
      <p class="claude-body claude-body--secondary mt-1">描述文字</p>
      <div class="mt-3">
        <button class="claude-btn claude-btn--primary">+ 新建</button>
      </div>
    </div>

    <!-- 搜索区 -->
    <div class="claude-card mt-4">
      <el-form :inline="true">
        <el-form-item label="搜索">
          <el-input class="claude-input" />
        </el-form-item>
        <el-form-item>
          <button class="claude-btn claude-btn--primary">查询</button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 列表区 -->
    <div class="claude-card mt-4">
      <el-table class="claude-table">
        <!-- 表格内容 -->
      </el-table>
      
      <div class="mt-3 flex justify-between items-center">
        <span class="claude-caption">共 100 条</span>
        <el-pagination />
      </div>
    </div>
  </div>
</template>
```

---

## ⚡ Element Plus 覆盖要点

所有Element Plus组件已自动应用Claude风格：

- ✅ `.el-card` → Ivory背景 + Cream边框
- ✅ `.el-button--primary` → Terracotta背景
- ✅ `.el-input` → Generous圆角 + Focus Blue焦点
- ✅ `.el-table th` → Warm Sand表头
- ✅ `.el-dialog` → Very圆角 + Serif标题
- ✅ `.el-tag` → Highly圆角

**无需额外配置，直接使用即可！**

---

## 🚫 禁止事项

❌ 不使用冷蓝灰色  
❌ 不对衬线字体用粗体(700+)  
❌ 不引入高饱和颜色（除Terracotta）  
❌ 不使用锐角(<6px圆角)  
❌ 不用纯白作页面背景  
❌ 不使用重投影  

---

## 📱 响应式断点

| 断点 | 宽度 | 说明 |
|------|------|------|
| Mobile | <640px | 单列布局 |
| Tablet | 768-991px | 2列网格 |
| Desktop | ≥992px | 完整布局 |

---

## 🔗 详细文档

- [完整设计系统](../styles/claude-design.css)
- [实施指南](CLAUDE_DESIGN_IMPLEMENTATION.md)
- [规范文档](../need.md#32-ui设计规范)

---

**提示**: 优先使用CSS变量和工具类，保持设计一致性！
