"""Read-only prompt embedding cache used by Wan deployment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import torch
from torch import Tensor


class TextEmbeddingCache:
    """Load precomputed UMT5 embeddings keyed by the exact prompt text."""

    def __init__(self, cache_dir: str | Path):
        self.root = Path(cache_dir).expanduser().resolve()
        manifest_path = self.root / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"Text embedding cache manifest not found: {manifest_path}")
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if self.manifest.get("cache_version") != 1:
            raise ValueError(
                f"Unsupported text embedding cache version: {self.manifest.get('cache_version')!r}"
            )
        self.hash_identity = self.manifest.get("hash_identity")
        if not isinstance(self.hash_identity, dict):
            raise ValueError(f"Missing hash_identity in {manifest_path}")
        self._prompt_paths: dict[str, str] = {}
        for index_path in sorted(self.root.glob("index.shard*-of-*.jsonl")):
            with index_path.open(encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    try:
                        row = json.loads(line)
                        prompt, relative_path = row["prompt"], row["path"]
                    except (json.JSONDecodeError, KeyError, TypeError) as exc:
                        raise ValueError(f"Invalid cache index row {index_path}:{line_number}") from exc
                    if not isinstance(prompt, str) or not isinstance(relative_path, str):
                        raise ValueError(f"Invalid cache index row {index_path}:{line_number}")
                    self._prompt_paths[prompt] = relative_path

    @staticmethod
    def key_for_prompt(prompt: str) -> str:
        if not isinstance(prompt, str):
            raise TypeError(f"prompt must be str, got {type(prompt).__name__}")
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def path_for_prompt(self, prompt: str) -> Path:
        relative_path = self._prompt_paths.get(prompt)
        if relative_path is not None:
            path = (self.root / relative_path).resolve()
            if self.root not in path.parents:
                raise ValueError(f"Cache index path escapes cache root: {relative_path!r}")
            return path
        return self.root / "embeddings" / f"{self.key_for_prompt(prompt)}.pt"

    def load_batch(
        self, prompts: list[str], *, device: torch.device | str, dtype: torch.dtype
    ) -> tuple[Tensor, Tensor]:
        if not prompts:
            raise ValueError("prompts must not be empty")

        contexts: list[Tensor] = []
        seq_lens: list[int] = []
        width: int | None = None
        for prompt in prompts:
            path = self.path_for_prompt(prompt)
            if not path.is_file():
                raise FileNotFoundError(
                    f"No cached text embedding for prompt hash {path.stem}: {prompt!r}"
                )
            record = torch.load(path, map_location="cpu", weights_only=True)
            if not isinstance(record, dict):
                raise ValueError(f"Invalid text embedding record in {path}: expected a dict")
            stored_prompt = record.get("prompt")
            if stored_prompt is not None and stored_prompt != prompt:
                raise ValueError(f"Prompt mismatch in cached text embedding: {path}")
            context = record.get("context")
            seq_len = record.get("seq_len")
            if not isinstance(context, Tensor) or context.ndim != 2:
                raise ValueError(f"Invalid context tensor in {path}: expected [seq, hidden]")
            if not isinstance(seq_len, int) or not 0 < seq_len <= context.shape[0]:
                raise ValueError(f"Invalid seq_len in {path}: {seq_len!r}")
            if width is None:
                width = int(context.shape[1])
            elif context.shape[1] != width:
                raise ValueError(f"Inconsistent embedding width in {path}: {context.shape[1]} != {width}")
            contexts.append(context[:seq_len])
            seq_lens.append(seq_len)

        max_len = max(seq_lens)
        batch = torch.zeros((len(contexts), max_len, width), dtype=dtype, device=device)
        for index, context in enumerate(contexts):
            batch[index, : seq_lens[index]].copy_(context.to(device=device, dtype=dtype))
        return batch, torch.tensor(seq_lens, dtype=torch.long, device=device)
