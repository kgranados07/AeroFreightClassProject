# Final Project: AeroFreight Back-end

## Kevin Granados, Charles Levy, Zachary Smith


# Description

We were tasked to create an autonomous logistics simulator for the back-end for AeroFreight. This backend implements a system for tracking delivery routes, two different types of trucks and different loading belts, while also simulating the environment with random events that could impact delivery. The simulation is split into 3 phases, those being Intake, Loading, and Delivery. Intake involves the arrival and processing of packages on conveyor belts. Loading has the simulation load the containers inside. Delivery navigates through a delivery route to deliver the packages

# Classes

## Intake Queue

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

## Cargo Stack

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

## Delivery Route

The delivery route class defines the route taken to deliver the packages. This class would need to travel back and forth between nodes, so a doubly linked list structure would work great.

### `RouteNode()`

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