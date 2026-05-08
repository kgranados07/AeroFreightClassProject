import random

# ==========================================
# 1. ENTITIES (OOP & Direct Attributes)
# ==========================================

class Package:
    """Parent class for all logistics packages."""
    def __init__(self, tracking_id: str, weight: float, destination: str):
        self.tracking_id = tracking_id
        self.weight = weight
        self.destination = destination

    def generate_shipping_label(self) -> str:
        """
        This method acts as a placeholder. 
        Subclasses MUST override this method.
        """
        raise NotImplementedError("Subclasses must override generate_shipping_label()")

class StandardPackage(Package):
    def generate_shipping_label(self) -> str:
        return f"[STANDARD] {self.tracking_id} -> {self.destination} -> {self.weight}kg"

class ExpressPackage(Package):
    def generate_shipping_label(self) -> str:
        return f"*** [EXPRESS] {self.tracking_id} -> {self.destination} ***"

# ==========================================
# 2. CUSTOM DATA STRUCTURES
# ==========================================

class IntakeQueue:
    """
    FIFO Queue for the warehouse conveyor belts.
    STUDENT TASK: Implement enqueue, dequeue, and is_empty using basic Python lists.
    No external libraries allowed.
    """
    def __init__(self):
        self.items = []

    def enqueue(self, package: Package):
        if not isinstance(package, Package):
            raise ValueError("only package objects can be enqueued.")
        self.items.append(package)


    def dequeue(self) -> Package:
        if self.is_empty():
            raise IndexError("Cannot dequeue from empty queue.")
        return self.items.pop(0) # Removes the first item, which is the oldest
        
        


    def is_empty(self) -> bool:
        


        return len(self.items) == 0


class CargoStack:
    """
    LIFO Stack simulating a physical truck bed.
    STUDENT TASK: Implement push, pop, and peek. Must enforce max_weight_capacity!
    """
    def __init__(self, max_weight_capacity: float):
        self.cargo_bay = []
        self.max_weight = max_weight_capacity
        self.current_weight = 0.0

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
        
    def is_empty(self) -> bool:
        return len(self.cargo_bay) == 0


class RouteNode:
    def __init__(self, package: Package):
        self.payload = package
        self.next = None
        self.prev = None  


class DeliveryRoute:
    """
    Custom Doubly Linked List representing the sequential driving route.
    """
    def __init__(self):
        self.head = None
        self.tail = None

    def add_stop_to_front(self, package: Package):
        """
        Crucial Constraint: Because trucks load LIFO, the first package in the route 
        must be the LAST package loaded into the truck.
        """
        new_node = RouteNode(package)
        if not self.head:
            self.head = new_node
        
        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node

    def cancel_stop(self, tracking_id: str) -> bool:
        """
        Telemetry event! Traverse the list, find the tracking ID, and delete the node.
        Return True if successfully removed.
        """
        current = self.head
        while current:
            if current.payload.tracking_id == tracking_id:
                # Found the node to delete
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next

                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev

                return True
            current = current.next
        return False  # Not found
        
    def pop_head(self) -> Package:
        """Removes and returns the payload of the first stop on the route."""
        if not self.head:
            return None
        payload = self.head.payload
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        else:            
            self.tail = None
        return payload
    
# ==========================================
# 3. THE SIMULATION ENGINE
# ==========================================
#logistic engine class that will manage the entire process of receiving packages, loading trucks, and simulating deliveries.
#  Write a loading sequence that processes the intake queues. The loading robot must always check the
# Express queue first; it only pulls from the Standard queue if the Express queue is empty.
# • Push the sorted packages into the CargoStack until the weight limit is reached, simultaneously building
# the DeliveryRoute linked list.
# • Simulate the delivery phase by looping through the route, popping packages from the stack, and
# confirming they correctly match the current target node in the linked list.
class LogisticsEngine:
    def __init__(self):
        self.standard_belt = IntakeQueue()
        self.express_belt = IntakeQueue()
        self.active_truck = CargoStack(max_weight_capacity=100.0) # Lowered to force multiple trucks
        self.active_route = DeliveryRoute()
        self.returned_packages = [] # Tracks canceled or undeliverable packages


    def receive_packages(self, packages: list):
        """Sort incoming packages onto the correct conveyor belts."""
        for p in packages:
            if isinstance(p, ExpressPackage):
                self.express_belt.enqueue(p)
            else:
                self.standard_belt.enqueue(p)

    def load_truck(self):
        """
        STUDENT TASK: 
        1. Always pull from express_belt first. If empty, pull from standard_belt.
        2. Push to CargoStack until full.
        3. As you push to the stack, simultaneously build the DeliveryRoute Linked List.
        """
        print("\n--- LOADING TRUCK ---")


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

            print(f"Loaded: {next_package.generate_shipping_label()}")



    def dispatch_and_simulate(self):
        """
        STUDENT TASK:
        Simulate the delivery. Loop until the active_truck is empty.
        Pop the package from the stack and verify its tracking_id matches the payload
        of the current RouteNode in the Linked List.
        """
        print("\n--- INITIATING DELIVERY ROUTE ---")
        
        # Simulated Delivery Loop Structure:
        # while not self.active_truck.is_empty():
            # chance = random.random()
            # if chance < 0.1:
            #     trigger_engine_failure()
            # elif chance < 0.2:
            #     trigger_cancellation()
            # else:
            #     deliver_package()
        while not self.active_truck.is_empty():
            chance = random.random()
            if chance < 0.1:
                print("ENGINE FAILURE! Dispatching rescue team.")
                while not self.active_truck.is_empty():
                    self.returned_packages.append(self.active_truck.pop())
                return
            elif chance < 0.2:
                print("DELIVERY CANCELLATION!.")
                while not self.active_truck.is_empty():
                    self.returned_packages.append(self.active_truck.pop())
                return
       
    
            package_from_truck = self.active_truck.pop()
            package_from_route = self.active_route.pop_head()
            if package_from_truck.tracking_id != package_from_route.tracking_id:
                print(f"ERROR: Mismatch in delivery! {package_from_truck.tracking_id} != {package_from_route.tracking_id}")
                self.returned_packages.append(package_from_truck)
            else:
                print(f"Delivered: {package_from_truck.generate_shipping_label()}")


# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Generate mock data
    mock_packages = []
    for i in range(1, 16):
        weight = round(random.uniform(5.0, 20.0), 1)
        dest = f"{random.randint(100,999)} Main St"
        if random.random() > 0.7:
            mock_packages.append(ExpressPackage(f"EXP-{i:03d}", weight, dest))
        else:
            mock_packages.append(StandardPackage(f"STD-{i:03d}", weight, dest))

    # Run the Engine
    engine = LogisticsEngine()
    engine.receive_packages(mock_packages)
    
    # Load and Dispatch first truck
    engine.load_truck()
    engine.dispatch_and_simulate()
    
    # Check if we need to dispatch a second truck for leftovers
    if not engine.standard_belt.is_empty() or not engine.express_belt.is_empty():
        print("\n--- INITIATING SECOND TRUCK DISPATCH ---")
        engine.load_truck()
        engine.dispatch_and_simulate()
        
    print("\n--- END OF DAY REPORT ---")
    print(f"Returned/Cancelled Packages: {len(engine.returned_packages)}")
    for p in engine.returned_packages:
        print(f" - {p.tracking_id} back in inventory.")