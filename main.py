"""
Process-Based Service Orchestration
Main entry point for the application
"""

import os
import signal
import sys
import logging
from dotenv import load_dotenv

from orchestrator.service_manager import ServiceManager
from gateway.api import HTTPGateway

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service manager for signal handling
service_manager = None


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logger.info("\nShutdown signal received. Stopping all services...")
    
    if service_manager:
        service_manager.stop_all_services()
    
    logger.info("All services stopped. Exiting.")
    sys.exit(0)


def main():
    """Main application entry point"""
    global service_manager
    
    print("=" * 60)
    print("Process-Based Service Orchestration")
    print("=" * 60)
    print("Starting services...")
    print("=" * 60)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create service manager
        service_manager = ServiceManager()
        
        # Start all services
        service_manager.start_all_services()
        
        print("\nAll services started successfully!")
        print("\nService Status:")
        for service_name in service_manager.registry.list_services():
            service_info = service_manager.registry.get_service(service_name)
            print(f"  - {service_name}: PID {service_info['pid']}, Status: {service_info['status']}")
        
        # Create and start HTTP Gateway
        gateway = HTTPGateway(service_manager)
        
        host = os.getenv('GATEWAY_HOST', '0.0.0.0')
        port = int(os.getenv('GATEWAY_PORT', 5000))
        debug = os.getenv('DEBUG', 'True').lower() == 'true'
        
        print("\n" + "=" * 60)
        print(f"HTTP Gateway starting on http://{host}:{port}")
        print("=" * 60)
        print("\nAvailable endpoints:")
        print("  - GET  /              - API information")
        print("  - GET  /health        - Health check")
        print("  - POST /users         - Create user")
        print("  - GET  /users         - List users")
        print("  - GET  /users/<id>    - Get user")
        print("  - POST /orders        - Create order")
        print("  - GET  /orders        - List orders")
        print("  - GET  /orders/<id>   - Get order")
        print("  - POST /notifications - Send notification")
        print("  - GET  /services      - List all services")
        print("=" * 60)
        print("\nPress Ctrl+C to stop all services\n")
        
        # Run gateway (blocking)
        gateway.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        if service_manager:
            service_manager.stop_all_services()
        sys.exit(1)


if __name__ == '__main__':
    main()
