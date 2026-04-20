# Task Scheduler 前端

基于 Vue 3 + Element Plus + Vite 构建的 SQL 导出任务管理系统前端。

## 技术栈

- **框架**: Vue 3.4+
- **UI库**: Element Plus 2.5+
- **构建工具**: Vite 5.0+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios 1.6+
- **SQL编辑器**: Monaco Editor

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

生成的文件在 `dist/` 目录

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口封装
│   │   ├── request.js    # Axios 实例和拦截器
│   │   └── sqlExport.js  # SQL导出相关API
│   ├── components/       # 公共组件
│   ├── views/            # 页面组件
│   │   ├── SqlExportTasks.vue    # 任务管理页面
│   │   └── SqlExportLogs.vue     # 执行日志页面
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── store/            # Pinia 状态管理
│   ├── utils/            # 工具函数
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── public/               # 静态资源
├── index.html            # HTML 模板
├── vite.config.js        # Vite 配置
└── package.json          # 依赖配置
```

## 功能模块

### 1. SQL任务管理 (`/tasks`)

- 任务列表展示（分页、搜索、筛选）
- 新建/编辑/删除任务
- 启用/停用任务
- 手动触发任务执行
- 配置项：
  - 任务名称
  - 数据源类型（MySQL/达梦）
  - SQL模板（支持占位符 :start_time, :end_time）
  - Cron表达式
  - 导出路径和文件名前缀
  - 最大记录数和分页大小

### 2. 执行日志 (`/logs`)

- 日志列表展示（分页、搜索、筛选）
- 查看执行详情
  - 执行时间
  - 执行状态
  - 记录数
  - 文件大小
  - 耗时
  - 错误信息

## API 代理配置

开发环境下，Vite 会自动将 `/api` 请求代理到后端：

```javascript
// vite.config.js
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:5000',
      changeOrigin: true
    }
  }
}
```

确保后端服务运行在 `http://127.0.0.1:5000`

## 环境变量

创建 `.env` 文件（可选）：

```env
# 后端API地址
VITE_API_BASE_URL=http://127.0.0.1:5000/api

# 其他配置...
```

## 部署

### 方案1：Nginx 部署

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/task-scheduler/dist;
    index index.html;
    
    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 反向代理
    location /api {
        proxy_pass http://backend-server:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 方案2：IIS 部署（Windows Server）

1. 安装 URL Rewrite 模块
2. 创建 `web.config`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="API Proxy" stopProcessing="true">
          <match url="^api/(.*)" />
          <action type="Rewrite" url="http://localhost:5000/api/{R:1}" />
        </rule>
        <rule name="SPA Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/index.html" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

## 开发规范

- 使用 Composition API (`<script setup>`)
- 组件命名：PascalCase（如 `SqlExportTasks.vue`）
- 变量/函数命名：camelCase
- 常量命名：UPPER_SNAKE_CASE
- 所有 API 调用统一放在 `src/api/` 目录
- 使用 Element Plus 组件库，保持UI一致性

## 常见问题

### 1. 跨域问题

开发环境已通过 Vite 代理解决，生产环境需配置 Nginx/IIS 反向代理。

### 2. 路由刷新404

确保 Web 服务器配置了 SPA 路由回退（见部署部分）。

### 3. 后端连接失败

检查：
- 后端服务是否启动
- `vite.config.js` 中的代理配置是否正确
- 防火墙是否允许端口访问

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

---

**注意**: 本项目需要配合后端 Flask 服务使用，请确保后端服务已正确启动。
