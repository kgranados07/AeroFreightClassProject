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
