"""
User Service
Manages user data and operations
"""

import logging
from services.base_service import BaseService

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """
    User Service - Manages user CRUD operations
    Runs as a separate process
    """
    
    def __init__(self, request_queue, response_queue, shared_stats, shared_lock=None):
        super().__init__('UserService', request_queue, response_queue, shared_stats, shared_lock)
        self.users = {}  # In-memory user storage
        self.user_counter = 1
    
    def handle_request(self, request):
        """
        Handle user-related requests
        
        Request format:
        {
            'action': 'create_user' | 'get_user' | 'list_users',
            'data': {...},
            'request_id': 'unique_id'
        }
        """
        action = request.get('action')
        data = request.get('data', {})
        request_id = request.get('request_id')
        
        logger.info(f"UserService handling: {action}")
        
        try:
            if action == 'create_user':
                return self.create_user(data, request_id)
            elif action == 'get_user':
                return self.get_user(data, request_id)
            elif action == 'list_users':
                return self.list_users(request_id)
            elif action == 'validate_user':
                return self.validate_user(data, request_id)
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
    
    def create_user(self, data, request_id):
        """Create a new user"""
        username = data.get('username')
        email = data.get('email')
        
        if not username or not email:
            return {
                'status': 'error',
                'message': 'Username and email are required',
                'request_id': request_id
            }
        
        # Check if user already exists
        for user in self.users.values():
            if user['username'] == username:
                return {
                    'status': 'error',
                    'message': f'User {username} already exists',
                    'request_id': request_id
                }
        
        # Create user
        user_id = self.user_counter
        self.users[user_id] = {
            'id': user_id,
            'username': username,
            'email': email
        }
        self.user_counter += 1
        
        logger.info(f"Created user: {username} (ID: {user_id})")
        
        return {
            'status': 'success',
            'message': 'User created successfully',
            'user': self.users[user_id],
            'request_id': request_id
        }
    
    def get_user(self, data, request_id):
        """Get user by ID"""
        user_id = data.get('user_id')
        
        if user_id not in self.users:
            return {
                'status': 'error',
                'message': f'User {user_id} not found',
                'request_id': request_id
            }
        
        return {
            'status': 'success',
            'user': self.users[user_id],
            'request_id': request_id
        }
    
    def list_users(self, request_id):
        """List all users"""
        return {
            'status': 'success',
            'users': list(self.users.values()),
            'count': len(self.users),
            'request_id': request_id
        }
    
    def validate_user(self, data, request_id):
        """Validate if user exists"""
        user_id = data.get('user_id')
        
        exists = user_id in self.users
        
        return {
            'status': 'success',
            'valid': exists,
            'user_id': user_id,
            'request_id': request_id
        }
