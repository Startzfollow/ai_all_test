# RAG Layered Refactor Teaching Note

## Goal

The RAG module should not be a single file that mixes document loading, chunking, embedding, storage, retrieval and generation. A layered structure makes the system easier to test, replace and explain.

## New structure

```text
backend/app/rag/
├── chunker.py        # document splitting
├── embeddings.py     # local/hash embedding and sentence-transformer adapter
├── vector_store.py   # vector-store protocol
├── local_store.py    # JSON vector store for CI and local demo
├── qdrant_store.py   # Qdrant implementation
├── retriever.py      # query embedding + top-k retrieval
├── reranker.py       # future reranker hook
├── pipeline.py       # end-to-end orchestration
└── types.py          # dataclasses
```

## Why this helps

- Local demos can run without Qdrant or network downloads.
- Qdrant can be enabled through config for production-like experiments.
- Unit tests can validate chunking, embedding, and retrieval separately.
- The README can explain the RAG flow as a real engineering pipeline rather than a list of buzzwords.

## Demo command

```bash
python scripts/eval_rag.py --documents-dir examples/docs --top-k 4
```

This writes a timestamped JSON file under `outputs/` with query, answer preview and source chunks.
