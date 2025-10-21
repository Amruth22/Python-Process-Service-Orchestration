"""
Notification Service
Handles asynchronous notification processing
"""

import logging
from services.base_service import BaseService

logger = logging.getLogger(__name__)


class NotificationService(BaseService):
    """
    Notification Service - Handles notifications
    Demonstrates asynchronous processing
    """
    
    def __init__(self, request_queue, response_queue, shared_stats, shared_lock=None):
        super().__init__('NotificationService', request_queue, response_queue, shared_stats, shared_lock)
        self.notifications_sent = 0
    
    def handle_request(self, request):
        """
        Handle notification requests
        
        Request format:
        {
            'action': 'send_notification',
            'data': {
                'user_id': 123,
                'message': 'Your order has been created',
                'type': 'email' | 'sms'
            },
            'request_id': 'unique_id'
        }
        """
        action = request.get('action')
        data = request.get('data', {})
        request_id = request.get('request_id')
        
        logger.info(f"NotificationService handling: {action}")
        
        try:
            if action == 'send_notification':
                return self.send_notification(data, request_id)
            elif action == 'get_stats':
                return self.get_stats(request_id)
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown action: {action}',
                    'request_id': request_id
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'request_id': request_id
            }
    
    def send_notification(self, data, request_id):
        """
        Send notification (simulated)
        In real application, this would send email/SMS
        """
        user_id = data.get('user_id')
        message = data.get('message')
        notification_type = data.get('type', 'email')
        
        if not user_id or not message:
            return {
                'status': 'error',
                'message': 'user_id and message are required',
                'request_id': request_id
            }
        
        # Simulate sending notification
        logger.info(f"Sending {notification_type} to user {user_id}: {message}")
        
        self.notifications_sent += 1
        
        # Update shared stats
        with self.shared_stats.get_lock():
            self.shared_stats['notifications_sent'] = self.notifications_sent
        
        return {
            'status': 'success',
            'message': f'{notification_type.capitalize()} notification sent',
            'user_id': user_id,
            'request_id': request_id
        }
    
    def get_stats(self, request_id):
        """Get notification statistics"""
        return {
            'status': 'success',
            'notifications_sent': self.notifications_sent,
            'request_id': request_id
        }
