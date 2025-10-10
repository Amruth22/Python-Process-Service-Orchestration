# MCQ Questions - Process-Based Service Orchestration

## Instructions
Choose the best answer for each question. Each question has only one correct answer.

---

### Question 1: Process vs Thread
What is the main advantage of using processes over threads in Python for CPU-intensive tasks?

A) Processes use less memory than threads  
B) Processes can bypass Python's Global Interpreter Lock (GIL) and achieve true parallelism  
C) Processes are easier to create than threads  
D) Processes share memory automatically without synchronization  

**Answer: B**

---

### Question 2: Multiprocessing Module
In Python's multiprocessing module, which method is used to start a new process?

A) `process.run()`  
B) `process.execute()`  
C) `process.start()`  
D) `process.begin()`  

**Answer: C**

---

### Question 3: Inter-Process Communication
Which IPC mechanism is best suited for asynchronous message passing between multiple processes in a producer-consumer pattern?

A) Shared memory with locks  
B) multiprocessing.Queue  
C) Global variables  
D) File-based communication  

**Answer: B**

---

### Question 4: Shared Memory
When using multiprocessing.Manager().dict() for shared memory, why is it important to use locks?

A) Locks make the code run faster  
B) Locks are required by Python syntax  
C) Locks prevent race conditions when multiple processes access shared data simultaneously  
D) Locks reduce memory usage  

**Answer: C**

---

### Question 5: Service Registry Pattern
What is the primary purpose of a service registry in a microservices architecture?

A) To store user authentication credentials  
B) To enable service discovery by tracking available services and their metadata  
C) To compile and execute service code  
D) To encrypt inter-service communication  

**Answer: B**

---

### Question 6: Health Monitoring
In a health monitoring system, what does a "heartbeat" mechanism typically indicate?

A) The CPU usage of a service  
B) The memory consumption of a process  
C) That a service is alive and responsive by sending periodic signals  
D) The number of requests a service has processed  

**Answer: C**

---

### Question 7: Process Isolation
What is a key benefit of process isolation in a service-oriented architecture?

A) All services can share the same variables directly  
B) If one service crashes, it doesn't affect other services running in separate processes  
C) Process isolation makes services run faster  
D) Isolated processes use less total memory  

**Answer: B**

---

### Question 8: Message Protocol
Why is it important to have a standard message protocol for inter-service communication?

A) To make the code look more organized  
B) To ensure consistent message format, easier debugging, and reliable communication between services  
C) To reduce the size of messages  
D) To eliminate the need for error handling  

**Answer: B**

---

### Question 9: Queue Communication
What happens when you call `queue.get()` on an empty multiprocessing.Queue without a timeout?

A) It returns None immediately  
B) It raises an exception immediately  
C) It blocks and waits until an item is available  
D) It returns an empty string  

**Answer: C**

---

### Question 10: Service Orchestration
In service orchestration, what does "graceful shutdown" mean?

A) Immediately terminating all processes  
B) Allowing services to complete in-flight requests and cleanup resources before stopping  
C) Shutting down services in alphabetical order  
D) Restarting services automatically  

**Answer: B**

---

### Question 11: Multiprocessing Manager
What is the role of multiprocessing.Manager() in Python?

A) It manages CPU cores allocation  
B) It provides a way to create shared objects that can be accessed by multiple processes  
C) It automatically restarts failed processes  
D) It compiles Python code for better performance  

**Answer: B**

---

### Question 12: Process Communication Timeout
Why is it important to implement timeouts when waiting for responses from other services?

A) Timeouts make the system faster  
B) Timeouts are required by Python  
C) Timeouts prevent indefinite blocking if a service is slow or unresponsive  
D) Timeouts reduce memory usage  

**Answer: C**

---

### Question 13: Gateway Pattern
What is the main purpose of an API Gateway in a microservices architecture?

A) To store all service data in one place  
B) To provide a single entry point for clients to access multiple backend services  
C) To replace all other services  
D) To encrypt all data automatically  

**Answer: B**

---

### Question 14: Process vs Thread Memory
How does memory management differ between processes and threads?

A) Processes share the same memory space; threads have separate memory  
B) Processes and threads both share all memory  
C) Processes have separate memory spaces; threads share memory within the same process  
D) There is no difference in memory management  

**Answer: C**

---

### Question 15: Service Health States
In a health monitoring system, which state indicates a service is running but responding slowly?

A) HEALTHY - Service is functioning normally  
B) DEGRADED - Service is operational but performance is below normal  
C) DEAD - Service process has terminated  
D) UNKNOWN - Service status cannot be determined  

**Answer: B**

---

## Answer Key Summary

1. B - GIL bypass for true parallelism  
2. C - process.start() method  
3. B - multiprocessing.Queue for async messaging  
4. C - Locks prevent race conditions  
5. B - Service discovery and tracking  
6. C - Periodic signals indicating service is alive  
7. B - Fault isolation benefit  
8. B - Consistent format and reliability  
9. C - Blocks until item available  
10. B - Complete requests before stopping  
11. B - Create shared objects for processes  
12. C - Prevent indefinite blocking  
13. B - Single entry point for clients  
14. C - Processes have separate memory  
15. B - DEGRADED state for slow services  

---

**Total Questions: 15**  
**Topics Covered:** Process-based architecture, Python multiprocessing, Inter-process communication, Shared memory, Service registry, Health monitoring, Service orchestration, Message protocols, Gateway pattern

**Difficulty Level:** Beginner to Intermediate  
**Passing Score:** 80% (12/15 correct answers)
