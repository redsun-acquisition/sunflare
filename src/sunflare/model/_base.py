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
        self, *, source: str = "model_info"
    ) -> SyncOrAsync[Descriptor]:
        """Provide a description of the model configuration.

        Inspects the local ``model_info`` object and
        returns a descriptor dictionary compatible
        with the Bluesky event model.

        Parameters
        ----------
        source : ``str``, optional
            Source of the configuration description. Default is ``model_info``.

        Returns
        -------
        dict[``str``, :class:`~event_model.DataKey`]
            A dictionary with the description of each field of the model configuration.
        """
        return self._model_info.describe_configuration(source)

    def read_configuration(
        self, *, timestamp: float = 0
    ) -> SyncOrAsync[dict[str, Reading[Any]]]:
        """Provide a description of the model configuration.

        Inspects the local ``model_info`` object and
        returns a reading dictionary compatible
        with the Bluesky event model.

        Parameters
        ----------
        timestamp : ``float``, optional
            Timestamp of the reading (i.e. ``time.time()``). Default is ``0``.

        Returns
        -------
        dict[``str``, :class:`~bluesky.protocols.Descriptor`]
            A dictionary with the description of each field of the model configuration.
        """
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
