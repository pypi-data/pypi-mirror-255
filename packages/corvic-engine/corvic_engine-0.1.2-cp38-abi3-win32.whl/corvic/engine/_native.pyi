import numpy as np
import numpy.typing as npt

def train_node2vec_batch(  # noqa: PLR0913
    *,
    sentences: npt.NDArray[np.uint32],
    words: npt.NDArray[np.uint32],
    window: np.int32,
    reduced_windows: npt.NDArray[np.int32],
    num_negative: np.uint32,
    cumulative: npt.NDArray[np.uint32],
    embeddings: npt.NDArray[np.float32],
    hidden_layer: npt.NDArray[np.float32],
    alpha: np.float32,
    work: npt.NDArray[np.float32],
    next_random: np.uint64,
    lock_factors: npt.NDArray[np.float32],
) -> None: ...
