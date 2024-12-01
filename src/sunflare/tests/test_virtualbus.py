import numpy as np

from sunflare.virtualbus import Signal, VirtualBus, ModuleVirtualBus, slot


class MockVirtualBus(VirtualBus):
    sigMySignal = Signal(int, description="My signal")

    def __init__(self):
        super().__init__()
        
def test_virtual_bus() -> None:
    """Tests the creation of a singleton virtual bus."""
    bus = MockVirtualBus()
    
    assert hasattr(bus, "sigMySignal")

def test_virtual_bus_registration() -> None:
    """Tests the registration of signals in the virtual bus."""
    
    class MockOwner:
        sigMySignal = Signal(int, description="My signal")
    
    owner = MockOwner()
    bus = MockVirtualBus()
    
    bus.register_signals(owner)
    
    assert "MockOwner" in bus
    
    def test_slot(x: int) -> None:
        assert x == 5
    
    bus["MockOwner"]["sigMySignal"].connect(lambda x: test_slot(x))
    bus["MockOwner"]["sigMySignal"].emit(5)

def test_module_virtual_bus() -> None:
    """Tests the creation of a singleton module virtual bus."""
    module_bus1 = ModuleVirtualBus()
    module_bus2 = ModuleVirtualBus()

    assert module_bus1 is module_bus2

def test_module_virtual_bus_registration() -> None:
    """Tests the registration of signals in the module virtual bus."""
    
    class MockOwner:
        sigMySignal = Signal(int, description="My signal")
    
    owner = MockOwner()
    bus = ModuleVirtualBus()
    
    bus.register_signals(owner)
    
    assert "MockOwner" in bus
    
    def test_slot(x: int) -> None:
        assert x == 5
    
    bus["MockOwner"]["sigMySignal"].connect(lambda x: test_slot(x))
    bus["MockOwner"]["sigMySignal"].emit(5)

def test_slot_decorator() -> None:
    """Tests the slot decorator."""
    
    @slot
    def test_slot(x: int) -> None:
        assert x == 5
    
    assert hasattr(test_slot, "__isslot__")
