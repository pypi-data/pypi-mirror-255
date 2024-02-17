"""Engine bindings."""
# pyright: reportUnnecessaryTypeIgnoreComment=false
#
# To allow linting without building, allow the module source to be missing
# (when the native library is not built) and also ignore pyright errors when
# ignore comments are not necessary (when the native library is built).

from corvic.engine._native import (  # pyright: ignore[reportMissingModuleSource]
    train_node2vec_batch,
)

# Manually expose and type native symbols. pyo3 does not generate typing
# information that Python type checkers understand [1] and extension modules
# cannot be marked as typed directly [2]. The sensible resolution is to expose
# extension modules through a typed wrapper.
#
# [1] https://github.com/PyO3/pyo3/issues/2454
# [2] https://github.com/python/typing/issues/1333.


__all__ = [
    "train_node2vec_batch",
]
