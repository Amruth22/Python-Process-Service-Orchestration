"""
HTTP Gateway
Flask API for accessing process-based services
"""

import time
import uuid
from flask import Flask, request, jsonify
from communication.message_protocol import MessageProtocol
import logging

logger = logging.getLogger(__name__)


class HTTPGateway:
    """
    HTTP Gateway for service access
    Provides REST API to interact with process-based services
    """
    
    def __init__(self, service_manager):
        """
        Initialize HTTP Gateway
        
        Args:
            service_manager: ServiceManager instance
        """
        self.service_manager = service_manager
        self.app = Flask(__name__)
        self.setup_routes()
        
        logger.info("HTTP Gateway initialized")
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Root endpoint"""
            return jsonify({
                'message': 'Process-Based Service Orchestration API',
                'version': '1.0.0',
                'endpoints': {
                    'users': '/users',
                    'orders': '/orders',
                    'notifications': '/notifications',
                    'services': '/services',
                    'health': '/health'
                }
            })
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'message': 'Gateway is running'
            })
        
        # User endpoints
        @self.app.route('/users', methods=['POST'])
        def create_user():
            """Create a new user"""
            data = request.get_json()
            
            if not data or 'username' not in data or 'email' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'username and email are required'
                }), 400
            
            response = self._send_request('UserService', 'create_user', data)
            
            if response and response.get('status') == 'success':
                return jsonify(response), 201
            else:
                return jsonify(response or {'status': 'error', 'message': 'Service timeout'}), 500
        
        @self.app.route('/users/<int:user_id>', methods=['GET'])
        def get_user(user_id):
            """Get user by ID"""
            response = self._send_request('UserService', 'get_user', {'user_id': user_id})
            
            if response and response.get('status') == 'success':
                return jsonify(response), 200
            else:
                return jsonify(response or {'status': 'error', 'message': 'Service timeout'}), 404
        
        @self.app.route('/users', methods=['GET'])
        def list_users():
            """List all users"""
            response = self._send_request('UserService', 'list_users', {})
            
            if response and response.get('status') == 'success':
                return jsonify(response), 200
            else:
                return jsonify(response or {'status': 'error', 'message': 'Service timeout'}), 500
        
        # Order endpoints
        @self.app.route('/orders', methods=['POST'])
        def create_order():
            """Create a new order"""
            data = request.get_json()
            
            if not data or 'user_id' not in data or 'product' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'user_id and product are required'
                }), 400
            
            response = self._send_request('OrderService', 'create_order', data)
            
            if response and response.get('status') == 'success':
                return jsonify(response), 201
            else:
                return jsonify(response or {'status': 'error', 'message': 'Service timeout'}), 500
        
        @self.app.route('/orders/<int:order_id>', methods=['GET'])
        def get_order(order_id):
            """Get order by ID"""
            response = self._send_request('OrderService', 'get_order', {'order_id': order_id})
            
            if response and response.get('status') == 'success':
                return jsonify(response), 200
            else:
                return jsonify(response or {'status': 'error', 'message': 'Service timeout'}), 404
        
        @self.app.route('/orders', methods=['GET'])
        def list_orders():
            """List all orders"""
            response = self._send_request('OrderService', 'list_orders', {})
            
            if response and response.get('status') == 'success':
                return jsonify(response), 200
            else:
                return jsonify(response or {'status': 'error', 'message': 'Service timeout'}), 500
        
        # Notification endpoints
        @self.app.route('/notifications', methods=['POST'])
        def send_notification():
            """Send a notification"""
            data = request.get_json()
            
            if not data or 'user_id' not in data or 'message' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'user_id and message are required'
                }), 400
            
            response = self._send_request('NotificationService', 'send_notification', data)
            
            if response and response.get('status') == 'success':
                return jsonify(response), 200
            else:
                return jsonify(response or {'status': 'error', 'message': 'Service timeout'}), 500
        
        # Service management endpoints
        @self.app.route('/services', methods=['GET'])
        def list_services():
            """List all services and their status"""
            status = self.service_manager.get_service_status()
            
            return jsonify({
                'status': 'success',
                'services': status,
                'count': len(status)
            }), 200
        
        @self.app.route('/services/<service_name>/health', methods=['GET'])
        def check_service_health(service_name):
            """Check health of a specific service"""
            service_info = self.service_manager.registry.get_service(service_name)
            
            if not service_info:
                return jsonify({
                    'status': 'error',
                    'message': f'Service {service_name} not found'
                }), 404
            
            health_status = self.service_manager.health_monitor.check_service_health(
                service_name, service_info
            )
            
            stats = self.service_manager.health_monitor.get_service_stats(service_name)
            
            return jsonify({
                'status': 'success',
                'service': service_name,
                'health': health_status,
                'stats': stats
            }), 200
    
    def _send_request(self, service_name, action, data, timeout=5):
        """
        Send request to a service and wait for response
        
        Args:
            service_name: Name of target service
            action: Action to perform
            data: Request data
            timeout: Response timeout in seconds
            
        Returns:
            Response dictionary or None on timeout
        """
        # Get service queues
        request_queue = self.service_manager.get_service_queue(service_name)
        response_queue = self.service_manager.get_response_queue(service_name)
        
        if not request_queue or not response_queue:
            logger.error(f"Service {service_name} not found")
            return {'status': 'error', 'message': f'Service {service_name} not found'}
        
        # Create request
        req = MessageProtocol.create_request(action, data)
        request_id = req['request_id']
        
        # Send request
        request_queue.put(req)
        logger.info(f"Sent request to {service_name}: {action}")
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not response_queue.empty():
                response = response_queue.get()
                if response.get('request_id') == request_id:
                    return response
            time.sleep(0.1)
        
        logger.warning(f"Request to {service_name} timed out")
        return None
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        logger.info(f"Starting HTTP Gateway on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)
