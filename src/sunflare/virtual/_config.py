from typing_extensions import Required, TypedDict

__all__ = ["RedSunConfig"]


class RedSunConfig(TypedDict, total=False):
    """Base configuration dictionary for Redsun applications.

    Describes the common top-level keys shared by all Redsun container
    configurations.  This is the canonical definition; the application
    layer (``redsun``) extends it with component-specific sections
    (``devices``, ``presenters``, ``views``) that are not propagated to
    individual components.

    Attributes
    ----------
    schema_version : float
        Version number for the configuration schema.
    session : str
        Display name for the session.
    frontend : str
        Frontend toolkit identifier (e.g. ``"pyqt"``, ``"pyside"``).
    """

    schema_version: Required[float]
    session: Required[str]
    frontend: Required[str]
