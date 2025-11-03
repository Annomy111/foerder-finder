# Advanced RAG System - Deployment Guide

**Version**: 2.0
**Date**: 2025-10-28
**Status**: Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Index Building](#index-building)
4. [API Integration](#api-integration)
5. [Testing & Validation](#testing--validation)
6. [Monitoring](#monitoring)
7. [Rollback Procedure](#rollback-procedure)
8. [Performance Tuning](#performance-tuning)

---

## Prerequisites

### System Requirements

**Minimum** (Development):
- CPU: 4 cores
- RAM: 8 GB
- Disk: 10 GB free
- Python: 3.11+

**Recommended** (Production):
- CPU: 8 cores (or VM.Standard.A1.Flex on OCI)
- RAM: 16 GB
- Disk: 50 GB free (for models + indices)
- GPU: Optional (speeds up embeddings by 3-5x)

### Environment Variables

Add to `/backend/.env`:

```bash
# Advanced RAG Configuration
USE_ADVANCED_RAG=true
RAG_VERBOSE=false  # Set true for debugging

# BGE-M3 Model (default if FlagEmbedding installed)
EMBEDDING_MODEL_NAME=BAAI/bge-m3
EMBEDDING_DEVICE=cpu  # or 'cuda' if GPU available

# Reranker Model
RERANKER_MODEL=BAAI/bge-reranker-base
RERANKER_DEVICE=cpu

# Query Expansion
ENABLE_QUERY_EXPANSION=true
NUM_QUERY_VARIANTS=3

# Feature Toggles
ENABLE_RERANKING=true
ENABLE_COMPRESSION=true
ENABLE_CRAG=true

# ChromaDB (same as before)
CHROMA_DB_PATH=/opt/chroma_db
CHROMA_COLLECTION_NAME=funding_docs

# DeepSeek (increased tokens for better drafts)
DEEPSEEK_MAX_TOKENS=3000
DEEPSEEK_TEMPERATURE=0.5
```

---

## Installation

### Step 1: Install Dependencies

```bash
cd /path/to/Papa\ Projekt/backend

# Update pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# This will install:
# - FlagEmbedding (BGE-M3 + reranker)
# - rank-bm25 (BM25 sparse search)
# - All existing dependencies
```

**Expected install time**: 5-10 minutes
**Disk usage**: ~3 GB (models will download on first use)

### Step 2: Download Models (First Run)

Models download automatically on first use. To pre-download:

```bash
# Test embedder (downloads BGE-M3 ~2GB)
python3 rag_indexer/advanced_embedder.py

# Test reranker (downloads bge-reranker-base ~500MB)
python3 rag_indexer/reranker.py

# Test query expansion (uses DeepSeek API, no download)
python3 rag_indexer/query_expansion.py
```

**Models stored in**: `~/.cache/huggingface/`

### Step 3: Verify Installation

```bash
# Test advanced RAG pipeline
python3 rag_indexer/advanced_rag_pipeline.py

# Expected output:
# [INFO] Initializing Advanced RAG Pipeline
# [SUCCESS] Advanced RAG Pipeline initialized
# [TEST] Testing Advanced RAG Pipeline
# ...
```

If you see errors about missing models:
- Check internet connection (models download from HuggingFace)
- Check disk space (~3 GB needed)
- Check firewall allows HuggingFace access

---

## Index Building

### Step 1: Backup Existing Index (Optional)

```bash
# Backup current ChromaDB
cd /opt  # or your CHROMA_DB_PATH
tar -czf chroma_db_backup_$(date +%Y%m%d).tar.gz chroma_db/

# Verify backup
ls -lh chroma_db_backup_*.tar.gz
```

### Step 2: Build Advanced RAG Indices

```bash
cd /path/to/Papa\ Projekt/backend

# Full rebuild (recommended)
python3 rag_indexer/build_index_advanced.py --rebuild

# Expected output:
# [INFO] ChromaDB Path: /opt/chroma_db
# [INFO] Collection: funding_docs
# [INFO] Loading embedding model...
# [INFO] Loading BGE-M3 model: BAAI/bge-m3
# [SUCCESS] BGE-M3 model loaded
# [INFO] Fetching funding documents from Oracle DB...
# [INFO] Fetched 150 funding documents
# [INFO] Total chunks: 2500
# [INFO] Indexing batch 1/5
# [INFO] Generating embeddings with BGE-M3...
# [SUCCESS] Indexed 500 chunks in ChromaDB
# ...
# [INFO] Building BM25 index for 2500 chunks...
# [SUCCESS] BM25 index built and saved
# [SUCCESS] Advanced RAG Index rebuild complete!
# [STATS] Total documents: 150
# [STATS] Total chunks: 2500
# [STATS] Duration: 450.23 seconds
```

**Expected duration**:
- CPU only: 10-20 minutes for 150 documents
- With GPU: 3-5 minutes

### Step 3: Verify Indices

```bash
# Test hybrid search
python3 rag_indexer/hybrid_searcher.py

# Expected output:
# [SUCCESS] ChromaDB collection count: 2500
# [SUCCESS] BM25 index loaded (2500 documents)
# [TEST] Query: "Tablets für Grundschule"
# --- Hybrid Search (RRF, Top 5) ---
# 1. RRF Score: 0.8523 | Förderung für digitale Endgeräte...
# ...
```

---

## API Integration

### Option A: Side-by-Side Deployment (Recommended)

Run both old and new API routers simultaneously for A/B testing.

**Step 1**: Update `backend/api/main.py`:

```python
from api.routers import drafts, drafts_advanced

# V1 (baseline)
app.include_router(drafts.router, prefix='/api/v1/drafts', tags=['drafts-v1'])

# V2 (advanced RAG)
app.include_router(drafts_advanced.router, prefix='/api/v2/drafts', tags=['drafts-v2'])
```

**Step 2**: Restart API:

```bash
# If using systemd
sudo systemctl restart foerder-api

# Or manually
pkill -f uvicorn
cd /path/to/backend
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Step 3**: Test both endpoints:

```bash
# V1 (old RAG)
curl -X POST http://localhost:8000/api/v1/drafts/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"funding_id": "ABC123", "application_id": "XYZ", "user_query": "Tablets für Klasse 3"}'

# V2 (advanced RAG)
curl -X POST http://localhost:8000/api/v2/drafts/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"funding_id": "ABC123", "application_id": "XYZ", "user_query": "Tablets für Klasse 3"}'
```

### Option B: Direct Replacement

Replace old router with new one (use only after testing).

```python
# In api/main.py
from api.routers import drafts_advanced as drafts

app.include_router(drafts.router, prefix='/api/v1/drafts', tags=['drafts'])
```

---

## Testing & Validation

### Test Suite

```bash
# Create test script
cat > test_advanced_rag.sh <<'EOF'
#!/bin/bash

echo "Testing Advanced RAG System"
echo "============================"
echo ""

# Test 1: Embedder
echo "[TEST 1] Advanced Embedder"
python3 rag_indexer/advanced_embedder.py
echo ""

# Test 2: Hybrid Search
echo "[TEST 2] Hybrid Searcher"
python3 rag_indexer/hybrid_searcher.py
echo ""

# Test 3: Reranker
echo "[TEST 3] Reranker"
python3 rag_indexer/reranker.py
echo ""

# Test 4: Query Expansion
echo "[TEST 4] Query Expansion"
python3 rag_indexer/query_expansion.py
echo ""

# Test 5: Full Pipeline
echo "[TEST 5] Advanced RAG Pipeline"
python3 rag_indexer/advanced_rag_pipeline.py
echo ""

echo "All tests completed!"
EOF

chmod +x test_advanced_rag.sh
./test_advanced_rag.sh
```

### Manual Query Testing

```bash
# Interactive testing
python3 -c "
import asyncio
from rag_indexer.advanced_rag_pipeline import AdvancedRAGPipeline

async def test():
    pipeline = AdvancedRAGPipeline(verbose=True)

    # Test queries
    queries = [
        'Tablets für Grundschule in Berlin',
        'MINT-Förderung Brandenburg',
        'Digitalisierung Bildung bis 10000 Euro'
    ]

    for query in queries:
        print(f'\n\nTesting: {query}')
        print('='*80)
        results = await pipeline.retrieve(query, top_k=5)
        for i, r in enumerate(results):
            print(f'{i+1}. Score: {r.get(\"rerank_score\", \"N/A\")} | {r[\"text\"][:100]}...')

asyncio.run(test())
"
```

---

## Monitoring

### Key Metrics to Track

Create a monitoring dashboard with:

1. **Retrieval Metrics**:
   - Average RRF score
   - Reranker score distribution
   - Query expansion success rate
   - CRAG quality ratings

2. **Performance Metrics**:
   - End-to-end latency (p50, p95, p99)
   - Embedding generation time
   - Reranking time
   - DeepSeek API latency

3. **System Metrics**:
   - ChromaDB collection size
   - BM25 index size
   - Memory usage
   - CPU usage

### Logging

Add to API:

```python
import structlog

logger = structlog.get_logger()

# In drafts_advanced.py
logger.info(
    "draft_generated",
    funding_id=funding_id,
    query_length=len(request.user_query),
    num_chunks=len(rag_result['retrieved_chunks']),
    avg_score=rag_result['retrieval_metadata']['avg_score'],
    generation_time=duration
)
```

---

## Rollback Procedure

If issues occur, rollback to baseline:

### Step 1: Switch API Endpoint

```python
# In api/main.py, change:
from api.routers import drafts_advanced as drafts
# To:
from api.routers import drafts
```

### Step 2: Restore Old Index (if needed)

```bash
cd /opt
rm -rf chroma_db
tar -xzf chroma_db_backup_YYYYMMDD.tar.gz
```

### Step 3: Restart API

```bash
sudo systemctl restart foerder-api
```

### Step 4: Verify

```bash
curl http://localhost:8000/api/v1/health
```

---

## Performance Tuning

### GPU Acceleration (Optional)

If GPU available:

```bash
# Install CUDA-enabled PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Update .env
EMBEDDING_DEVICE=cuda
RERANKER_DEVICE=cuda
```

**Expected speedup**: 3-5x faster embeddings + reranking

### Batch Size Optimization

```python
# In advanced_embedder.py
embeddings = self.embedder.embed_documents(
    texts,
    batch_size=64,  # Increase if more RAM available (default: 32)
    ...
)
```

### Caching

Add Redis cache for frequent queries:

```python
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def retrieve_with_cache(query, funding_id):
    cache_key = f"rag:{funding_id}:{hash(query)}"
    cached = cache.get(cache_key)

    if cached:
        return json.loads(cached)

    results = await pipeline.retrieve(query, funding_id)
    cache.setex(cache_key, 3600, json.dumps(results))  # 1 hour TTL
    return results
```

---

## Troubleshooting

### Issue: "FlagEmbedding not installed"

**Solution**:
```bash
pip install -U FlagEmbedding
```

### Issue: "CUDA out of memory"

**Solutions**:
1. Reduce batch size:
   ```python
   batch_size=16  # instead of 32
   ```
2. Use CPU instead:
   ```bash
   EMBEDDING_DEVICE=cpu
   ```
3. Use FP16 (half precision):
   ```python
   use_fp16=True
   ```

### Issue: "BM25 index not found"

**Solution**:
```bash
# Rebuild BM25 index
python3 rag_indexer/build_index_advanced.py --rebuild
```

### Issue: "DeepSeek API timeout"

**Solution**:
1. Increase timeout:
   ```python
   async with httpx.AsyncClient(timeout=120.0) as client:
   ```
2. Check DeepSeek API status
3. Check network connectivity

---

## Success Criteria

System is production-ready when:

- ✅ All models load successfully
- ✅ ChromaDB + BM25 indices built
- ✅ Test queries return results
- ✅ API endpoints respond in <5s
- ✅ Generated drafts are coherent and relevant
- ✅ Monitoring dashboard shows healthy metrics

---

## Next Steps

After successful deployment:

1. **A/B Testing**: Route 20% traffic to v2, compare metrics
2. **User Feedback**: Collect "helpful/not helpful" votes
3. **Iterate**: Tune hyperparameters based on feedback
4. **Scale**: Increase batch sizes, add GPU, cache frequent queries

---

**Questions or Issues?**

Check logs:
- API: `/var/log/foerder-api.log`
- Indexer: Output of `build_index_advanced.py`
- ChromaDB: `/opt/chroma_db/chroma.log`

For support: See `CLAUDE.md` or Advanced RAG Architecture doc.
