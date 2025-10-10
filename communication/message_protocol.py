"""
Message Protocol
Defines standard message format for inter-service communication
"""

import uuid
import logging

logger = logging.getLogger(__name__)


class MessageProtocol:
    """
    Standard message format for service communication
    """
    
    @staticmethod
    def create_request(action, data=None):
        """
        Create a standard request message
        
        Args:
            action: Action to perform
            data: Request data
            
        Returns:
            Dictionary with standard format
        """
        return {
            'action': action,
            'data': data or {},
            'request_id': str(uuid.uuid4())
        }
    
    @staticmethod
    def create_response(status, data=None, message=None, request_id=None):
        """
        Create a standard response message
        
        Args:
            status: 'success' or 'error'
            data: Response data
            message: Response message
            request_id: Original request ID
            
        Returns:
            Dictionary with standard format
        """
        response = {
            'status': status,
            'request_id': request_id
        }
        
        if data:
            response.update(data)
        
        if message:
            response['message'] = message
        
        return response
    
    @staticmethod
    def validate_request(request):
        """
        Validate request format
        
        Args:
            request: Request dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['action', 'request_id']
        
        for field in required_fields:
            if field not in request:
                logger.error(f"Invalid request: missing {field}")
                return False
        
        return True
    
    @staticmethod
    def validate_response(response):
        """
        Validate response format
        
        Args:
            response: Response dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['status', 'request_id']
        
        for field in required_fields:
            if field not in response:
                logger.error(f"Invalid response: missing {field}")
                return False
        
        if response['status'] not in ['success', 'error']:
            logger.error(f"Invalid response status: {response['status']}")
            return False
        
        return True
