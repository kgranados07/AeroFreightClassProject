# Final Project: AeroFreight Backend

### Creators: Kevin Granados, Charles Levy, Zachary Smith


## Description

We were tasked to create an autonomous logistics simulator for the back-end for AeroFreight. This backend implements a system for tracking delivery routes, two different types of trucks and different loading belts, while also simulating the environment with random events that could impact delivery. The simulation is split into 3 phases, those being Intake, Loading, and Delivery. Intake involves the arrival and processing of packages on conveyor belts. Loading has the simulation load the containers inside. Delivery navigates through a delivery route to deliver the packages

## Classes

### Intake Queue

The intake queue is meant to represent the transport belts that carry packages. Since belts function similarly to lines, a queue structure would fit best as it has a FIFO mentality. The `__init__()` method only contains the initiation of a list named `items`.

```python
class IntakeQueue:
    def __init__(self):
        self.items = []
```

The next two methods are `dequeue()` and `enqueue()`, two key methods for queues. `enqueue()` takes a package and places it at the end of the queue, while `dequeue()` takes the package at the front and removes it from the queue.

```python
    def enqueue(self, package: Package):
        if not isinstance(package, Package):
            raise ValueError("only package objects can be enqueued.")
        self.items.append(package)


    def dequeue(self) -> Package:
        if self.is_empty():
            raise IndexError("Cannot dequeue from empty queue.")
        return self.items.pop(0)
```
The last method is `is_empty()`, which checks whether or not `self.items` is empty.

```python
    def is_empty(self) -> bool:
        return len(self.items) == 0
```

### Cargo Stack

The cargo stack class represents the trucks that would be used for the simulation. The basic structure is a stack, with the packages representing the nodes. The class starts with the `__init__()` method that initiates a list representing the cargo bay, the maximum weight, and current weight.

```python
class CargoStack:
    def __init__(self, max_weight_capacity: float):
        self.cargo_bay = []
        self.max_weight = max_weight_capacity
        self.current_weight = 0.0
```

The next two methods are `pop()` and `push()`, which are two key functions for stack structures. `pop()` removes and returns the most recent package (the package in the front), and `push()` adds one to the front.

```python
    def push(self, package: Package) -> bool:
        """Return True if loaded, False if adding this package exceeds max_weight."""
        if self.current_weight + package.weight > self.max_weight:
            return False  # Cannot load this package, would exceed weight limit
        
        self.cargo_bay.append(package)
        self.current_weight += package.weight
        return True

    def pop(self) -> Package:
        if self.is_empty():
            raise IndexError("Cannot pop from empty stack.")
        package = self.cargo_bay.pop()
        self.current_weight -= package.weight
        return package
```

The final method in this class is `is_empty()`, which returns a boolean value depending if the length of the cargo bay is 0.

```python
    def is_empty(self) -> bool:
        return len(self.cargo_bay) == 0
```

### Delivery Route

The delivery route class defines the route taken to deliver the packages. This class would need to travel back and forth between nodes, so a doubly linked list structure would work great.

#### `RouteNode()`

Delivery routes uses its own specialized nodes to track individual stops. Each node is initialized with a payload linking to a package, a pointer tracking the next node, and one pointing to the previous.

```python
class RouteNode:
    def __init__(self, package: Package):
        self.payload = package
        self.next = None
        self.prev = None  
```

The first method of the delivery route initializes the head pointer and the tail pointer

```python
class DeliveryRoute:
    def __init__(self):
        self.head = None
        self.tail = None
```

The next method is `add_stop_to_front()`, which adds a new node based on a provided package to the front of the delivery route. It creates a new RouteNode and then adds it into the linked list.

```python
    def add_stop_to_front(self, package: Package):
        new_node = RouteNode(package)
        if not self.head:
            self.head = new_node
        
        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node
```

The third method is `cancel_stop()`, which is meant to be a telemetry event that could trigger. the method uses a tracking ID to search the route, and once it finds a package with a matching ID, it removes it from the list.

```python
    def cancel_stop(self, tracking_id: str) -> bool:
        current = self.head
        while current:
            if current.payload.tracking_id == tracking_id:
                if current.prev:
                    current.prev.next = current.next
                else: self.head = current.next

                if current.next:
                    current.next.prev = current.prev
                else: self.tail = current.prev
                return True
            current = current.next
        return False    
```

Finally, the `pop_head()` method removes the first stop on the route nad returns the package.

```python
    def pop_head(self) -> Package:
        if not self.head:
            return None
        payload = self.head.payload
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        return payload
```
### Logistics Engine

The logistics engine is the main code that defines the simulation. It contains 4 methods, each covers a different process in the system.

The first method is the `__init__()` method, and this initializes an express and standard belt, an active truck, an active route, and a list of returned packages.

```python
class LogisticsEngine:
    def __init__(self):
        self.standard_belt = IntakeQueue()
        self.express_belt = IntakeQueue()
        self.active_truck = CargoStack(max_weight_capacity=100.0)
        self.active_route = DeliveryRoute()
        self.returned_packages = []
```
The next method, `receive_packages()`, takes a list of packages anditerates through them to place them in corresponding express or standard belts.

```python
    def receive_packages(self, packages: list):
        for p in packages:
            if isinstance(p, ExpressPackage):
                self.express_belt.enqueue(p)
            else:
                self.standard_belt.enqueue(p)
```
The following method is `load_truck()`. This method pulls from both standard and express belts and organizes them on the active truck, starting with the express belt first. Meanwhile, the delivery route is being built simultaniously in accordance to the truck.

```python
    def load_truck(self):
        """
        STUDENT TASK: 
        1. Always pull from express_belt first. If empty, pull from standard_belt.
        2. Push to CargoStack until full.
        3. As you push to the stack, simultaneously build the DeliveryRoute Linked List.
        """
        while not self.express_belt.is_empty() or not self.standard_belt.is_empty():
            if not self.express_belt.is_empty():
                next_package = self.express_belt.dequeue()
            elif not self.standard_belt.is_empty():
                next_package = self.standard_belt.dequeue()
            else:
                break  # No more to load

            if self.active_truck.push(next_package):
                self.active_route.add_stop_to_front(next_package)
            else:
                # Can't load package, put it on the appropriate belt
                if isinstance(next_package, ExpressPackage):
                    self.express_belt.enqueue(next_package)
                else:
                    self.standard_belt.enqueue(next_package)
                break  # Truck is full, stop loading
```

Finally, the Delivery method named `dispatch_and_simulate()` is resposible for simulating the delivery process. It will update the routes accordingly and account for specific events.

```python
    def dispatch_and_simulate(self):
        print("\n--- INITIATING DELIVERY ROUTE ---")
        while not self.active_truck.is_empty():
            truck_package = self.active_truck.pop()
            route_package = self.active_route.pop_head()
            if truck_package is None or route_package is None:
                break
            # Random event generation
            chance = random.random()
            # Engine failure
            if chance < 0.1:
                print(f"\n!!! ENGINE FAILURE during delivery of {truck_package.tracking_id} !!!"
                self.returned_packages.append(truck_package)
                # Transfer remaining cargo
                self.transfer_to_rescue_truck()
            # Delivery cancellation
            elif chance < 0.2:
                print(f"\nTelemetry Alert: Customer canceled order.")
                print(f"Canceled delivery: {truck_package.tracking_id}")
                self.returned_packages.append(truck_package)
            # Successful delivery
            else:
                print(f"Delivered: {truck_package.generate_shipping_label()}")
        print("\nRoute complete.")
```

## Challenges

The main challenge throughout the project was with the final class. Unlike the previous classes, this class mainly serves the function of running code more than storing data; it uses the other classes as objects. For example, the `load_truck()` method requires collaberation between two `IntakeQueue` objects, A `CargoStack` object, a `DeliveryRoute` object, and all of the nodes and packages those objects work with. Working around the chaos was difficult.