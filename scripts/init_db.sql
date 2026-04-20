-- ============================================
-- task-scheduler 数据库初始化脚本（MySQL版本）
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS task_scheduler_dev 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE task_scheduler_dev;

-- ============================================
-- SQL导出任务配置表
-- ============================================
CREATE TABLE IF NOT EXISTS sql_export_task (
    task_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '任务ID',
    task_name VARCHAR(200) NOT NULL COMMENT '任务名称',
    datasource_type VARCHAR(50) NOT NULL COMMENT '数据源类型：mysql/dm',
    datasource_config TEXT NOT NULL COMMENT '数据源配置JSON（密码已加密）',
    sql_template TEXT NOT NULL COMMENT 'SQL模板',
    time_params TEXT NOT NULL COMMENT '时间参数配置JSON',
    cron_expression VARCHAR(100) NOT NULL COMMENT 'Cron表达式',
    export_path VARCHAR(500) NOT NULL COMMENT '导出路径',
    filename_prefix VARCHAR(100) NOT NULL COMMENT '文件名前缀',
    max_rows INT DEFAULT 100000 COMMENT '最大记录数',
    batch_size INT DEFAULT 5000 COMMENT '分页大小',
    is_enabled SMALLINT DEFAULT 1 COMMENT '是否启用：0-停用 1-启用',
    description TEXT COMMENT '任务描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_is_enabled (is_enabled),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='SQL导出任务配置表';

-- ============================================
-- SQL导出执行日志表
-- ============================================
CREATE TABLE IF NOT EXISTS sql_export_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    task_id INT NOT NULL COMMENT '任务ID',
    start_time DATETIME NOT NULL COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    status VARCHAR(20) NOT NULL COMMENT '执行状态：success/failed',
    record_count INT DEFAULT 0 COMMENT '记录数',
    file_path VARCHAR(500) COMMENT '文件路径',
    file_size BIGINT COMMENT '文件大小（字节）',
    duration_seconds FLOAT COMMENT '耗时（秒）',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (task_id) REFERENCES sql_export_task(task_id) ON DELETE CASCADE,
    INDEX idx_task_id (task_id),
    INDEX idx_start_time (start_time),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='SQL导出执行日志表';

-- ============================================
-- 插入示例数据（可选）
-- ============================================
-- 注意：实际使用时，密码需要加密后存储
-- 这里仅作为示例，展示数据结构

/*
INSERT INTO sql_export_task (
    task_name, 
    datasource_type, 
    datasource_config, 
    sql_template, 
    time_params, 
    cron_expression, 
    export_path, 
    filename_prefix,
    description
) VALUES (
    '泉州遗留库工单日报',
    'mysql',
    '{"host":"127.0.0.1","port":3306,"user":"root","password":"encrypted_password","database":"task_scheduler_dev","charset":"utf8mb4"}',
    'SELECT * FROM your_table WHERE CREATE_TIME BETWEEN :start_time AND :end_time',
    '{"start_time":{"type":"fixed","value":"2025-01-01 00:00:00"},"end_time":{"type":"relative","offset_days":-1,"time_of_day":"23:59:59"}}',
    '0 0 2 * * *',
    './exports/',
    '泉州遗留库工单',
    '每日导出泉州地区遗留库工单数据'
);
*/

-- ============================================
-- 完成提示
-- ============================================
SELECT 'Database initialization completed successfully!' AS message;
