"""
Service Manager
Manages service lifecycle (start, stop, restart)
"""

import logging
from multiprocessing import Queue, Manager

from services.user_service import UserService
from services.order_service import OrderService
from services.notification_service import NotificationService
from orchestrator.registry import ServiceRegistry
from orchestrator.health_monitor import HealthMonitor

logger = logging.getLogger(__name__)


class ServiceManager:
    """
    Service Manager
    Orchestrates all services
    """
    
    def __init__(self):
        """Initialize service manager"""
        self.registry = ServiceRegistry()
        self.services = {}
        
        # Create shared memory for statistics
        manager = Manager()
        self.shared_stats = manager.dict()
        
        # Create queues for communication
        self.user_request_queue = Queue()
        self.user_response_queue = Queue()
        
        self.order_request_queue = Queue()
        self.order_response_queue = Queue()
        
        self.notification_request_queue = Queue()
        self.notification_response_queue = Queue()
        
        # Health monitor
        self.health_monitor = HealthMonitor(self.registry, self.shared_stats)
        
        logger.info("Service Manager initialized")
    
    def start_all_services(self):
        """Start all services"""
        logger.info("Starting all services...")
        
        # Start UserService
        self.start_service('UserService')
        
        # Start OrderService
        self.start_service('OrderService')
        
        # Start NotificationService
        self.start_service('NotificationService')
        
        # Start health monitoring
        self.health_monitor.start()
        
        logger.info("All services started successfully")
    
    def start_service(self, service_name):
        """
        Start a specific service
        
        Args:
            service_name: Name of service to start
        """
        if service_name in self.services:
            logger.warning(f"Service {service_name} already running")
            return
        
        try:
            if service_name == 'UserService':
                service = UserService(
                    self.user_request_queue,
                    self.user_response_queue,
                    self.shared_stats
                )
            elif service_name == 'OrderService':
                service = OrderService(
                    self.order_request_queue,
                    self.order_response_queue,
                    self.shared_stats,
                    self.user_request_queue  # OrderService needs to call UserService
                )
            elif service_name == 'NotificationService':
                service = NotificationService(
                    self.notification_request_queue,
                    self.notification_response_queue,
                    self.shared_stats
                )
            else:
                logger.error(f"Unknown service: {service_name}")
                return
            
            # Start the service
            process = service.start()
            
            # Store service instance
            self.services[service_name] = service
            
            # Register in registry
            self.registry.register(service_name, {
                'pid': process.pid,
                'request_queue': service.request_queue,
                'response_queue': service.response_queue,
                'process': process
            })
            
            logger.info(f"Service {service_name} started successfully")
            
        except Exception as e:
            logger.error(f"Error starting service {service_name}: {e}")
    
    def stop_service(self, service_name):
        """Stop a specific service"""
        if service_name not in self.services:
            logger.warning(f"Service {service_name} not running")
            return
        
        try:
            service = self.services[service_name]
            service.stop()
            
            # Remove from registry
            self.registry.deregister(service_name)
            
            # Remove from services dict
            del self.services[service_name]
            
            logger.info(f"Service {service_name} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping service {service_name}: {e}")
    
    def stop_all_services(self):
        """Stop all services"""
        logger.info("Stopping all services...")
        
        # Stop health monitor first
        self.health_monitor.stop()
        
        # Stop all services
        service_names = list(self.services.keys())
        for service_name in service_names:
            self.stop_service(service_name)
        
        logger.info("All services stopped")
    
    def get_service_queue(self, service_name):
        """Get request queue for a service"""
        if service_name == 'UserService':
            return self.user_request_queue
        elif service_name == 'OrderService':
            return self.order_request_queue
        elif service_name == 'NotificationService':
            return self.notification_request_queue
        return None
    
    def get_response_queue(self, service_name):
        """Get response queue for a service"""
        if service_name == 'UserService':
            return self.user_response_queue
        elif service_name == 'OrderService':
            return self.order_response_queue
        elif service_name == 'NotificationService':
            return self.notification_response_queue
        return None
    
    def get_service_status(self):
        """Get status of all services"""
        status = {}
        
        for service_name in self.registry.list_services():
            service_info = self.registry.get_service(service_name)
            stats = self.health_monitor.get_service_stats(service_name)
            
            status[service_name] = {
                'pid': service_info.get('pid'),
                'status': service_info.get('status'),
                'registered_at': service_info.get('registered_at'),
                'stats': stats
            }
        
        return status
