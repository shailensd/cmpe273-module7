from dataclasses import dataclass, field

@dataclass
class OrderEvent:
    order_id: str
    version: int
    status: str
    
@dataclass
class OrderState:
    order_id: str
    current_status: str = "NOT STARTED"
    next_expected_version: int = 1
    pending_events: dict[int, OrderEvent] = field(default_factory=dict)
    history: list[OrderEvent] = field(default_factory=list)
    
    def receive_event(self, event: OrderEvent):
        if event.order_id != self.order_id:
            print(f"received event for order {event.order_id}, but this state is for order {self.order_id}. Ignoring.")
            return
        
        if event.version < self.next_expected_version:
            print(f"received event version {event.version} for order {self.order_id}, but next expected version is {self.next_expected_version}. Ignoring.")
            return
        
        if event.version > self.next_expected_version:
            if event.version in self.pending_events:
                print(f"received duplicate event version {event.version} for order {self.order_id}. Ignoring.")
            else:
                print(f"received future event version {event.version} for order {self.order_id}. Storing in pending events.")
                self.pending_events[event.version] = event
            return

        self.apply_event(event)
        self.apply_pending_events()
        
    def apply_event(self, event: OrderEvent):
        self.current_status = event.status
        self.history.append(event)
        self.next_expected_version += 1
        print(f"applied event version {event.version} and order {event.order_id} is now {event.status}.")
            
    def apply_pending_events(self):
        while self.next_expected_version in self.pending_events:
            event = self.pending_events.pop(self.next_expected_version)
            self.apply_event(event)

    def print_state(self):
        print(f"\nCurrent order state:")
        print(f"Order ID: {self.order_id}")
        print(f"Status: {self.current_status}")
        print(f"Next Expected Version: {self.next_expected_version}")
        print(f"Pending Events: {sorted(self.pending_events.keys())}")
        print(f"Applied versions: {[event.version for event in self.history]}")
            
        
def main():
    order = OrderState(order_id="order-1")
    version2 = OrderEvent(order_id="order-1", version=2, status="PAID")
    version1 = OrderEvent(order_id="order-1", version=1, status="CREATED")
    
    print("Receiving version 2:")
    order.receive_event(version2)
    
    print("Receiving version 1:")
    order.receive_event(version1)
    
    print("Receiving version 2 again:")
    order.receive_event(version2)
    
    
    order.print_state()
    
def missing_event_test():
    print("\n--- Missing Event Test ---")
    order = OrderState(order_id="order-2")
    version2= OrderEvent(order_id="order-2", version=2, status="PAID")
    
    print("Receiving only version 2:")
    order.receive_event(version2)
    
    order.print_state()
    
    
if __name__ == "__main__":
    main()
    missing_event_test()
    