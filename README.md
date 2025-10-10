# Process-Based Service Orchestration

Educational Python application demonstrating **process-based service orchestration**, **Python multiprocessing**, **inter-service communication**, **shared memory**, **service registry**, and **health monitoring**.

## Features

### 🔄 Process-Based Services
- **UserService** - User management running as separate process
- **OrderService** - Order processing with inter-service calls
- **NotificationService** - Asynchronous notification handling
- Each service runs in its own OS process with isolated memory

### 🔗 Inter-Service Communication
- **Queue-based messaging** - Asynchronous message passing between services
- **Request/Response pattern** - Structured communication protocol
- **Message Protocol** - Standard format for all messages
- **Timeout handling** - Graceful handling of slow services

### 💾 Shared Memory
- **Shared statistics** - Real-time metrics across all services
- **Heartbeat tracking** - Service health monitoring
- **Request counters** - Track service usage
- **Thread-safe access** - Proper synchronization

### 📋 Service Registry
- **Service registration** - Automatic service discovery
- **Metadata storage** - PID, queues, status tracking
- **Service lookup** - Find services by name
- **Status management** - Track service health states

### 🏥 Health Monitoring
- **Process health checks** - Verify processes are alive
- **Heartbeat monitoring** - Detect unresponsive services
- **Auto-restart** - Recover from failures (configurable)
- **Statistics tracking** - Monitor service performance

### 🌐 HTTP Gateway
- **REST API** - Easy access to services via HTTP
- **Flask-based** - Simple and familiar interface
- **Service proxy** - Gateway pattern implementation
- **JSON responses** - Standard API format

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Amruth22/Python-Process-Service-Orchestration.git
cd Python-Process-Service-Orchestration
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

The application will start all services and the HTTP gateway on `http://localhost:5000`

### 5. Run Tests
```bash
python tests.py
```

## Project Structure

```
Python-Process-Service-Orchestration/
│
├── services/
│   ├── base_service.py          # Base service class
│   ├── user_service.py          # User management service
│   ├── order_service.py         # Order processing service
│   └── notification_service.py  # Notification service
│
├── orchestrator/
│   ├── service_manager.py       # Service lifecycle management
│   ├── registry.py              # Service registry
│   └── health_monitor.py        # Health monitoring
│
├── communication/
│   └── message_protocol.py      # Message format standard
│
├── gateway/
│   └── api.py                   # HTTP gateway (Flask)
│
├── main.py                      # Application entry point
├── tests.py                     # Unit tests (10 tests)
├── requirements.txt             # Dependencies
├── .env                         # Configuration
└── README.md                    # This file
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      HTTP Gateway (Flask)                    │
│                    http://localhost:5000                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Service Manager                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Service Registry                         │  │
│  │  - UserService: PID 1234, Queue A, Status: Running   │  │
│  │  - OrderService: PID 1235, Queue B, Status: Running  │  │
│  │  - NotificationService: PID 1236, Queue C, Running   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Health Monitor                           │  │
│  │  - Checks process health every 5 seconds             │  │
│  │  - Monitors heartbeats                                │  │
│  │  - Auto-restart on failure                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────────┐ ┌▼────────────────┐
│ UserService  │ │OrderService │ │NotificationSvc  │
│  (Process 1) │ │ (Process 2) │ │  (Process 3)    │
│              │ │             │ │                 │
│ Queue: A     │ │ Queue: B    │ │ Queue: C        │
│ PID: 1234    │ │ PID: 1235   │ │ PID: 1236       │
└──────────────┘ └─────────────┘ └─────────────────┘
        │                │                │
        └────────────────┴────────────────┘
                         │
                ┌────────▼────────┐
                │  Shared Memory  │
                │  - Statistics   │
                │  - Heartbeats   │
                │  - Counters     │
                └─────────────────┘
```

## API Endpoints

### Root & Health

#### Get API Information
```http
GET /
```

**Response:**
```json
{
  "message": "Process-Based Service Orchestration API",
  "version": "1.0.0",
  "endpoints": {
    "users": "/users",
    "orders": "/orders",
    "notifications": "/notifications",
    "services": "/services"
  }
}
```

#### Health Check
```http
GET /health
```

### User Endpoints

#### Create User
```http
POST /users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com"
}
```

#### Get User
```http
GET /users/{user_id}
```

#### List Users
```http
GET /users
```

### Order Endpoints

#### Create Order
```http
POST /orders
Content-Type: application/json

{
  "user_id": 1,
  "product": "Laptop",
  "quantity": 2
}
```

**Note:** OrderService validates user by calling UserService

#### Get Order
```http
GET /orders/{order_id}
```

#### List Orders
```http
GET /orders
```

### Notification Endpoints

#### Send Notification
```http
POST /notifications
Content-Type: application/json

{
  "user_id": 1,
  "message": "Your order has been created",
  "type": "email"
}
```

### Service Management

#### List All Services
```http
GET /services
```

**Response:**
```json
{
  "status": "success",
  "services": {
    "UserService": {
      "pid": 1234,
      "status": "running",
      "stats": {
        "requests": 10,
        "last_heartbeat": 0.5
      }
    }
  },
  "count": 3
}
```

#### Check Service Health
```http
GET /services/{service_name}/health
```

## Usage Examples

### Using cURL

#### Create a User
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com"
  }'
```

#### Create an Order
```bash
curl -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "product": "Smartphone",
    "quantity": 1
  }'
```

#### List All Services
```bash
curl http://localhost:5000/services
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Create a user
response = requests.post(f"{BASE_URL}/users", json={
    "username": "bob",
    "email": "bob@example.com"
})
print(response.json())

# Create an order
response = requests.post(f"{BASE_URL}/orders", json={
    "user_id": 1,
    "product": "Laptop",
    "quantity": 2
})
print(response.json())

# Check service health
response = requests.get(f"{BASE_URL}/services/UserService/health")
print(response.json())
```

## How It Works

### 1. Process-Based Architecture

Each service runs in its own OS process:
```python
# Each service is a separate process
user_process = Process(target=user_service.run)
order_process = Process(target=order_service.run)

user_process.start()  # Starts in new process
order_process.start()  # Starts in another new process
```

**Benefits:**
- True parallelism (no GIL limitations)
- Fault isolation (one crash doesn't affect others)
- Separate memory spaces
- Can utilize multiple CPU cores

### 2. Inter-Service Communication

Services communicate via queues:
```python
# OrderService sends request to UserService
request = {
    'action': 'validate_user',
    'data': {'user_id': 123},
    'request_id': 'unique-id'
}
user_service_queue.put(request)

# UserService processes and responds
response = user_service_queue.get()
# Process request...
response_queue.put(response)
```

### 3. Shared Memory

Services share statistics via Manager:
```python
# Create shared memory
manager = Manager()
shared_stats = manager.dict()

# Services update shared stats
with shared_stats.get_lock():
    shared_stats['requests'] = shared_stats.get('requests', 0) + 1
```

### 4. Service Registry

Tracks all running services:
```python
registry.register('UserService', {
    'pid': process.pid,
    'status': 'running',
    'queue': request_queue
})

# Later, find the service
service_info = registry.get_service('UserService')
```

### 5. Health Monitoring

Monitors service health:
```python
# Check if process is alive
if process.is_alive():
    status = 'healthy'

# Check heartbeat
last_heartbeat = shared_stats['UserService_heartbeat']
if time.now() - last_heartbeat > 10:
    status = 'unhealthy'
```

## Testing

Run the comprehensive test suite:

```bash
python tests.py
```

### Test Coverage (10 Tests)

1. ✅ **Service Process Creation** - Test process spawning
2. ✅ **Service Registration** - Test registry operations
3. ✅ **Queue Communication** - Test message passing
4. ✅ **Shared Memory** - Test shared data access
5. ✅ **Service Discovery** - Test finding services
6. ✅ **Health Check** - Test health monitoring
7. ✅ **Inter-Service Communication** - Test service-to-service calls
8. ✅ **HTTP Gateway** - Test REST API endpoints
9. ✅ **Message Protocol** - Test message format
10. ✅ **Service Manager** - Test orchestration

### Test Output Example

```
1. Testing service process creation...
   ✅ Service process created with PID: 12345
   ✅ Service process stopped successfully

2. Testing service registration...
   ✅ Service registered successfully
   ✅ Service info retrieved: PID 12345
   ✅ Service listed: ['TestService']
   ✅ Service deregistered successfully
```

## Educational Notes

### 1. Process vs Thread

**Process:**
- Separate memory space
- True parallelism
- Heavier resource usage
- Better isolation

**Thread:**
- Shared memory space
- GIL limitations in Python
- Lighter resource usage
- Less isolation

**When to use processes:**
- CPU-intensive tasks
- Need true parallelism
- Want fault isolation
- Microservices architecture

### 2. Inter-Process Communication (IPC)

**Queue:**
- Thread-safe message passing
- FIFO order
- Good for async communication
- Used in this project

**Pipe:**
- Two-way communication
- Faster for 1-to-1
- Direct connection
- Not used (kept simple)

**Shared Memory:**
- Fastest IPC method
- Requires synchronization
- Good for shared state
- Used for statistics

### 3. Service Orchestration

**Key Concepts:**
- **Service Registry** - Know what's running
- **Health Monitoring** - Keep services alive
- **Graceful Shutdown** - Clean exit
- **Inter-Service Calls** - Services working together

### 4. Microservices Patterns

This project demonstrates:
- **Service Discovery** - Registry pattern
- **Health Checks** - Monitoring pattern
- **API Gateway** - Gateway pattern
- **Message Passing** - Async communication

## Configuration

Edit `.env` file:

```env
# Service Configuration
SERVICE_CHECK_INTERVAL=5
MAX_RESTART_ATTEMPTS=3
HEARTBEAT_TIMEOUT=10

# HTTP Gateway
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=5000
DEBUG=True

# Logging
LOG_LEVEL=INFO
```

## Production Considerations

For production use:

1. **Persistence:**
   - Replace in-memory storage with database
   - Add data persistence layer
   - Implement state recovery

2. **Scalability:**
   - Use Redis for shared memory
   - Implement load balancing
   - Add horizontal scaling

3. **Reliability:**
   - Implement retry logic
   - Add circuit breakers
   - Improve error handling

4. **Monitoring:**
   - Add metrics collection
   - Implement logging aggregation
   - Set up alerting

5. **Security:**
   - Add authentication
   - Implement authorization
   - Secure inter-service communication

## Dependencies

- **Flask 3.0.0** - HTTP gateway
- **python-dotenv 1.0.0** - Environment variables
- **pytest 7.4.3** - Testing framework
- **requests 2.31.0** - HTTP client for tests

## Troubleshooting

### Services not starting
- Check if ports are available
- Verify Python version (3.7+)
- Check logs for errors

### Communication timeout
- Increase timeout in `.env`
- Check if services are running
- Verify queue connections

### Tests failing
- Ensure no other instance is running
- Check port 5001 is available
- Run tests with verbose output

## License

This project is for educational purposes. Feel free to use and modify as needed.

## Additional Resources

- [Python multiprocessing documentation](https://docs.python.org/3/library/multiprocessing.html)
- [Microservices patterns](https://microservices.io/patterns/)
- [Process-based parallelism](https://realpython.com/python-concurrency/)

---

**Happy Learning! 🚀**
