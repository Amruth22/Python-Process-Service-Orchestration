"""
Order Service
Manages order processing and inter-service communication
"""

import logging
import uuid
from services.base_service import BaseService

logger = logging.getLogger(__name__)


class OrderService(BaseService):
    """
    Order Service - Manages order processing
    Demonstrates inter-service communication
    """
    
    def __init__(self, request_queue, response_queue, shared_stats, user_service_queue, shared_lock=None):
        super().__init__('OrderService', request_queue, response_queue, shared_stats, shared_lock)
        self.orders = {}  # In-memory order storage
        self.order_counter = 1
        self.user_service_queue = user_service_queue
    
    def handle_request(self, request):
        """
        Handle order-related requests
        
        Request format:
        {
            'action': 'create_order' | 'get_order' | 'list_orders',
            'data': {...},
            'request_id': 'unique_id'
        }
        """
        action = request.get('action')
        data = request.get('data', {})
        request_id = request.get('request_id')
        
        logger.info(f"OrderService handling: {action}")
        
        try:
            if action == 'create_order':
                return self.create_order(data, request_id)
            elif action == 'get_order':
                return self.get_order(data, request_id)
            elif action == 'list_orders':
                return self.list_orders(request_id)
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
    
    def create_order(self, data, request_id):
        """
        Create a new order
        Validates user by calling UserService
        """
        user_id = data.get('user_id')
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        if not user_id or not product:
            return {
                'status': 'error',
                'message': 'user_id and product are required',
                'request_id': request_id
            }
        
        # Validate user by calling UserService
        logger.info(f"Validating user {user_id} with UserService")
        
        validation_request = {
            'action': 'validate_user',
            'data': {'user_id': user_id},
            'request_id': str(uuid.uuid4())
        }
        
        # Send request to UserService
        self.user_service_queue.put(validation_request)
        
        # Wait for response (simplified - in production use proper async handling)
        import time
        timeout = 5
        start_time = time.time()
        validation_response = None
        
        while time.time() - start_time < timeout:
            if not self.response_queue.empty():
                response = self.response_queue.get()
                if response.get('request_id') == validation_request['request_id']:
                    validation_response = response
                    break
            time.sleep(0.1)
        
        if not validation_response:
            return {
                'status': 'error',
                'message': 'User validation timeout',
                'request_id': request_id
            }
        
        if not validation_response.get('valid'):
            return {
                'status': 'error',
                'message': f'User {user_id} not found',
                'request_id': request_id
            }
        
        # Create order
        order_id = self.order_counter
        self.orders[order_id] = {
            'id': order_id,
            'user_id': user_id,
            'product': product,
            'quantity': quantity,
            'status': 'created'
        }
        self.order_counter += 1
        
        logger.info(f"Created order: {order_id} for user {user_id}")
        
        return {
            'status': 'success',
            'message': 'Order created successfully',
            'order': self.orders[order_id],
            'request_id': request_id
        }
    
    def get_order(self, data, request_id):
        """Get order by ID"""
        order_id = data.get('order_id')
        
        if order_id not in self.orders:
            return {
                'status': 'error',
                'message': f'Order {order_id} not found',
                'request_id': request_id
            }
        
        return {
            'status': 'success',
            'order': self.orders[order_id],
            'request_id': request_id
        }
    
    def list_orders(self, request_id):
        """List all orders"""
        return {
            'status': 'success',
            'orders': list(self.orders.values()),
            'count': len(self.orders),
            'request_id': request_id
        }
