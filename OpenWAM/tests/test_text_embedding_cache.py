from __future__ import annotations

import hashlib
import json

import pytest
import torch

from openwam.model.video_backbone.wan.text_embedding_cache import TextEmbeddingCache


def _make_cache(tmp_path, records):
    (tmp_path / "embeddings").mkdir()
    (tmp_path / "manifest.json").write_text(
        json.dumps({"cache_version": 1, "hash_identity": {"dtype": "bfloat16"}}),
        encoding="utf-8",
    )
    for prompt, context, seq_len in records:
        key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        torch.save(
            {"prompt": prompt, "context": context, "seq_len": seq_len},
            tmp_path / "embeddings" / f"{key}.pt",
        )
    return TextEmbeddingCache(tmp_path)


def test_load_batch_pads_cropped_embeddings(tmp_path):
    cache = _make_cache(
        tmp_path,
        [
            ("short", torch.ones(2, 4, dtype=torch.bfloat16), 2),
            ("long", torch.full((3, 4), 2, dtype=torch.bfloat16), 3),
        ],
    )

    context, seq_lens = cache.load_batch(["short", "long"], device="cpu", dtype=torch.float32)

    assert context.shape == (2, 3, 4)
    assert context.dtype == torch.float32
    assert seq_lens.tolist() == [2, 3]
    assert torch.count_nonzero(context[0, 2]) == 0


def test_missing_prompt_fails_instead_of_falling_back(tmp_path):
    cache = _make_cache(tmp_path, [])

    with pytest.raises(FileNotFoundError, match="No cached text embedding"):
        cache.load_batch(["not cached"], device="cpu", dtype=torch.bfloat16)


def test_record_prompt_must_match_hash_target(tmp_path):
    cache = _make_cache(tmp_path, [("expected", torch.ones(2, 4), 2)])
    path = cache.path_for_prompt("expected")
    torch.save({"prompt": "different", "context": torch.ones(2, 4), "seq_len": 2}, path)

    with pytest.raises(ValueError, match="Prompt mismatch"):
        cache.load_batch(["expected"], device="cpu", dtype=torch.float32)


def test_archive_index_is_authoritative_for_non_prompt_hash_keys(tmp_path):
    prompt = "indexed prompt"
    (tmp_path / "embeddings").mkdir()
    (tmp_path / "manifest.json").write_text(
        json.dumps({"cache_version": 1, "hash_identity": {"dtype": "bfloat16"}}), encoding="utf-8"
    )
    (tmp_path / "index.shard000-of-001.jsonl").write_text(
        json.dumps({"key": "custom-key", "path": "embeddings/custom-key.pt", "prompt": prompt}) + "\n",
        encoding="utf-8",
    )
    torch.save(
        {"prompt": prompt, "context": torch.ones(2, 4), "seq_len": 2},
        tmp_path / "embeddings/custom-key.pt",
    )

    cache = TextEmbeddingCache(tmp_path)
    context, seq_lens = cache.load_batch([prompt], device="cpu", dtype=torch.float32)

    assert context.shape == (1, 2, 4)
    assert seq_lens.tolist() == [2]
