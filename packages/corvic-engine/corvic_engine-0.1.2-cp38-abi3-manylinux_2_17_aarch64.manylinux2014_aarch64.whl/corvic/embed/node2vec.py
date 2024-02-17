"""Node2Vec embeddings."""
from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Sequence
from queue import Queue
from typing import Any, Literal, TypeAlias, cast

import numpy as np
import numpy.typing as npt
from numba import njit  # pyright: ignore[reportUnknownVariableType]
from scipy.sparse import csr_matrix
from tqdm.auto import trange

from corvic import engine

_CSR_INDEX: TypeAlias = npt.NDArray[np.int32] | npt.NDArray[np.int64]
_MAX_SENTENCE_LEN = 10000
_MAX_WORDS_IN_BATCH = _MAX_SENTENCE_LEN


class Space:
    """A feature space, i.e., a graph."""

    def __init__(
        self,
        edges: Sequence[tuple[int, int]],
        directed: bool = True,
    ):
        """Create a space from a sequence of edges."""
        nodes: dict[int, int] = defaultdict(lambda: len(nodes))
        from_: list[int] = []
        to: list[int] = []

        for tpl in edges:
            a, b = tpl
            a = nodes[a]
            b = nodes[b]
            from_.append(a)
            to.append(b)
            if not directed:
                from_.append(b)
                to.append(a)

        n = len(nodes)

        edges_matrix = csr_matrix(
            (np.ones(len(from_), dtype=bool), (from_, to)), shape=(n, n)
        )

        edges_matrix.sort_indices()
        self.indptr = edges_matrix.indptr  # pyright: ignore[reportUnknownMemberType]
        self.indices = edges_matrix.indices  # pyright: ignore[reportUnknownMemberType]
        node_names: list[int | None] = [None] * n
        for name, i in nodes.items():
            node_names[i] = name
        self.node_names = np.array(node_names)


@njit(nogil=True)  # pyright: ignore[reportUntypedFunctionDecorator]
def _isin_sorted(a: _CSR_INDEX, x: int) -> bool:
    return a[np.searchsorted(a, x)] == x


@njit(nogil=True)  # pyright: ignore[reportUntypedFunctionDecorator]
def _neighbors(indptr: _CSR_INDEX, indices_or_data: _CSR_INDEX, t: int) -> _CSR_INDEX:
    return indices_or_data[indptr[t] : indptr[t + 1]]


@njit(nogil=True)  # pyright: ignore[reportUntypedFunctionDecorator]
def _random_walk(  # noqa: PLR0913
    *,
    indptr: _CSR_INDEX,
    indices: _CSR_INDEX,
    walk_length: int,
    p: float,
    q: float,
    t: int,
):
    max_prob = max(1 / p, 1, 1 / q)
    prob_0 = 1 / p / max_prob
    prob_1 = 1 / max_prob
    prob_2 = 1 / q / max_prob

    walk = np.empty(walk_length, dtype=indices.dtype)
    walk[0] = t
    neighbors = _neighbors(indptr, indices, t)
    if not neighbors.size:
        return walk[:1]

    walk[1] = np.random.choice(_neighbors(indptr, indices, t))  # noqa: NPY002
    for j in range(2, walk_length):
        neighbors = _neighbors(indptr, indices, walk[j - 1])
        if not neighbors.size:
            return walk[:j]
        if p == q == 1:
            # faster version
            walk[j] = np.random.choice(neighbors)  # noqa: NPY002
            continue
        while True:
            new_node = np.random.choice(neighbors)  # noqa: NPY002
            r = np.random.rand()  # noqa: NPY002
            if new_node == walk[j - 2]:
                if r < prob_0:
                    break
            elif _isin_sorted(_neighbors(indptr, indices, walk[j - 2]), new_node):
                if r < prob_1:
                    break
            elif r < prob_2:
                break
        walk[j] = new_node
    return walk


def _generate_random_walk(
    space: Space, walk_length: int, p: float, q: float, source_node_id: int
) -> list[str]:
    walk = _random_walk(
        indptr=cast(_CSR_INDEX, space.indptr),  # pyright: ignore[reportUnknownMemberType]
        indices=cast(_CSR_INDEX, space.indices),  # pyright: ignore[reportUnknownMemberType]
        walk_length=walk_length,
        p=p,
        q=q,
        t=source_node_id,
    )
    return space.node_names[walk].tolist()


class KeyedVectors:
    """Vectors whose entries are keyed by an arbitrary value.

    Used to represent embeddings.
    """

    vectors: npt.NDArray[np.float32]

    key_to_index: dict[Any, int]
    index_to_key: list[Any]

    count: npt.NDArray[np.int32]
    sample_prob: npt.NDArray[np.uint32]

    def __init__(self, dim: int):  # noqa: D107
        self.dim = dim
        self.key_to_index = {}
        self.index_to_key = []
        self.vectors = np.zeros(1, dtype=np.float32)
        self.count = np.zeros(1, dtype=np.int32)
        self.sample_prob = np.zeros(1, dtype=np.uint32)

    def allocate_vectors(self):  # noqa: D102
        self.count = np.ndarray(len(self), dtype=np.int32)
        self.sample_prob = np.ndarray(len(self), dtype=np.uint32)

    def set_count(self, word: Any, count: int):  # noqa: D102
        self.count[self.key_to_index[word]] = count

    def get_count(self, word: Any) -> int:  # noqa: D102
        return self.count[self.key_to_index[word]]

    def set_sample_prob(self, word: Any, prob: np.uint32):  # noqa: D102
        self.sample_prob[self.key_to_index[word]] = prob

    def initialize_embedding(self):  # noqa: D102
        rng = np.random.default_rng(seed=1)
        vectors = rng.random((len(self), self.dim), dtype=np.float32)
        vectors *= 2.0
        vectors -= 1.0
        vectors /= self.dim
        self.vectors = vectors

    def sort_by_descending_frequency(self):  # noqa: D102
        if not len(self):
            return
        count_sorted_indexes = np.argsort(self.count)[::-1]

        self.index_to_key = [self.index_to_key[idx] for idx in count_sorted_indexes]
        self.key_to_index = {word: i for i, word in enumerate(self.index_to_key)}
        self.sample_prob = self.sample_prob[count_sorted_indexes]
        self.count = self.count[count_sorted_indexes]

    def __len__(self):  # noqa: D105
        return len(self.index_to_key)

    def __getitem__(self, key: Any) -> npt.NDArray[np.float32]:  # noqa: D105
        return self.vectors[self.key_to_index[key]]


def _zeros_aligned(
    shape: int, dtype: npt.DTypeLike, order: Literal["C"] = "C", align=128
):
    nbytes = np.prod(shape, dtype=np.int64) * np.dtype(dtype).itemsize
    buffer = np.zeros(nbytes + align, dtype=np.uint8)
    start_index = -buffer.ctypes.data % align
    return (
        buffer[start_index : start_index + nbytes]
        .view(dtype)
        .reshape(shape, order=order)
    )


class _Word2Vec:
    thread_excs: list[Exception]

    def __init__(  # noqa: PLR0913
        self,
        dim: int = 100,
        alpha: float = 0.025,
        window: int = 5,
        min_count: int = 5,
        sample: float = 1e-3,
        seed: int = 1,
        workers: int = 1,
        min_alpha: float = 0.0001,
        negative: int = 5,
        ns_exponent=0.75,
        batch_words: int = _MAX_WORDS_IN_BATCH,
    ):
        self.workers = workers
        self.batch_words = batch_words

        self.alpha = alpha
        self.min_alpha = min_alpha

        self.window = window
        self.negative = negative
        self.ns_exponent = ns_exponent

        self.min_count = min_count
        self.sample = sample

        self.keyed_vectors = KeyedVectors(dim)

        self.seed = seed
        self.layer1_size = dim

        self.thread_excs = []
        self.thread_excs_lock = threading.Lock()

        self.cumulative = None
        self.syn1neg = None

    def _build_vocab(self, corpus_iterable: Sequence[Sequence[str]]):
        vocab = self._scan_vocab(corpus_iterable)
        self._prepare_vocab(vocab)
        self.keyed_vectors.initialize_embedding()

    def _prepare_vocab(self, vocab: dict[str, int]):
        retain_total = 0
        retain_words: list[str] = []

        for word, v in vocab.items():
            if v >= self.min_count:
                retain_words.append(word)
                retain_total += v
                self.keyed_vectors.key_to_index[word] = len(
                    self.keyed_vectors.index_to_key
                )
                self.keyed_vectors.index_to_key.append(word)

        self.keyed_vectors.allocate_vectors()

        for word in self.keyed_vectors.index_to_key:
            self.keyed_vectors.set_count(word, vocab[word])

        if not self.sample:
            threshold_count = retain_total
        elif self.sample < 1.0:  # noqa: PLR2004
            threshold_count = self.sample * retain_total
        else:
            threshold_count = int(self.sample * (3 + np.sqrt(5)) / 2)

        downsample_total, downsample_unique = 0, 0
        for w in retain_words:
            v = vocab[w]
            word_probability = (np.sqrt(v / threshold_count) + 1) * (
                threshold_count / v
            )
            if word_probability < 1.0:  # noqa: PLR2004
                downsample_unique += 1
                downsample_total += word_probability * v
            else:
                word_probability = 1.0
                downsample_total += v
            self.keyed_vectors.set_sample_prob(
                w, np.uint32(word_probability * (2**32 - 1))
            )

        self.keyed_vectors.sort_by_descending_frequency()
        self.cumulative = self._make_cumulative(self.keyed_vectors, self.ns_exponent)
        self.syn1neg = np.zeros(
            (len(self.keyed_vectors), self.layer1_size), dtype=np.float32
        )

    @classmethod
    def _make_cumulative(
        cls,
        keyed_vectors: KeyedVectors,
        neg_sample_exp: float,
        domain: float = 2**31 - 1,
    ) -> npt.NDArray[np.uint32]:
        vocab_size = len(keyed_vectors)
        cumulative = np.zeros(vocab_size, dtype=np.uint32)
        train_words_pow = 0.0
        for word_index in range(vocab_size):
            count = keyed_vectors.count[word_index]
            train_words_pow += count**neg_sample_exp
        value = 0.0
        for word_index in range(vocab_size):
            count = keyed_vectors.count[word_index]
            value += count**neg_sample_exp
            cumulative[word_index] = round(value / train_words_pow * domain)

        return cumulative

    @classmethod
    def _scan_vocab(cls, sentences: Sequence[Sequence[str]]) -> dict[str, int]:
        vocab: dict[str, int] = defaultdict(int)
        for sentence in sentences:
            for word in sentence:
                vocab[word] += 1

        return vocab

    def _get_thread_working_mem(self):
        work = _zeros_aligned(self.layer1_size, dtype=np.float32)
        return work

    def _add_thread_exc(self, exc: Exception):
        with self.thread_excs_lock:
            self.thread_excs.append(exc)

    def _worker_loop(
        self, job_queue: Queue[tuple[Sequence[Sequence[str]], float] | None]
    ):
        work = self._get_thread_working_mem()
        while True:
            job = job_queue.get()
            if job is None:
                break
            try:
                data_iterable, alpha = job

                self._do_train_job(data_iterable, alpha, work)
            except Exception as exc:
                self._add_thread_exc(exc)

    @classmethod
    def _raw_word_count(cls, batch: Sequence[Sequence[str]]) -> int:
        return sum(len(sentence) for sentence in batch)

    def _job_producer(  # noqa: PLR0913
        self,
        data_iterator: Sequence[Sequence[str]],
        job_queue: Queue[tuple[Sequence[Sequence[str]], float] | None],
        cur_epoch: int,
        total_epochs: int,
        total_examples: int,
    ):
        job_batch = []
        batch_size = 0
        pushed_examples = 0
        next_alpha = self._get_next_alpha(0.0, cur_epoch, total_epochs)
        job_no = 0

        for data in data_iterator:
            data_length = self._raw_word_count([data])

            if batch_size + data_length <= self.batch_words:
                job_batch.append(data)
                batch_size += data_length
            else:
                job_no += 1
                job_queue.put((job_batch, next_alpha))

                pushed_examples += len(job_batch)
                epoch_progress = 1.0 * pushed_examples / total_examples
                next_alpha = self._get_next_alpha(
                    epoch_progress, cur_epoch, total_epochs
                )

                job_batch = [data]
                batch_size = data_length

        if job_batch:
            job_no += 1
            job_queue.put((job_batch, next_alpha))

        for _ in range(self.workers):
            job_queue.put(None)

    def _get_next_alpha(self, epoch_progress: float, cur_epoch: int, total_epochs: int):
        start_alpha = self.alpha
        end_alpha = self.min_alpha

        progress = (cur_epoch + epoch_progress) / total_epochs
        next_alpha = start_alpha - (start_alpha - end_alpha) * progress
        next_alpha = max(end_alpha, next_alpha)

        return next_alpha

    def _train_epoch(  # noqa: PLR0913
        self,
        data_iterable: Sequence[Sequence[str]],
        cur_epoch: int,
        total_examples: int,
        total_epochs: int,
        queue_factor: int = 2,
    ):
        job_queue: Queue[tuple[Sequence[Sequence[str]], float] | None] = Queue(
            maxsize=queue_factor * self.workers
        )

        self.thread_excs = []

        workers = [
            threading.Thread(target=self._worker_loop, args=(job_queue,))
            for _ in range(self.workers)
        ]

        workers.append(
            threading.Thread(
                target=self._job_producer,
                args=(data_iterable, job_queue),
                kwargs={
                    "cur_epoch": cur_epoch,
                    "total_epochs": total_epochs,
                    "total_examples": total_examples,
                },
            )
        )

        for thread in workers:
            thread.daemon = True
            thread.start()

        for thread in workers:
            thread.join()

        for exc in self.thread_excs:
            raise exc from None

    def train(  # noqa: PLR0913
        self,
        corpus_iterable: Sequence[Sequence[str]],
        *,
        epochs: int,
        total_examples: int,
        start_alpha: float | None = None,
        end_alpha: float | None = None,
        queue_factor=2,
    ):
        self.alpha = start_alpha or self.alpha
        self.min_alpha = end_alpha or self.min_alpha

        for cur_epoch in range(epochs):
            self._train_epoch(
                corpus_iterable,
                cur_epoch=cur_epoch,
                total_examples=total_examples,
                queue_factor=queue_factor,
                total_epochs=epochs,
            )

    def _do_train_job(
        self,
        sentence_seq: Sequence[Sequence[str]],
        alpha: float,
        work: npt.NDArray[np.float32],
    ):
        assert self.syn1neg is not None
        assert self.cumulative is not None

        r1 = np.random.randint(  # pyright: ignore[reportUnknownMemberType] # noqa: NPY002
            np.uint64(0), np.uint64(2**24)
        )
        r2 = np.random.randint(np.uint64(0), np.uint64(2**24))  # pyright: ignore[reportUnknownMemberType] # noqa: NPY002
        next_random = np.uint64(2**24) * r1 + r2
        vocab_samples = self.keyed_vectors.sample_prob

        sentences = np.ndarray(_MAX_SENTENCE_LEN + 1, np.uint32)
        words = np.ndarray(_MAX_SENTENCE_LEN, np.uint32)
        reduced_windows = np.ndarray(_MAX_SENTENCE_LEN, np.int32)

        effective_words = 0
        effective_sentences = 0
        sentences[0] = 0
        for sen in sentence_seq:
            if not sen:
                continue
            for token in sen:
                if token not in self.keyed_vectors.key_to_index:
                    continue
                word_index = self.keyed_vectors.key_to_index[token]
                # TODO(ddn): random_int32(next_random)
                sample = cast(int, np.random.randint(0, 2**32 - 1))  # pyright: ignore[reportUnknownMemberType] # noqa: NPY002
                if self.sample and vocab_samples[word_index] < sample:
                    continue
                words[effective_words] = word_index
                effective_words += 1
                if effective_words == _MAX_SENTENCE_LEN:
                    break
            effective_sentences += 1
            sentences[effective_sentences] = effective_words
            if effective_words == _MAX_SENTENCE_LEN:
                break

        for i, item in enumerate(np.random.randint(0, self.window, effective_words)):  # pyright: ignore[reportUnknownMemberType] # noqa: NPY002
            reduced_windows[i] = np.int32(item)

        lock_factors = np.ones(1, dtype=np.float32)

        engine.train_node2vec_batch(
            sentences=sentences[: effective_sentences + 1],  # pyright: ignore[reportUnknownArgumentType]
            words=words,
            window=np.int32(self.window),
            reduced_windows=reduced_windows,
            num_negative=np.uint32(self.negative),
            cumulative=self.cumulative,
            embeddings=self.keyed_vectors.vectors,
            hidden_layer=self.syn1neg,
            alpha=np.float32(alpha),
            next_random=np.uint64(next_random),
            work=work,
            lock_factors=lock_factors,
        )

    @property
    def wv(self):
        return self.keyed_vectors


class Node2Vec(_Word2Vec):
    """Node to vector algorithm."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        space: Space,
        dim: int,
        walk_length: int,
        window: int,
        p: float = 1.0,
        q: float = 1.0,
        workers: int = 1,
        batch_walks: int | None = None,
    ):
        """Create a new instance of Node2Vec.

        Parameters
        ---------------------------
        space: Space
            Graph object whose nodes are to be embedded.
        dim: int
            The dimensionality of the embedding
        walk_length: int
            Length of the random walk to be computed
        window: int
            The dimension of the window.
            This is HALF of the context, as gensim will
            consider as context all nodes before `window`
            and after `window`.
        p: float = 1.0
            The higher the value, the lower the probability to return to
            the previous node during a walk.
        q: float = 1.0
            The higher the value, the lower the probability to return to
            a node connected to a previous node during a walk.
        workers : int, optional (default = 1)
            The number of threads to use during the embedding process.
        batch_walks: Optional[int] = None
            Target size (in words) for batches of examples passed to worker threads
        """
        if walk_length >= _MAX_SENTENCE_LEN:
            raise ValueError(f"walk_length >= {_MAX_SENTENCE_LEN}")
        assert walk_length < _MAX_SENTENCE_LEN
        if batch_walks is None:
            batch_words = _MAX_SENTENCE_LEN
        else:
            batch_words = min(walk_length * batch_walks, _MAX_SENTENCE_LEN)

        super().__init__(
            window=window,
            min_count=1,
            workers=workers,
            batch_words=batch_words,
            dim=dim,
        )
        self._build_vocab([[w] for w in space.node_names])
        self.space = space
        self.walk_length = walk_length
        self.p = p
        self.q = q

    def train(self, epochs: int, *, verbose: bool = True):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Train the model and compute the node embedding.

        Parameters
        --------------------
        epochs: int
            Number of epochs to train the model for.
        verbose: bool = True
            Whether to show loading bar.
        """

        def gen_nodes():
            """Number of epochs to compute."""
            for _ in trange(
                epochs,
                dynamic_ncols=True,
                desc="Epochs",
                leave=False,
                disable=not verbose,
            ):
                for i in np.random.permutation(len(self.space.node_names)):  # noqa: NPY002
                    # dummy walk with same length
                    yield [i] * self.walk_length

        super().train(
            list(gen_nodes()),
            epochs=1,
            total_examples=epochs * len(self.space.node_names),
        )

    def _generate_random_walk(self, source_node_id: int) -> list[str]:
        return _generate_random_walk(
            self.space, self.walk_length, self.p, self.q, source_node_id
        )

    def _do_train_job(
        self,
        sentence_seq: Sequence[Sequence[str]],
        alpha: float,
        work: npt.NDArray[np.float32],
    ):
        walks = [self._generate_random_walk(int(w[0])) for w in sentence_seq]
        super()._do_train_job(walks, alpha, work)
