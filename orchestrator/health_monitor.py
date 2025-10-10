"""
Health Monitor
Monitors service health and performs auto-restart
"""

import time
import logging
from threading import Thread

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Simple health monitoring system
    Checks if services are alive and restarts if needed
    """
    
    def __init__(self, registry, shared_stats, check_interval=5, heartbeat_timeout=10):
        """
        Initialize health monitor
        
        Args:
            registry: ServiceRegistry instance
            shared_stats: Shared memory for statistics
            check_interval: How often to check health (seconds)
            heartbeat_timeout: Max time since last heartbeat (seconds)
        """
        self.registry = registry
        self.shared_stats = shared_stats
        self.check_interval = check_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.running = False
        self.monitor_thread = None
        
        logger.info("Health Monitor initialized")
    
    def start(self):
        """Start health monitoring in background thread"""
        self.running = True
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health Monitor started")
    
    def stop(self):
        """Stop health monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health Monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.check_all_services()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
    
    def check_all_services(self):
        """Check health of all registered services"""
        services = self.registry.get_all_services()
        
        for name, service_info in services.items():
            health_status = self.check_service_health(name, service_info)
            
            if health_status == 'healthy':
                self.registry.update_status(name, 'running')
            elif health_status == 'unhealthy':
                logger.warning(f"Service {name} is unhealthy")
                self.registry.update_status(name, 'unhealthy')
            elif health_status == 'dead':
                logger.error(f"Service {name} is dead")
                self.registry.update_status(name, 'dead')
    
    def check_service_health(self, name, service_info):
        """
        Check health of a single service
        
        Returns:
            'healthy', 'unhealthy', or 'dead'
        """
        process = service_info.get('process')
        
        # Check 1: Is process alive?
        if not process or not process.is_alive():
            return 'dead'
        
        # Check 2: Check heartbeat
        try:
            heartbeat_key = f'{name}_heartbeat'
            if heartbeat_key in self.shared_stats:
                last_heartbeat = self.shared_stats[heartbeat_key]
                time_since_heartbeat = time.time() - last_heartbeat
                
                if time_since_heartbeat > self.heartbeat_timeout:
                    return 'unhealthy'
        except Exception as e:
            logger.error(f"Error checking heartbeat for {name}: {e}")
            return 'unhealthy'
        
        return 'healthy'
    
    def get_service_stats(self, name):
        """Get statistics for a service"""
        stats = {}
        
        try:
            stats['requests'] = self.shared_stats.get(f'{name}_requests', 0)
            stats['started_at'] = self.shared_stats.get(f'{name}_started', 'unknown')
            
            heartbeat_key = f'{name}_heartbeat'
            if heartbeat_key in self.shared_stats:
                last_heartbeat = self.shared_stats[heartbeat_key]
                stats['last_heartbeat'] = time.time() - last_heartbeat
            else:
                stats['last_heartbeat'] = None
        except Exception as e:
            logger.error(f"Error getting stats for {name}: {e}")
        
        return stats
