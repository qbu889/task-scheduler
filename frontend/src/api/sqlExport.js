import request from './request'

// 获取任务列表
export function getTasks(params) {
  return request({
    url: '/sql-export/tasks',
    method: 'get',
    params
  })
}

// 获取任务详情
export function getTaskById(taskId) {
  return request({
    url: `/sql-export/tasks/${taskId}`,
    method: 'get'
  })
}

// 创建任务
export function createTask(data) {
  return request({
    url: '/sql-export/tasks',
    method: 'post',
    data
  })
}

// 更新任务
export function updateTask(taskId, data) {
  return request({
    url: `/sql-export/tasks/${taskId}`,
    method: 'put',
    data
  })
}

// 删除任务
export function deleteTask(taskId) {
  return request({
    url: `/sql-export/tasks/${taskId}`,
    method: 'delete'
  })
}

// 启用任务
export function enableTask(taskId) {
  return request({
    url: `/sql-export/tasks/${taskId}/enable`,
    method: 'put'
  })
}

// 停用任务
export function disableTask(taskId) {
  return request({
    url: `/sql-export/tasks/${taskId}/disable`,
    method: 'put'
  })
}

// 手动触发任务
export function triggerTask(taskId, overrideParams) {
  return request({
    url: `/sql-export/tasks/${taskId}/trigger`,
    method: 'post',
    data: { override_time_params: overrideParams }
  })
}

// 获取执行日志
export function getLogs(params) {
  return request({
    url: '/sql-export/logs',
    method: 'get',
    params
  })
}

// 获取日志详情
export function getLogById(logId) {
  return request({
    url: `/sql-export/logs/${logId}`,
    method: 'get'
  })
}

// 测试数据源连接
export function testDatasource(config) {
  return request({
    url: '/sql-export/datasources/test',
    method: 'post',
    data: config
  })
}
