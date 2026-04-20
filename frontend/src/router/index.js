import { createRouter, createWebHistory } from 'vue-router'
import SqlExportTasks from '../views/SqlExportTasks.vue'
import SqlExportLogs from '../views/SqlExportLogs.vue'

const routes = [
  {
    path: '/',
    redirect: '/tasks'
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: SqlExportTasks
  },
  {
    path: '/logs',
    name: 'Logs',
    component: SqlExportLogs
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
