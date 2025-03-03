from typing import Any, Generic, TypeVar

from bluesky.protocols import Descriptor, Reading, SyncOrAsync

from sunflare.config import ModelInfo

from ._protocols import ModelProtocol

MI = TypeVar("MI", bound=ModelInfo)


class Model(ModelProtocol, Generic[MI]):
    """A boilerplate base class for quick model development.

    Users may subclass from this model and provide their custom
    :class:`~sunflare.config.ModelInfo` implementation.

    Example usage:

    .. code-block:: python

        from sunflare.model import Model
        from sunflare.config import ModelInfo
        from attrs import define


        @define
        class MyModelInfo(ModelInfo):
            str_param: str
            bool_param: bool
            # any other parameters...


        class MyModel(Model[MyModelInfo]):
            def __init__(self, name: str, model_info: MyModelInfo) -> None:
                super().__init__(name, model_info)
                # any other initialization code...

    Parameters
    ----------
    name : ``str``
        Name of the model. Serves as a unique identifier for the object created from it.
    model_info : ``MI``
        Instance of :class:`~sunflare.config.ModelInfo`. subclass.
    """

    def __init__(self, name: str, model_info: MI) -> None:
        self._name = name
        self._model_info = model_info

    def describe_configuration(
        self, source: str = "model_info"
    ) -> SyncOrAsync[Descriptor]:
        return self._model_info.describe_configuration(source)

    def read_configuration(
        self, timestamp: float = 0
    ) -> SyncOrAsync[dict[str, Reading[Any]]]:
        return self._model_info.read_configuration(timestamp)

    @property
    def name(self) -> str:
        return self._name

    @property
    def model_info(self) -> MI:
        return self._model_info

    @property
    def parent(self) -> None:
        return None
