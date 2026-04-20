"""
SQL导出API路由
"""
from flask import Blueprint, request, jsonify
from app.services.sql_export_service import sql_export_service
import logging

logger = logging.getLogger(__name__)

sql_export_bp = Blueprint('sql_export', __name__)


@sql_export_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        is_enabled = request.args.get('is_enabled', None, type=int)
        task_name = request.args.get('task_name', None)
        
        logger.info(f"Getting task list: page={page}, page_size={page_size}, is_enabled={is_enabled}, task_name={task_name}")
        
        tasks, total, page, page_size = sql_export_service.get_task_list(
            page=page, 
            page_size=page_size,
            is_enabled=is_enabled,
            task_name=task_name
        )
        
        logger.info(f"Retrieved {len(tasks)} tasks (total: {total})")
        
        return jsonify({
            'success': True,
            'data': [task.to_dict() for task in tasks],
            'total': total,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        logger.error(f"Failed to get tasks: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """获取任务详情"""
    try:
        logger.info(f"Getting task detail: task_id={task_id}")
        
        task = sql_export_service.get_task_detail(task_id)
        
        logger.info(f"Retrieved task detail: {task.task_name}")
        
        return jsonify({'success': True, 'data': task.to_dict()})
        
    except ValueError as e:
        logger.warning(f"Task not found: task_id={task_id}")
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to get task detail: task_id={task_id}, error={str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/tasks', methods=['POST'])
def create_task():
    """创建新任务"""
    try:
        config = request.get_json()
        
        logger.info(f"Creating new task: name={config.get('task_name')}, datasource_type={config.get('datasource_type')}")
        
        # 验证必填字段
        required_fields = ['task_name', 'datasource_type', 'datasource_config', 
                          'sql_template', 'time_params', 'cron_expression']
        for field in required_fields:
            if field not in config:
                logger.warning(f"Missing required field: {field}")
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        task = sql_export_service.create_task(config)
        
        logger.info(f"Task created successfully: task_id={task.task_id}, name={task.task_name}")
        
        return jsonify({
            'success': True,
            'message': 'Task created successfully',
            'data': task.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    try:
        config = request.get_json()
        logger.info(f"Updating task: task_id={task_id}")
        
        task = sql_export_service.update_task(task_id, config)
        
        logger.info(f"Task updated successfully: task_id={task_id}, name={task.task_name}")
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully',
            'data': task.to_dict()
        })
        
    except ValueError as e:
        logger.warning(f"Task not found for update: task_id={task_id}")
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to update task: task_id={task_id}, error={str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    try:
        logger.info(f"Deleting task: task_id={task_id}")
        
        sql_export_service.delete_task(task_id)
        
        logger.info(f"Task deleted successfully: task_id={task_id}")
        
        return jsonify({'success': True, 'message': 'Task deleted successfully'})
        
    except ValueError as e:
        logger.warning(f"Task not found for deletion: task_id={task_id}")
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to delete task: task_id={task_id}, error={str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/tasks/<int:task_id>/enable', methods=['PUT'])
def enable_task(task_id):
    """启用任务"""
    try:
        logger.info(f"Enabling task: task_id={task_id}")
        
        task = sql_export_service.enable_task(task_id)
        
        logger.info(f"Task enabled successfully: task_id={task_id}")
        
        return jsonify({
            'success': True,
            'message': 'Task enabled',
            'data': task.to_dict()
        })
        
    except ValueError as e:
        logger.warning(f"Task not found for enabling: task_id={task_id}")
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to enable task: task_id={task_id}, error={str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/tasks/<int:task_id>/disable', methods=['PUT'])
def disable_task(task_id):
    """停用任务"""
    try:
        logger.info(f"Disabling task: task_id={task_id}")
        
        task = sql_export_service.disable_task(task_id)
        
        logger.info(f"Task disabled successfully: task_id={task_id}")
        
        return jsonify({
            'success': True,
            'message': 'Task disabled',
            'data': task.to_dict()
        })
        
    except ValueError as e:
        logger.warning(f"Task not found for disabling: task_id={task_id}")
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to disable task: task_id={task_id}, error={str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/tasks/<int:task_id>/trigger', methods=['POST'])
def trigger_task(task_id):
    """手动触发任务执行"""
    try:
        config = request.get_json() or {}
        override_time_params = config.get('override_time_params')
        
        logger.info(f"Manually triggering task: task_id={task_id}, override_time_params={override_time_params is not None}")
        
        result = sql_export_service.execute_task(task_id, override_time_params)
        
        logger.info(f"Task execution completed: task_id={task_id}, success={result.get('success')}")
        
        return jsonify(result)
        
    except ValueError as e:
        logger.warning(f"Task not found for triggering: task_id={task_id}")
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to trigger task: task_id={task_id}, error={str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/logs', methods=['GET'])
def get_logs():
    """获取执行日志列表"""
    try:
        task_id = request.args.get('task_id', None, type=int)
        status = request.args.get('status', None)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        logs, total, page, page_size = sql_export_service.get_execution_logs(
            task_id=task_id,
            status=status,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs],
            'total': total,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        logger.error(f"Failed to get logs: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/logs/<int:log_id>', methods=['GET'])
def get_log_detail(log_id):
    """获取日志详情"""
    from app.models.sql_export_log import SqlExportLog
    
    try:
        log = SqlExportLog.query.get(log_id)
        if not log:
            return jsonify({'success': False, 'message': 'Log not found'}), 404
        
        return jsonify({'success': True, 'data': log.to_dict()})
        
    except Exception as e:
        logger.error(f"Failed to get log detail: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@sql_export_bp.route('/logs/<int:log_id>/download', methods=['GET'])
def download_log_file(log_id):
    """下载日志生成的文件"""
    from app.models.sql_export_log import SqlExportLog
    from flask import send_file
    import os
    
    try:
        log = SqlExportLog.query.get(log_id)
        if not log:
            return jsonify({'success': False, 'message': 'Log not found'}), 404
        
        if not log.file_path:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        if not os.path.exists(log.file_path):
            return jsonify({'success': False, 'message': 'File does not exist'}), 404
        
        # 提取文件名
        filename = os.path.basename(log.file_path)
        
        # 发送文件
        return send_file(
            log.file_path,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Failed to download file: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
