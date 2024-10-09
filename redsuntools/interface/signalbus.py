from abc import ABC

class SignalBus(ABC):
    """ SignalBus base class.
    
    The signal bus is a mechanism for communication between objects. It is used to send signals from one object to another. \\
    The bus allows to interconnect different controllers of the Controller layer and provide the means to exchange data between them. \\
    A bus can automatically register a new signal from a controller, exposing it to other controllers.

    Parameters
    ----------
    ABC : _type_
        _description_
    """