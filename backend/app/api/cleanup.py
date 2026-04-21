"""
文件清理API路由
"""
from flask import Blueprint, request, jsonify
from app.services.file_cleanup_service import file_cleanup_service
import logging

logger = logging.getLogger(__name__)

cleanup_bp = Blueprint('cleanup', __name__)


@cleanup_bp.route('/files', methods=['POST'])
def cleanup_files():
    """
    手动触发文件清理
    
    Query Parameters:
        retention_days (int): 保留天数，默认7天
        
    Returns:
        JSON: 清理结果统计
    """
    try:
        retention_days = request.args.get('retention_days', 7, type=int)
        
        logger.info(f"Manual file cleanup requested: retention_days={retention_days}")
        
        # 执行清理
        stats = file_cleanup_service.clean_old_files(retention_days)
        
        logger.info(f"Manual cleanup completed: deleted={stats['total_deleted']}, "
                   f"freed={stats['total_size_freed'] / 1024:.2f} KB")
        
        return jsonify({
            'success': True,
            'message': f'清理完成，删除 {stats["total_deleted"]} 个文件',
            'data': {
                'total_scanned': stats['total_scanned'],
                'total_deleted': stats['total_deleted'],
                'total_size_freed': stats['total_size_freed'],
                'total_size_freed_mb': round(stats['total_size_freed'] / 1024 / 1024, 2),
                'paths_cleaned': stats['paths_cleaned'],
                'errors': stats['errors']
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to cleanup files: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@cleanup_bp.route('/files/report', methods=['GET'])
def get_cleanup_report():
    """
    获取清理报告（预览将要删除的文件，不实际删除）
    
    Query Parameters:
        retention_days (int): 保留天数，默认7天
        
    Returns:
        JSON: 清理报告
    """
    try:
        retention_days = request.args.get('retention_days', 7, type=int)
        
        logger.info(f"Cleanup report requested: retention_days={retention_days}")
        
        # 获取报告
        report = file_cleanup_service.get_cleanup_report(retention_days)
        
        return jsonify({
            'success': True,
            'data': {
                'retention_days': report['retention_days'],
                'total_scanned': report['total_scanned'],
                'files_to_delete_count': len(report['files_to_delete']),
                'total_size_to_free': report['total_size_to_free'],
                'total_size_to_free_mb': round(report['total_size_to_free'] / 1024 / 1024, 2),
                'files_to_delete': report['files_to_delete'],
                'errors': report['errors']
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get cleanup report: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@cleanup_bp.route('/files/task/<int:task_id>', methods=['POST'])
def cleanup_task_files(task_id):
    """
    清理指定任务的过期文件
    
    Args:
        task_id: 任务ID
        
    Query Parameters:
        retention_days (int): 保留天数，默认7天
        
    Returns:
        JSON: 清理结果统计
    """
    try:
        retention_days = request.args.get('retention_days', 7, type=int)
        
        logger.info(f"Task file cleanup requested: task_id={task_id}, retention_days={retention_days}")
        
        # 执行清理
        stats = file_cleanup_service.cleanup_by_task_id(task_id, retention_days)
        
        logger.info(f"Task {task_id} cleanup completed: deleted={stats['total_deleted']}")
        
        return jsonify({
            'success': True,
            'message': f'任务清理完成，删除 {stats["total_deleted"]} 个文件',
            'data': stats
        })
        
    except ValueError as e:
        logger.warning(f"Task not found: task_id={task_id}")
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to cleanup task files: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
