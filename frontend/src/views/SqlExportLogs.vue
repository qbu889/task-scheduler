<template>
  <div class="logs-container">
    <el-card>
      <template #header>
        <span>SQL导出执行日志</span>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="任务ID">
          <el-input v-model="searchForm.task_id" placeholder="请输入任务ID" clearable />
        </el-form-item>
        <el-form-item label="执行状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadLogs">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 日志列表 -->
      <el-table :data="logList" v-loading="loading" border stripe>
        <el-table-column prop="log_id" label="日志ID" width="100" />
        <el-table-column prop="task_id" label="任务ID" width="100" />
        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column prop="end_time" label="结束时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="record_count" label="记录数" width="100" />
        <el-table-column prop="duration_seconds" label="耗时(秒)" width="100">
          <template #default="{ row }">
            {{ row.duration_seconds ? row.duration_seconds.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="file_path" label="文件路径" min-width="250" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.file_path" 
              size="small" 
              type="primary" 
              @click="downloadFile(row)"
            >
              下载
            </el-button>
            <el-button size="small" @click="showLogDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadLogs"
        @current-change="loadLogs"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 日志详情对话框 -->
    <el-dialog v-model="detailVisible" title="执行日志详情" width="1000px">
      <el-descriptions :column="2" border v-if="currentLog">
        <el-descriptions-item label="日志ID">{{ currentLog.log_id }}</el-descriptions-item>
        <el-descriptions-item label="任务ID">{{ currentLog.task_id }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ currentLog.start_time }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ currentLog.end_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <el-tag :type="currentLog.status === 'success' ? 'success' : 'danger'">
            {{ currentLog.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="记录数">{{ currentLog.record_count }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">
          {{ formatFileSize(currentLog.file_size) }}
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ currentLog.duration_seconds ? currentLog.duration_seconds.toFixed(2) + '秒' : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="文件路径" :span="2">
          {{ currentLog.file_path || '-' }}
          <el-button 
            v-if="currentLog.file_path" 
            size="small" 
            type="primary" 
            @click="downloadFile(currentLog)"
            style="margin-left: 10px;"
          >
            下载
          </el-button>
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2" v-if="currentLog.error_message">
          <el-alert :title="currentLog.error_message" type="error" :closable="false" />
        </el-descriptions-item>
        
        <el-descriptions-item label="执行SQL" :span="2" v-if="currentLog.final_sql">
          <div class="sql-display">
            <pre>{{ currentLog.final_sql }}</pre>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLogs } from '@/api/sqlExport'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const detailVisible = ref(false)
const currentLog = ref(null)

const searchForm = reactive({
  task_id: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const logList = ref([])

// 加载日志列表
const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    const res = await getLogs(params)
    logList.value = res.data
    pagination.total = res.total
  } catch (error) {
    console.error('加载日志列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.task_id = ''
  searchForm.status = ''
  pagination.page = 1
  loadLogs()
}

// 显示日志详情
const showLogDetail = (row) => {
  currentLog.value = row
  detailVisible.value = true
}

// 下载文件
const downloadFile = async (row) => {
  if (!row.log_id) {
    ElMessage.warning('日志ID不存在')
    return
  }
  
  try {
    const downloadUrl = `http://localhost:5000/api/sql-export/logs/${row.log_id}/download`
    
    // 使用 fetch 获取文件
    const response = await fetch(downloadUrl)
    
    if (!response.ok) {
      throw new Error('下载失败')
    }
    
    // 获取文件名
    const contentDisposition = response.headers.get('content-disposition')
    let filename = `file_${row.log_id}.xlsx`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (match && match[1]) {
        filename = match[1].replace(/['"]/g, '')
      }
    }
    
    // 转换为 Blob
    const blob = await response.blob()
    
    // 创建隐藏的 a 标签触发下载
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // 释放 URL
    URL.revokeObjectURL(link.href)
    
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('Download error:', error)
    ElMessage.error('下载失败: ' + error.message)
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB'
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs-container {
  padding: 20px;
}

.search-form {
  margin-bottom: 20px;
}
/* 日志详情对话框 */
.sql-display {
  width: 100%;
  max-height: 400px;
  overflow: auto;
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
}

.sql-display pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #303133;
}
</style>
