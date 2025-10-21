"""
Base Service Class
Provides common functionality for all services
"""

import time
import logging
from multiprocessing import Process, Queue
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseService:
    """
    Base class for all services
    Each service runs in its own process
    """

    def __init__(self, name, request_queue, response_queue, shared_stats, shared_lock=None):
        """
        Initialize base service

        Args:
            name: Service name
            request_queue: Queue for incoming requests
            response_queue: Queue for outgoing responses
            shared_stats: Shared memory for statistics
            shared_lock: Lock for synchronizing access to shared_stats
        """
        self.name = name
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.shared_stats = shared_stats
        self.shared_lock = shared_lock
        self.running = False
        self.process = None

        logger.info(f"Service {self.name} initialized")
    
    def start(self):
        """Start the service in a separate process"""
        self.process = Process(target=self.run, name=self.name)
        self.process.start()
        logger.info(f"Service {self.name} started with PID {self.process.pid}")
        return self.process
    
    def run(self):
        """
        Main service loop - runs in separate process
        Override this method in child classes
        """
        self.running = True
        logger.info(f"Service {self.name} running in process {self.process.pid if self.process else 'unknown'}")

        # Update shared stats
        with self.shared_lock:
            self.shared_stats[f'{self.name}_started'] = datetime.now().isoformat()
            self.shared_stats[f'{self.name}_requests'] = 0

        while self.running:
            try:
                # Check for incoming requests
                if not self.request_queue.empty():
                    request = self.request_queue.get(timeout=1)

                    # Update request count
                    with self.shared_lock:
                        key = f'{self.name}_requests'
                        self.shared_stats[key] = self.shared_stats.get(key, 0) + 1

                    # Process request
                    response = self.handle_request(request)

                    # Send response
                    if response:
                        self.response_queue.put(response)

                # Send heartbeat
                self.send_heartbeat()

                # Small sleep to prevent CPU spinning
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in {self.name}: {e}")
    
    def handle_request(self, request):
        """
        Handle incoming request
        Override this method in child classes
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary
        """
        logger.info(f"{self.name} received request: {request}")
        return {'status': 'success', 'service': self.name}
    
    def send_heartbeat(self):
        """Send heartbeat to indicate service is alive"""
        with self.shared_lock:
            self.shared_stats[f'{self.name}_heartbeat'] = time.time()
    
    def stop(self):
        """Stop the service"""
        self.running = False
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=5)
            logger.info(f"Service {self.name} stopped")
    
    def is_alive(self):
        """Check if service process is alive"""
        return self.process and self.process.is_alive()
    
    def get_pid(self):
        """Get process ID"""
        return self.process.pid if self.process else None
