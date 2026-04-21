<template>
  <div class="claude-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <h2 class="claude-heading claude-heading--section">SQL导出任务管理</h2>
      <p class="claude-body claude-body--secondary mt-1">
        配置和管理定时 SQL 数据导出任务，支持 MySQL 和达梦数据库
      </p>
      <div class="mt-3">
        <button class="claude-btn claude-btn--primary" @click="showCreateDialog">
          <span>+ 新建任务</span>
        </button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="claude-card mt-4">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="任务名称">
          <el-input 
            v-model="searchForm.task_name" 
            placeholder="请输入任务名称" 
            clearable 
            class="claude-input"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="searchForm.is_enabled" 
            placeholder="请选择" 
            clearable
            style="width: 120px;"
          >
            <el-option label="启用" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <button class="claude-btn claude-btn--primary" @click="loadTasks">查询</button>
          <button class="claude-btn claude-btn--secondary" @click="resetSearch">重置</button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 任务列表 -->
    <div class="claude-card mt-4">
      <el-table 
        :data="taskList" 
        v-loading="loading" 
        border 
        stripe
        class="claude-table"
      >
        <el-table-column prop="task_id" label="ID" width="80" />
        <el-table-column prop="task_name" label="任务名称" min-width="200">
          <template #default="{ row }">
            <strong>{{ row.task_name }}</strong>
          </template>
        </el-table-column>
        <el-table-column prop="datasource_type" label="数据源" width="120">
          <template #default="{ row }">
            <el-tag :type="row.datasource_type === 'mysql' ? 'success' : 'warning'" size="small">
              {{ row.datasource_type === 'mysql' ? 'MySQL' : '达梦' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cron_expression" label="Cron表达式" width="150">
          <template #default="{ row }">
            <code class="claude-code">{{ row.cron_expression }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="is_enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled === 1 ? 'success' : 'info'" size="small">
              {{ row.is_enabled === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <button class="claude-btn claude-btn--secondary claude-btn--sm" @click="showEditDialog(row)">
              编辑
            </button>
            <button 
              class="claude-btn claude-btn--sm"
              :class="row.is_enabled === 1 ? 'claude-btn--secondary' : 'claude-btn--primary'"
              @click="toggleTaskStatus(row)"
            >
              {{ row.is_enabled === 1 ? '停用' : '启用' }}
            </button>
            <button class="claude-btn claude-btn--primary claude-btn--sm" @click="triggerTaskExecute(row)">
              执行
            </button>
            <button class="claude-btn claude-btn--danger claude-btn--sm" @click="handleDelete(row)">
              删除
            </button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="mt-3 flex justify-between items-center">
        <span class="claude-caption">
          共 {{ pagination.total }} 条记录
        </span>
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="sizes, prev, pager, next"
          @size-change="loadTasks"
          @current-change="loadTasks"
        />
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="resetForm"
      class="claude-dialog"
    >
      <el-form :model="taskForm" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="任务名称" prop="task_name">
          <el-input 
            v-model="taskForm.task_name" 
            placeholder="请输入任务名称" 
            class="claude-input"
          />
        </el-form-item>
        <el-form-item label="数据源类型" prop="datasource_type">
          <el-radio-group v-model="taskForm.datasource_type">
            <el-radio label="mysql">MySQL</el-radio>
            <el-radio label="dm">达梦数据库</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- MySQL数据源配置 -->
        <template v-if="taskForm.datasource_type === 'mysql'">
          <el-form-item label="主机地址" prop="datasource_config.host">
            <el-input 
              v-model="taskForm.datasource_config.host" 
              placeholder="127.0.0.1" 
              class="claude-input"
            />
          </el-form-item>
          <el-form-item label="端口" prop="datasource_config.port">
            <el-input-number 
              v-model="taskForm.datasource_config.port" 
              :min="1" 
              :max="65535"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="用户名" prop="datasource_config.user">
            <el-input 
              v-model="taskForm.datasource_config.user" 
              placeholder="root" 
              class="claude-input"
            />
          </el-form-item>
          <el-form-item label="密码" prop="datasource_config.password">
            <el-input 
              v-model="taskForm.datasource_config.password" 
              type="password"
              placeholder="请输入密码" 
              show-password
              class="claude-input"
            />
          </el-form-item>
          <el-form-item label="数据库名" prop="datasource_config.database">
            <el-input 
              v-model="taskForm.datasource_config.database" 
              placeholder="请输入数据库名" 
              class="claude-input"
            />
          </el-form-item>
          <el-form-item label="字符集">
            <el-input 
              v-model="taskForm.datasource_config.charset" 
              placeholder="utf8mb4" 
              class="claude-input"
            />
          </el-form-item>
        </template>
        
        <!-- 达梦数据库配置 -->
        <template v-if="taskForm.datasource_type === 'dm'">
          <el-form-item label="主机地址" prop="datasource_config.host">
            <el-input 
              v-model="taskForm.datasource_config.host" 
              placeholder="127.0.0.1" 
              class="claude-input"
            />
          </el-form-item>
          <el-form-item label="端口" prop="datasource_config.port">
            <el-input-number 
              v-model="taskForm.datasource_config.port" 
              :min="1" 
              :max="65535"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="用户名" prop="datasource_config.user">
            <el-input 
              v-model="taskForm.datasource_config.user" 
              placeholder="SYSDBA" 
              class="claude-input"
            />
          </el-form-item>
          <el-form-item label="密码" prop="datasource_config.password">
            <el-input 
              v-model="taskForm.datasource_config.password" 
              type="password"
              placeholder="请输入密码" 
              show-password
              class="claude-input"
            />
          </el-form-item>
          <el-form-item label="数据库名" prop="datasource_config.database">
            <el-input 
              v-model="taskForm.datasource_config.database" 
              placeholder="请输入数据库名" 
              class="claude-input"
            />
          </el-form-item>
          <el-form-item label="字符集">
            <el-input 
              v-model="taskForm.datasource_config.charset" 
              placeholder="utf8" 
              class="claude-input"
            />
          </el-form-item>
        </template>
        <el-form-item label="SQL模板" prop="sql_template">
          <el-input
            v-model="taskForm.sql_template"
            type="textarea"
            :rows="8"
            placeholder="请输入SQL查询语句，使用 :start_time 和 :end_time 作为时间占位符"
            class="claude-textarea"
          />
          <div class="form-tip claude-caption mt-1">
            💡 提示：使用 <code class="claude-code">:start_time</code> 和 <code class="claude-code">:end_time</code> 作为时间参数占位符
          </div>
        </el-form-item>
        
        <!-- 时间参数配置 -->
        <el-form-item label="时间参数配置">
          <div style="width: 100%;">
            <div class="time-params-section">
              <div class="time-param-item">
                <label class="param-label">开始时间 (start_time)</label>
                <el-radio-group v-model="taskForm.time_params.start_time.type" style="margin-bottom: 8px;">
                  <el-radio label="relative">相对时间</el-radio>
                  <el-radio label="fixed">固定时间</el-radio>
                </el-radio-group>
                
                <template v-if="taskForm.time_params.start_time.type === 'relative'">
                  <div style="display: flex; gap: 10px; align-items: center;">
                    <span>偏移天数：</span>
                    <el-input-number v-model="taskForm.time_params.start_time.offset_days" :min="-365" :max="365" style="width: 120px;" />
                    <span>时间：</span>
                    <el-time-picker v-model="taskForm.time_params.start_time.time_of_day" format="HH:mm:ss" value-format="HH:mm:ss" style="width: 120px;" />
                  </div>
                  <div class="time-preview" style="margin-top: 8px; padding: 8px; background: #f5f7fa; border-radius: 4px;">
                    <span class="preview-label" style="color: #909399; font-size: 12px;">实际时间：</span>
                    <span class="preview-value" style="color: #409eff; font-weight: 500;">{{ computedStartTime }}</span>
                  </div>
                </template>
                
                <template v-if="taskForm.time_params.start_time.type === 'fixed'">
                  <el-date-picker 
                    v-model="taskForm.time_params.start_time.fixed_time" 
                    type="datetime" 
                    placeholder="选择日期时间" 
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    style="width: 100%;"
                  />
                </template>
              </div>
              
              <div class="time-param-item" style="margin-top: 16px;">
                <label class="param-label">结束时间 (end_time)</label>
                <el-radio-group v-model="taskForm.time_params.end_time.type" style="margin-bottom: 8px;">
                  <el-radio label="relative">相对时间</el-radio>
                  <el-radio label="fixed">固定时间</el-radio>
                </el-radio-group>
                
                <template v-if="taskForm.time_params.end_time.type === 'relative'">
                  <div style="display: flex; gap: 10px; align-items: center;">
                    <span>偏移天数：</span>
                    <el-input-number v-model="taskForm.time_params.end_time.offset_days" :min="-365" :max="365" style="width: 120px;" />
                    <span>时间：</span>
                    <el-time-picker v-model="taskForm.time_params.end_time.time_of_day" format="HH:mm:ss" value-format="HH:mm:ss" style="width: 120px;" />
                  </div>
                  <div class="time-preview" style="margin-top: 8px; padding: 8px; background: #f5f7fa; border-radius: 4px;">
                    <span class="preview-label" style="color: #909399; font-size: 12px;">实际时间：</span>
                    <span class="preview-value" style="color: #409eff; font-weight: 500;">{{ computedEndTime }}</span>
                  </div>
                </template>
                
                <template v-if="taskForm.time_params.end_time.type === 'fixed'">
                  <el-date-picker 
                    v-model="taskForm.time_params.end_time.fixed_time" 
                    type="datetime" 
                    placeholder="选择日期时间" 
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    style="width: 100%;"
                  />
                </template>
              </div>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="Cron表达式" prop="cron_expression">
          <!-- Cron生成器 -->
          <div class="cron-builder" style="margin-bottom: 12px;">
            <el-radio-group v-model="cronConfig.frequency" @change="generateCron" style="margin-bottom: 12px;">
              <el-radio label="minute">每N分钟</el-radio>
              <el-radio label="hourly">每小时</el-radio>
              <el-radio label="daily">每天</el-radio>
              <el-radio label="weekly">每周</el-radio>
              <el-radio label="monthly">每月</el-radio>
              <el-radio label="custom">自定义</el-radio>
            </el-radio-group>
            
            <!-- 每N分钟 -->
            <div v-if="cronConfig.frequency === 'minute'" style="display: flex; align-items: center; gap: 10px;">
              <span>每</span>
              <el-input-number v-model="cronConfig.minuteInterval" :min="1" :max="59" @change="generateCron" style="width: 100px;" />
              <span>分钟执行一次</span>
            </div>
            
            <!-- 每小时 -->
            <div v-if="cronConfig.frequency === 'hourly'" style="display: flex; align-items: center; gap: 10px;">
              <span>每小时的第</span>
              <el-input-number v-model="cronConfig.minute" :min="0" :max="59" @change="generateCron" style="width: 100px;" />
              <span>分钟执行</span>
            </div>
            
            <!-- 每天 -->
            <div v-if="cronConfig.frequency === 'daily'" style="display: flex; align-items: center; gap: 10px;">
              <span>每天</span>
              <el-time-picker 
                v-model="cronConfig.dailyTime" 
                format="HH:mm" 
                value-format="HH:mm" 
                @change="generateCron"
                style="width: 120px;" 
              />
              <span>执行</span>
            </div>
            
            <!-- 每周 -->
            <div v-if="cronConfig.frequency === 'weekly'" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <span>每周</span>
              <el-select v-model="cronConfig.weekDay" @change="generateCron" style="width: 100px;">
                <el-option label="周一" value="1" />
                <el-option label="周二" value="2" />
                <el-option label="周三" value="3" />
                <el-option label="周四" value="4" />
                <el-option label="周五" value="5" />
                <el-option label="周六" value="6" />
                <el-option label="周日" value="0" />
              </el-select>
              <el-time-picker 
                v-model="cronConfig.dailyTime" 
                format="HH:mm" 
                value-format="HH:mm" 
                @change="generateCron"
                style="width: 120px;" 
              />
              <span>执行</span>
            </div>
            
            <!-- 每月 -->
            <div v-if="cronConfig.frequency === 'monthly'" style="display: flex; align-items: center; gap: 10px;">
              <span>每月</span>
              <el-input-number v-model="cronConfig.monthDay" :min="1" :max="28" @change="generateCron" style="width: 100px;" />
              <span>日</span>
              <el-time-picker 
                v-model="cronConfig.dailyTime" 
                format="HH:mm" 
                value-format="HH:mm" 
                @change="generateCron"
                style="width: 120px;" 
              />
              <span>执行</span>
            </div>
            
            <!-- 自定义提示 -->
            <div v-if="cronConfig.frequency === 'custom'" style="color: #909399; font-size: 12px;">
              请在下方手动输入Cron表达式
            </div>
          </div>
          
          <!-- Cron表达式显示 -->
          <el-input 
            v-model="taskForm.cron_expression" 
            placeholder="Cron表达式将自动生成或手动输入" 
            class="claude-input"
            @input="onCronInputChange"
          />
          
          <!-- 下次执行时间预览 -->
          <div v-if="taskForm.cron_expression && nextRunTimes.length > 0" class="cron-preview" style="margin-top: 8px; padding: 8px; background: #f0f9ff; border-left: 3px solid #409eff; border-radius: 4px;">
            <div style="color: #409eff; font-size: 13px; font-weight: 500; margin-bottom: 4px;">
              下次执行时间预览：
            </div>
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <div v-for="(time, index) in nextRunTimes" :key="index" style="color: #606266; font-size: 12px;">
                第{{ index + 1 }}次：{{ formatDateTime(time) }}
              </div>
            </div>
          </div>
          
          <div class="form-tip claude-caption mt-1">
            🕐 5字段格式（分 时 日 月 周），例：<br>
            <code class="claude-code">*/2 * * * *</code> - 每2分钟 | 
            <code class="claude-code">0 2 * * *</code> - 每天凌晨2点
          </div>
        </el-form-item>
        <el-form-item label="导出路径" prop="export_path">
          <el-input 
            v-model="taskForm.export_path" 
            placeholder="例如: D:/exports/" 
            class="claude-input"
          />
        </el-form-item>
        <el-form-item label="文件名前缀" prop="filename_prefix">
          <el-input 
            v-model="taskForm.filename_prefix" 
            placeholder="例如: 泉州遗留库工单" 
            class="claude-input"
          />
        </el-form-item>
        <el-form-item label="最大记录数">
          <el-input-number v-model="taskForm.max_rows" :min="1000" :max="5000000" />
        </el-form-item>
        <el-form-item label="分页大小">
          <el-input-number v-model="taskForm.batch_size" :min="1000" :max="10000" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="taskForm.is_enabled" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input
            v-model="taskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
            class="claude-textarea"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="claude-btn claude-btn--secondary" @click="dialogVisible = false">
          取消
        </button>
        <button 
          class="claude-btn claude-btn--primary" 
          @click="handleSubmit" 
          :disabled="submitting"
        >
          {{ submitting ? '提交中...' : '确定' }}
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTasks, createTask, updateTask, deleteTask, enableTask, disableTask, triggerTask } from '@/api/sqlExport'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新建任务')
const formRef = ref(null)

// 用于取消上一次请求
let abortController = null

const searchForm = reactive({
  task_name: '',
  is_enabled: null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const taskList = ref([])

const taskForm = reactive({
  task_id: null,
  task_name: '',
  datasource_type: 'mysql',
  datasource_config: {
    host: '127.0.0.1',
    port: 3306,
    user: 'root',
    password: '',
    database: '',
    charset: 'utf8mb4'
  },
  sql_template: '',
  time_params: {
    start_time: {
      type: 'relative',
      offset_days: -7,
      time_of_day: '00:00:00',
      fixed_time: ''  // 固定时间（当type='fixed'时使用）
    },
    end_time: {
      type: 'relative',
      offset_days: -1,
      time_of_day: '23:59:59',
      fixed_time: ''  // 固定时间（当type='fixed'时使用）
    }
  },
  cron_expression: '',
  export_path: 'D:/exports/',
  filename_prefix: '',
  max_rows: 100000,
  batch_size: 5000,
  is_enabled: 1,
  description: ''
})

// Cron配置
const cronConfig = reactive({
  frequency: 'daily', // minute, hourly, daily, weekly, monthly, custom
  minuteInterval: 2,
  minute: 0,
  dailyTime: '02:00',
  weekDay: '1',
  monthDay: 1
})

// 下次执行时间
const nextRunTimes = ref([])

const rules = {
  task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  datasource_type: [{ required: true, message: '请选择数据源类型', trigger: 'change' }],
  sql_template: [{ required: true, message: '请输入SQL模板', trigger: 'blur' }],
  cron_expression: [{ required: true, message: '请输入Cron表达式', trigger: 'blur' }],
  export_path: [{ required: true, message: '请输入导出路径', trigger: 'blur' }],
  filename_prefix: [{ required: true, message: '请输入文件名前缀', trigger: 'blur' }]
}

// 计算实际时间
const computedStartTime = computed(() => {
  const startParam = taskForm.time_params.start_time
  if (startParam.type === 'fixed') {
    return startParam.fixed_time || '-'
  }
  
  // 相对时间计算
  const now = new Date()
  const offsetDays = startParam.offset_days || 0
  const timeOfDay = startParam.time_of_day || '00:00:00'
  
  const targetDate = new Date(now.getTime() + offsetDays * 24 * 60 * 60 * 1000)
  const [hours, minutes, seconds] = timeOfDay.split(':').map(Number)
  
  targetDate.setHours(hours, minutes, seconds, 0)
  
  return formatDateTime(targetDate)
})

const computedEndTime = computed(() => {
  const endParam = taskForm.time_params.end_time
  if (endParam.type === 'fixed') {
    return endParam.fixed_time || '-'
  }
  
  // 相对时间计算
  const now = new Date()
  const offsetDays = endParam.offset_days || 0
  const timeOfDay = endParam.time_of_day || '23:59:59'
  
  const targetDate = new Date(now.getTime() + offsetDays * 24 * 60 * 60 * 1000)
  const [hours, minutes, seconds] = timeOfDay.split(':').map(Number)
  
  targetDate.setHours(hours, minutes, seconds, 0)
  
  return formatDateTime(targetDate)
})

const formatDateTime = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 生成Cron表达式
const generateCron = () => {
  let cron = ''
  
  switch (cronConfig.frequency) {
    case 'minute':
      cron = `*/${cronConfig.minuteInterval} * * * *`
      break
    case 'hourly':
      cron = `${cronConfig.minute} * * * *`
      break
    case 'daily': {
      const [hour, minute] = cronConfig.dailyTime.split(':').map(Number)
      cron = `${minute} ${hour} * * *`
      break
    }
    case 'weekly': {
      const [hour, minute] = cronConfig.dailyTime.split(':').map(Number)
      cron = `${minute} ${hour} * * ${cronConfig.weekDay}`
      break
    }
    case 'monthly': {
      const [hour, minute] = cronConfig.dailyTime.split(':').map(Number)
      cron = `${minute} ${hour} ${cronConfig.monthDay} * *`
      break
    }
    case 'custom':
      // 自定义模式不自动生成
      return
  }
  
  taskForm.cron_expression = cron
  calculateNextRunTimes()
}

// 解析手动输入的Cron表达式
const onCronInputChange = () => {
  // 当用户手动输入时，切换到自定义模式
  cronConfig.frequency = 'custom'
  calculateNextRunTimes()
}

// 解析手动输入的Cron表达式（已废弃，使用onCronInputChange）
const parseCron = () => {
  const cron = taskForm.cron_expression.trim()
  if (!cron) return
  
  calculateNextRunTimes()
}

// 计算下次执行时间
const calculateNextRunTimes = () => {
  const cron = taskForm.cron_expression.trim()
  if (!cron) {
    nextRunTimes.value = []
    return
  }
  
  try {
    const parts = cron.split(/\s+/)
    if (parts.length !== 5) {
      nextRunTimes.value = []
      return
    }
    
    const [minute, hour, day, month, weekDay] = parts
    const times = []
    const now = new Date()
    
    // 简化的下次执行时间计算（仅支持常见模式）
    for (let i = 0; i < 3; i++) {
      const nextTime = calculateNextTime(now, { minute, hour, day, month, weekDay }, i)
      if (nextTime) {
        times.push(nextTime)
      }
    }
    
    nextRunTimes.value = times
  } catch (e) {
    nextRunTimes.value = []
  }
}

// 计算下一次执行时间
const calculateNextTime = (fromTime, cron, offset = 0) => {
  const { minute, hour, day, month, weekDay } = cron
  
  // 解析字段值
  const parseField = (field, min, max) => {
    if (field === '*') return null
    if (field.includes('/')) {
      const [, step] = field.split('/')
      return { step: parseInt(step), base: min }
    }
    return parseInt(field)
  }
  
  const minuteVal = parseField(minute, 0, 59)
  const hourVal = parseField(hour, 0, 23)
  const dayVal = parseField(day, 1, 31)
  const monthVal = parseField(month, 1, 12)
  const weekDayVal = parseField(weekDay, 0, 6)
  
  // 简化计算：对于常见模式给出近似值
  const next = new Date(fromTime.getTime())
  
  if (minute.includes('/') && hour === '*') {
    // 每N分钟
    const step = parseInt(minute.split('/')[1])
    next.setMinutes(next.getMinutes() + step * (offset + 1))
    return next
  }
  
  if (hour !== '*' && minute !== '*') {
    // 具体时间
    const targetHour = parseInt(hour)
    const targetMinute = parseInt(minute)
    
    next.setHours(targetHour, targetMinute, 0, 0)
    
    if (next <= fromTime || offset > 0) {
      // 需要加一天
      if (weekDay !== '*') {
        // 每周的某天
        const targetWeekDay = parseInt(weekDay)
        const currentWeekDay = next.getDay()
        let daysToAdd = (targetWeekDay - currentWeekDay + 7) % 7
        if (daysToAdd === 0 && (next <= fromTime || offset > 0)) {
          daysToAdd = 7
        }
        next.setDate(next.getDate() + daysToAdd * (offset + (next <= fromTime ? 0 : 1)))
      } else if (day !== '*') {
        // 每月的某天
        next.setMonth(next.getMonth() + (offset + (next <= fromTime ? 1 : 0)))
      } else {
        // 每天
        next.setDate(next.getDate() + (offset + (next <= fromTime ? 1 : 0)))
      }
    }
    
    return next
  }
  
  return null
}

// 加载任务列表
const loadTasks = async () => {
  // 取消上一次未完成的请求
  if (abortController) {
    abortController.abort()
  }
  
  // 创建新的 AbortController
  abortController = new AbortController()
  
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    const res = await getTasks(params, abortController.signal)
    taskList.value = res.data
    pagination.total = res.total
  } catch (error) {
    // 如果是请求被取消，忽略错误
    if (error.name !== 'AbortError') {
      console.error('加载任务列表失败:', error)
    }
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.task_name = ''
  searchForm.is_enabled = null
  pagination.page = 1
  loadTasks()
}

// 显示创建对话框
const showCreateDialog = () => {
  dialogTitle.value = '新建任务'
  resetForm()
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogTitle.value = '编辑任务'
  
  // 深拷贝避免引用问题
  Object.assign(taskForm, row)
  
  // 解析JSON字符串为对象
  if (typeof taskForm.datasource_config === 'string') {
    taskForm.datasource_config = JSON.parse(taskForm.datasource_config)
  }
  
  if (typeof taskForm.time_params === 'string') {
    taskForm.time_params = JSON.parse(taskForm.time_params)
  }
  
  // 初始化time_params的fixed_time字段
  if (!taskForm.time_params.start_time.fixed_time) {
    taskForm.time_params.start_time.fixed_time = ''
  }
  if (!taskForm.time_params.end_time.fixed_time) {
    taskForm.time_params.end_time.fixed_time = ''
  }
  
  // 解析已有的Cron表达式
  if (row.cron_expression) {
    parseExistingCron(row.cron_expression)
  }
  
  dialogVisible.value = true
}

// 解析已有的Cron表达式
const parseExistingCron = (cron) => {
  if (!cron) return
  
  const parts = cron.trim().split(/\s+/)
  if (parts.length !== 5) return
  
  const [minute, hour, day, month, weekDay] = parts
  
  // 尝试识别模式
  if (minute.includes('/') && hour === '*' && day === '*' && month === '*' && weekDay === '*') {
    // 每N分钟
    cronConfig.frequency = 'minute'
    cronConfig.minuteInterval = parseInt(minute.split('/')[1])
  } else if (minute !== '*' && hour === '*' && day === '*' && month === '*' && weekDay === '*') {
    // 每小时
    cronConfig.frequency = 'hourly'
    cronConfig.minute = parseInt(minute)
  } else if (minute !== '*' && hour !== '*' && day === '*' && month === '*' && weekDay === '*') {
    // 每天
    cronConfig.frequency = 'daily'
    cronConfig.dailyTime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
  } else if (minute !== '*' && hour !== '*' && day === '*' && month === '*' && weekDay !== '*') {
    // 每周
    cronConfig.frequency = 'weekly'
    cronConfig.weekDay = weekDay
    cronConfig.dailyTime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
  } else if (minute !== '*' && hour !== '*' && day !== '*' && month === '*' && weekDay === '*') {
    // 每月
    cronConfig.frequency = 'monthly'
    cronConfig.monthDay = parseInt(day)
    cronConfig.dailyTime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
  } else {
    // 自定义
    cronConfig.frequency = 'custom'
  }
  
  // 计算下次执行时间
  calculateNextRunTimes()
}

// 重置表单
const resetForm = () => {
  Object.assign(taskForm, {
    task_id: null,
    task_name: '',
    datasource_type: 'mysql',
    datasource_config: {
      host: '127.0.0.1',
      port: 3306,
      user: 'root',
      password: '',
      database: '',
      charset: 'utf8mb4'
    },
    sql_template: '',
    time_params: {
      start_time: {
        type: 'relative',
        offset_days: -7,
        time_of_day: '00:00:00',
        fixed_time: ''  // 固定时间（当type='fixed'时使用）
      },
      end_time: {
        type: 'relative',
        offset_days: -1,
        time_of_day: '23:59:59',
        fixed_time: ''  // 固定时间（当type='fixed'时使用）
      }
    },
    cron_expression: '',
    export_path: 'D:/exports/',
    filename_prefix: '',
    max_rows: 100000,
    batch_size: 5000,
    is_enabled: 1,
    description: ''
  })
  
  // 重置Cron配置
  Object.assign(cronConfig, {
    frequency: 'daily',
    minuteInterval: 2,
    minute: 0,
    dailyTime: '02:00',
    weekDay: '1',
    monthDay: 1
  })
  nextRunTimes.value = []
  
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (taskForm.task_id) {
        await updateTask(taskForm.task_id, taskForm)
        ElMessage.success('更新成功')
      } else {
        await createTask(taskForm)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadTasks()
    } catch (error) {
      console.error('提交失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

// 切换任务状态
const toggleTaskStatus = async (row) => {
  try {
    if (row.is_enabled === 1) {
      await disableTask(row.task_id)
      ElMessage.success('已停用')
    } else {
      await enableTask(row.task_id)
      ElMessage.success('已启用')
    }
    loadTasks()
  } catch (error) {
    console.error('切换状态失败:', error)
  }
}

// 手动触发执行
const triggerTaskExecute = async (row) => {
  try {
    await ElMessageBox.confirm('确定要立即执行此任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await triggerTask(row.task_id)
    ElMessage.success('任务已提交执行')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('触发执行失败:', error)
    }
  }
}

// 删除任务
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此任务吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteTask(row.task_id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
/* ===== 页面级样式 - Claude风格 ===== */

.claude-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-5xl);
}

.page-header h2 {
  margin: 0 0 var(--space-base) 0;
}

.page-header p {
  margin: 0;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2xl);
  align-items: flex-end;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.search-form :deep(.el-form-item__label) {
  font-weight: var(--weight-medium);
  color: var(--color-near-black);
}

.form-tip {
  margin-top: var(--space-base);
  padding-left: var(--space-base);
}

/* 时间参数配置区域 */
.time-params-section {
  background-color: var(--color-ivory);
  border: 1px solid var(--color-border-cream);
  border-radius: var(--radius-comfortable);
  padding: var(--space-xl);
}

.time-param-item {
  padding: var(--space-lg);
  background-color: white;
  border-radius: var(--radius-comfortable);
}

.param-label {
  display: block;
  font-weight: var(--weight-medium);
  color: var(--color-near-black);
  margin-bottom: var(--space-lg);
  font-size: var(--text-body);
}

/* 对话框中的表单 */
:deep(.claude-dialog) {
  /* 已在App.vue中全局定义 */
}

:deep(.el-form-item) {
  margin-bottom: var(--space-4xl);
}

:deep(.el-form-item__label) {
  font-family: var(--font-sans);
  font-weight: var(--weight-medium);
  color: var(--color-near-black);
}

/* 单选按钮组 */
:deep(.el-radio-group) {
  display: flex;
  gap: var(--space-2xl);
}

:deep(.el-radio__label) {
  color: var(--color-near-black);
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  color: var(--color-near-black);
  font-weight: var(--weight-medium);
}

/* 数字输入框 */
:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-input-number .el-input__wrapper) {
  background-color: var(--color-ivory);
  border-radius: var(--radius-generous);
}

/* 开关 */
:deep(.el-switch) {
  --el-switch-on-color: var(--color-terracotta);
}

/* 表格优化 */
.claude-table {
  width: 100%;
}

:deep(.claude-table .el-table__header th) {
  font-family: var(--font-sans);
  font-weight: var(--weight-medium);
  font-size: var(--text-body-sm);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  color: var(--color-charcoal-warm);
  background-color: var(--color-warm-sand);
  padding: var(--space-xl) var(--space-lg);
}

:deep(.claude-table .el-table__body td) {
  padding: var(--space-xl) var(--space-lg);
  color: var(--color-near-black);
}

:deep(.claude-table .el-table__row:hover > td) {
  background-color: var(--color-warm-sand) !important;
}

/* 操作按钮组 */
:deep(.el-table .cell) {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-header h2 {
    font-size: var(--text-subheading);
  }
  
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  :deep(.el-table) {
    font-size: var(--text-body-sm);
  }
}
</style>
