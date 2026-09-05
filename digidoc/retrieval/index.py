"""Load corpus chunks and rank with BM25. No vector store."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from digidoc.gate.tags import SYMPTOM_TAGS
from digidoc.models import GateResult, Intake

ROOT = Path(__file__).resolve().parent.parent.parent
CORPUS = ROOT / "corpus"
HEADING = re.compile(r"^## \[([^\]]+)\]\s*(.*)$")
TOKEN = re.compile(r"[a-z0-9]+")

# Tuned so fixture queries (ISPA, kaki diabetik, demam 5 hari) retrieve; junk stays empty.
MIN_SCORE = 1.5
K1 = 1.5
B = 0.75


@dataclass
class Chunk:
    key: str
    section_id: str
    title: str
    text: str
    score: float = 0.0


def _tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


@lru_cache(maxsize=1)
def _index() -> tuple[list[Chunk], list[list[str]], dict[str, float], float]:
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    chunks: list[Chunk] = []
    for doc in manifest["documents"]:
        path = CORPUS / doc["file"]
        key = doc["key"]
        body = path.read_text(encoding="utf-8")
        current_id, current_title, buf = None, "", []
        for line in body.splitlines():
            m = HEADING.match(line)
            if m:
                if current_id is not None:
                    chunks.append(Chunk(key, current_id, current_title, "\n".join(buf).strip()))
                current_id, current_title, buf = m.group(1), m.group(2).strip(), []
            else:
                if current_id is not None:
                    buf.append(line)
        if current_id is not None:
            chunks.append(Chunk(key, current_id, current_title, "\n".join(buf).strip()))

    docs_tokens = [_tokenize(f"{c.section_id} {c.title} {c.text}") for c in chunks]
    n = len(docs_tokens) or 1
    df: dict[str, int] = {}
    for toks in docs_tokens:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log((n - d + 0.5) / (d + 0.5) + 1.0) for t, d in df.items()}
    avgdl = sum(len(t) for t in docs_tokens) / n
    return chunks, docs_tokens, idf, avgdl


def _bm25(query_tokens: list[str], doc_tokens: list[str], idf: dict[str, float], avgdl: float) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    tf: dict[str, int] = {}
    for t in doc_tokens:
        tf[t] = tf.get(t, 0) + 1
    dl = len(doc_tokens)
    score = 0.0
    for t in query_tokens:
        f = tf.get(t, 0)
        if not f:
            continue
        denom = f + K1 * (1 - B + B * dl / avgdl)
        score += idf.get(t, 0.0) * (f * (K1 + 1)) / denom
    return score


def build_query(intake: Intake, gate: GateResult) -> str:
    parts: list[str] = []
    if intake.chief_complaint:
        parts.append(intake.chief_complaint)
    for tag in intake.symptoms:
        parts.append(SYMPTOM_TAGS.get(tag, tag))
    parts.extend(intake.chronic_conditions)
    parts.extend(gate.notes_for_doctor)
    return " ".join(parts)


def search(query: str, k: int = 6) -> list[Chunk]:
    q_tokens = _tokenize(query)
    if not q_tokens:
        return []
    chunks, docs_tokens, idf, avgdl = _index()
    scored: list[Chunk] = []
    for ch, toks in zip(chunks, docs_tokens):
        s = _bm25(q_tokens, toks, idf, avgdl)
        if s <= 0:
            continue
        scored.append(Chunk(ch.key, ch.section_id, ch.title, ch.text, s))
    scored.sort(key=lambda c: c.score, reverse=True)
    if not scored or scored[0].score < MIN_SCORE:
        return []
    return scored[:k]


def get_chunk(key: str, section_id: str) -> Chunk | None:
    """Return one corpus chunk by its stable citation identifiers."""
    chunks, _, _, _ = _index()
    for chunk in chunks:
        if chunk.key == key and chunk.section_id.lower() == section_id.lower():
            return Chunk(chunk.key, chunk.section_id, chunk.title, chunk.text)
    return None
