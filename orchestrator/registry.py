"""
Service Registry
Tracks all running services and their metadata
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Simple service registry
    Keeps track of all running services
    """
    
    def __init__(self):
        self.services = {}
        logger.info("Service Registry initialized")
    
    def register(self, name, service_info):
        """
        Register a service
        
        Args:
            name: Service name
            service_info: Dictionary with service metadata
        """
        self.services[name] = {
            'name': name,
            'pid': service_info.get('pid'),
            'status': 'running',
            'registered_at': datetime.now().isoformat(),
            'request_queue': service_info.get('request_queue'),
            'response_queue': service_info.get('response_queue'),
            'process': service_info.get('process')
        }
        logger.info(f"Service registered: {name} (PID: {service_info.get('pid')})")
    
    def deregister(self, name):
        """Remove a service from registry"""
        if name in self.services:
            del self.services[name]
            logger.info(f"Service deregistered: {name}")
    
    def get_service(self, name):
        """Get service information by name"""
        return self.services.get(name)
    
    def list_services(self):
        """List all registered services"""
        return list(self.services.keys())
    
    def get_all_services(self):
        """Get all service information"""
        return self.services
    
    def update_status(self, name, status):
        """Update service status"""
        if name in self.services:
            self.services[name]['status'] = status
            logger.info(f"Service {name} status updated to: {status}")
    
    def is_registered(self, name):
        """Check if service is registered"""
        return name in self.services
