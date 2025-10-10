"""
Comprehensive Unit Tests for Process-Based Service Orchestration
Tests multiprocessing, inter-service communication, registry, and health monitoring
"""

import unittest
import time
import requests
from multiprocessing import Process, Queue, Manager

from services.user_service import UserService
from services.order_service import OrderService
from services.notification_service import NotificationService
from orchestrator.service_manager import ServiceManager
from orchestrator.registry import ServiceRegistry
from orchestrator.health_monitor import HealthMonitor
from communication.message_protocol import MessageProtocol


class ServiceOrchestrationTestCase(unittest.TestCase):
    """Unit tests for Process-Based Service Orchestration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration - runs once before all tests"""
        print("\n" + "=" * 60)
        print("Process-Based Service Orchestration - Unit Test Suite")
        print("=" * 60)
        print("Testing: Multiprocessing, IPC, Registry, Health Monitoring")
        print("=" * 60 + "\n")
        
        # Start service manager for HTTP tests
        cls.service_manager = ServiceManager()
        cls.service_manager.start_all_services()
        
        # Give services time to start
        time.sleep(2)
        
        # Start HTTP gateway in separate process
        from gateway.api import HTTPGateway
        cls.gateway = HTTPGateway(cls.service_manager)
        
        def run_gateway():
            cls.gateway.run(host='127.0.0.1', port=5001, debug=False)
        
        cls.gateway_process = Process(target=run_gateway, daemon=True)
        cls.gateway_process.start()
        
        # Give gateway time to start
        time.sleep(2)
        
        cls.base_url = "http://127.0.0.1:5001"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        print("\n" + "=" * 60)
        print("Cleaning up...")
        print("=" * 60)
        
        # Stop gateway
        if cls.gateway_process:
            cls.gateway_process.terminate()
            cls.gateway_process.join(timeout=5)
        
        # Stop all services
        cls.service_manager.stop_all_services()
        
        print("Cleanup completed")
    
    # Test 1: Service Process Creation
    def test_01_service_process_creation(self):
        """Test that services can be created as separate processes"""
        print("\n1. Testing service process creation...")
        
        # Create queues
        request_queue = Queue()
        response_queue = Queue()
        manager = Manager()
        shared_stats = manager.dict()
        
        # Create service
        service = UserService(request_queue, response_queue, shared_stats)
        
        # Start service
        process = service.start()
        
        # Verify process is running
        self.assertIsNotNone(process)
        self.assertTrue(process.is_alive())
        print(f"   ✅ Service process created with PID: {process.pid}")
        
        # Stop service
        service.stop()
        time.sleep(0.5)
        self.assertFalse(process.is_alive())
        print("   ✅ Service process stopped successfully")
    
    # Test 2: Service Registration
    def test_02_service_registration(self):
        """Test service registry operations"""
        print("\n2. Testing service registration...")
        
        registry = ServiceRegistry()
        
        # Register a service
        registry.register('TestService', {
            'pid': 12345,
            'request_queue': None,
            'response_queue': None,
            'process': None
        })
        
        # Verify registration
        self.assertTrue(registry.is_registered('TestService'))
        print("   ✅ Service registered successfully")
        
        # Get service info
        service_info = registry.get_service('TestService')
        self.assertIsNotNone(service_info)
        self.assertEqual(service_info['pid'], 12345)
        print(f"   ✅ Service info retrieved: PID {service_info['pid']}")
        
        # List services
        services = registry.list_services()
        self.assertIn('TestService', services)
        print(f"   ✅ Service listed: {services}")
        
        # Deregister service
        registry.deregister('TestService')
        self.assertFalse(registry.is_registered('TestService'))
        print("   ✅ Service deregistered successfully")
    
    # Test 3: Queue Communication
    def test_03_queue_communication(self):
        """Test message passing via queues"""
        print("\n3. Testing queue communication...")
        
        request_queue = Queue()
        response_queue = Queue()
        manager = Manager()
        shared_stats = manager.dict()
        
        # Create and start service
        service = UserService(request_queue, response_queue, shared_stats)
        service.start()
        time.sleep(1)
        
        # Send request
        request = MessageProtocol.create_request('create_user', {
            'username': 'test_user',
            'email': 'test@example.com'
        })
        request_queue.put(request)
        print(f"   ✅ Request sent: {request['action']}")
        
        # Wait for response
        time.sleep(1)
        self.assertFalse(response_queue.empty())
        
        response = response_queue.get(timeout=2)
        self.assertEqual(response['status'], 'success')
        print(f"   ✅ Response received: {response['status']}")
        
        # Stop service
        service.stop()
    
    # Test 4: Shared Memory
    def test_04_shared_memory(self):
        """Test shared memory access between processes"""
        print("\n4. Testing shared memory...")
        
        manager = Manager()
        shared_stats = manager.dict()
        
        # Write to shared memory
        shared_stats['test_key'] = 'test_value'
        shared_stats['counter'] = 0
        
        # Verify access
        self.assertEqual(shared_stats['test_key'], 'test_value')
        self.assertEqual(shared_stats['counter'], 0)
        print("   ✅ Shared memory write successful")
        
        # Update counter
        with shared_stats.get_lock():
            shared_stats['counter'] = shared_stats['counter'] + 1
        
        self.assertEqual(shared_stats['counter'], 1)
        print(f"   ✅ Shared memory update successful: counter = {shared_stats['counter']}")
    
    # Test 5: Service Discovery
    def test_05_service_discovery(self):
        """Test finding services in registry"""
        print("\n5. Testing service discovery...")
        
        # Services should be running from setUpClass
        services = self.service_manager.registry.list_services()
        
        self.assertIn('UserService', services)
        self.assertIn('OrderService', services)
        self.assertIn('NotificationService', services)
        print(f"   ✅ Services discovered: {services}")
        
        # Get specific service
        user_service = self.service_manager.registry.get_service('UserService')
        self.assertIsNotNone(user_service)
        self.assertIsNotNone(user_service['pid'])
        print(f"   ✅ UserService found: PID {user_service['pid']}")
    
    # Test 6: Health Check
    def test_06_health_check(self):
        """Test service health monitoring"""
        print("\n6. Testing health check...")
        
        # Check UserService health
        user_service = self.service_manager.registry.get_service('UserService')
        health_status = self.service_manager.health_monitor.check_service_health(
            'UserService', user_service
        )
        
        self.assertEqual(health_status, 'healthy')
        print(f"   ✅ UserService health: {health_status}")
        
        # Get service stats
        stats = self.service_manager.health_monitor.get_service_stats('UserService')
        self.assertIsNotNone(stats)
        print(f"   ✅ Service stats retrieved: {stats}")
    
    # Test 7: Inter-Service Communication
    def test_07_inter_service_communication(self):
        """Test OrderService calling UserService"""
        print("\n7. Testing inter-service communication...")
        
        # First create a user
        user_request = MessageProtocol.create_request('create_user', {
            'username': 'order_user',
            'email': 'order@example.com'
        })
        
        user_queue = self.service_manager.get_service_queue('UserService')
        user_response_queue = self.service_manager.get_response_queue('UserService')
        
        user_queue.put(user_request)
        time.sleep(1)
        
        user_response = user_response_queue.get(timeout=2)
        self.assertEqual(user_response['status'], 'success')
        user_id = user_response['user']['id']
        print(f"   ✅ User created: ID {user_id}")
        
        # Now create an order (which will call UserService to validate)
        order_request = MessageProtocol.create_request('create_order', {
            'user_id': user_id,
            'product': 'Test Product',
            'quantity': 2
        })
        
        order_queue = self.service_manager.get_service_queue('OrderService')
        order_response_queue = self.service_manager.get_response_queue('OrderService')
        
        order_queue.put(order_request)
        time.sleep(2)  # Give time for inter-service communication
        
        order_response = order_response_queue.get(timeout=3)
        self.assertEqual(order_response['status'], 'success')
        print(f"   ✅ Order created: {order_response['order']}")
        print("   ✅ Inter-service communication successful")
    
    # Test 8: HTTP Gateway
    def test_08_http_gateway(self):
        """Test HTTP gateway endpoints"""
        print("\n8. Testing HTTP gateway...")
        
        # Test root endpoint
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        print(f"   ✅ Root endpoint: {response.status_code}")
        
        # Test health endpoint
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        print(f"   ✅ Health endpoint: {data['status']}")
        
        # Test create user via HTTP
        response = requests.post(f"{self.base_url}/users", json={
            'username': 'http_user',
            'email': 'http@example.com'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        print(f"   ✅ Create user via HTTP: {data['user']['username']}")
        
        # Test list services
        response = requests.get(f"{self.base_url}/services")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data['count'], 0)
        print(f"   ✅ List services: {data['count']} services running")
    
    # Test 9: Message Protocol
    def test_09_message_protocol(self):
        """Test message protocol format"""
        print("\n9. Testing message protocol...")
        
        # Create request
        request = MessageProtocol.create_request('test_action', {'key': 'value'})
        
        self.assertIn('action', request)
        self.assertIn('data', request)
        self.assertIn('request_id', request)
        self.assertEqual(request['action'], 'test_action')
        print(f"   ✅ Request created: {request['action']}")
        
        # Validate request
        is_valid = MessageProtocol.validate_request(request)
        self.assertTrue(is_valid)
        print("   ✅ Request validation passed")
        
        # Create response
        response = MessageProtocol.create_response(
            'success',
            {'result': 'test'},
            'Operation successful',
            request['request_id']
        )
        
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['request_id'], request['request_id'])
        print(f"   ✅ Response created: {response['status']}")
        
        # Validate response
        is_valid = MessageProtocol.validate_response(response)
        self.assertTrue(is_valid)
        print("   ✅ Response validation passed")
    
    # Test 10: Service Manager
    def test_10_service_manager(self):
        """Test service manager operations"""
        print("\n10. Testing service manager...")
        
        # Get service status
        status = self.service_manager.get_service_status()
        
        self.assertIsInstance(status, dict)
        self.assertGreater(len(status), 0)
        print(f"   ✅ Service status retrieved: {len(status)} services")
        
        # Verify all services are running
        for service_name, service_info in status.items():
            self.assertIsNotNone(service_info['pid'])
            self.assertEqual(service_info['status'], 'running')
            print(f"   ✅ {service_name}: PID {service_info['pid']}, Status: {service_info['status']}")


def run_tests():
    """Run all unit tests"""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(ServiceOrchestrationTestCase)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    if not result.failures and not result.errors:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Process-Based Service Orchestration - Unit Test Suite")
    print("=" * 60)
    
    try:
        success = run_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
