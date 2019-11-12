import warnings

from .loader import TOMLLoader as _TOMLLoader

__all__ = ("TOMLLoader",)


class TOMLLoader(_TOMLLoader):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        warnings.warn(
            "TOMLLoader has been moved to the swift_libs.translations.loader package",
            DeprecationWarning,
        )
