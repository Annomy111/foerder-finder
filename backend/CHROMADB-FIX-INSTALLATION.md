# ChromaDB SQLite Fix - Installation Guide

## Problem

ChromaDB requires SQLite 3.35+ but many Linux systems (including Oracle Cloud VMs) have older SQLite versions that cannot be easily upgraded due to system dependencies.

**Error you might see:**
```
RuntimeError: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
```

## Solution: pysqlite3-binary Workaround

We use the `pysqlite3-binary` package which provides a newer SQLite version as a Python module. The code automatically substitutes it before ChromaDB imports `sqlite3`.

## Installation Steps (Production Server)

### 1. SSH to Production VM

```bash
ssh -i ~/.ssh/be-api-direct opc@130.61.76.199
```

### 2. Check Current SQLite Version

```bash
sqlite3 --version
# If < 3.35.0, you need the workaround
```

### 3. Install pysqlite3-binary

```bash
cd /opt/foerder-finder-backend  # or your backend directory

# Activate virtual environment if you use one
source venv/bin/activate  # if applicable

# Install pysqlite3-binary
pip install pysqlite3-binary
```

**Expected output:**
```
Collecting pysqlite3-binary
  Downloading pysqlite3_binary-0.5.2.post1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.8 MB)
Installing collected packages: pysqlite3-binary
Successfully installed pysqlite3-binary-0.5.2.post1
```

### 4. Verify Installation

Test that the workaround works:

```bash
python3 -c "
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print('[SUCCESS] pysqlite3 module substitution successful')
except ImportError:
    print('[ERROR] pysqlite3-binary not installed')
    exit(1)

import chromadb
print('[SUCCESS] ChromaDB imported successfully')
print(f'ChromaDB version: {chromadb.__version__}')

# Test PersistentClient
client = chromadb.PersistentClient(path='/tmp/test_chroma')
print('[SUCCESS] ChromaDB PersistentClient created')
"
```

**Expected output:**
```
[SUCCESS] pysqlite3 module substitution successful
[SUCCESS] ChromaDB imported successfully
ChromaDB version: 1.0.15
[SUCCESS] ChromaDB PersistentClient created
```

### 5. Update Environment Variables

Enable advanced RAG in your `.env` file:

```bash
nano .env
```

Add or update:
```bash
USE_ADVANCED_RAG=true
```

### 6. Test RAG Components

Test the hybrid searcher:

```bash
cd /opt/foerder-finder-backend
python3 -m rag_indexer.hybrid_searcher
```

Test the search API:

```bash
python3 -c "from api.routers.search import router; print('[SUCCESS] Search router imported')"
```

### 7. Restart API Service

```bash
sudo systemctl restart foerder-api
sudo systemctl status foerder-api
```

### 8. Verify API Health

```bash
curl http://localhost:8000/api/v1/health
```

Or with authentication:

```bash
# Get JWT token first, then:
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/search/health
```

**Expected response:**
```json
{
  "status": "ok",
  "chromadb_collection_count": 1234,
  "embedder_model": "BAAI/bge-m3",
  "reranker_model": "BAAI/bge-reranker-base",
  "query_expander_enabled": true,
  "compression_enabled": true,
  "crag_enabled": true
}
```

## Code Changes Summary

The following files now include the pysqlite3 workaround at the top:

1. `/backend/api/routers/search.py`
2. `/backend/api/routers/drafts.py`
3. `/backend/rag_indexer/hybrid_searcher.py`
4. `/backend/rag_indexer/build_index.py`
5. `/backend/rag_indexer/build_index_advanced.py`

**Workaround code (already added):**
```python
# CRITICAL: pysqlite3-binary workaround MUST be at the very top
# ChromaDB requires SQLite 3.35+, but system SQLite may be older
# This substitutes pysqlite3 module before ChromaDB imports sqlite3
try:
    __import__('pysqlite3')
    import sys as _sys
    _sys.modules['sqlite3'] = _sys.modules.pop('pysqlite3')
except ImportError:
    # pysqlite3-binary not installed, will use system SQLite (may fail)
    pass
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pysqlite3'"

**Solution:** Install the package:
```bash
pip install pysqlite3-binary
```

### Issue: ChromaDB still fails with SQLite version error

**Possible causes:**
1. pysqlite3-binary not installed in the correct Python environment
2. The workaround code is not at the top of the file (must be before ALL other imports)
3. ChromaDB is imported indirectly by another module that doesn't have the workaround

**Solution:**
1. Check which Python is running: `which python3`
2. Verify installation: `python3 -m pip list | grep pysqlite3`
3. Ensure virtual environment is activated if you use one

### Issue: "ImportError: cannot import name 'X' from chromadb"

**Solution:** ChromaDB version mismatch. Reinstall:
```bash
pip install --upgrade chromadb
```

### Issue: Permission denied when creating ChromaDB directory

**Solution:** Ensure the API user has write permissions:
```bash
sudo chown -R opc:opc /opt/chroma_db
sudo chmod 755 /opt/chroma_db
```

## Performance Impact

The pysqlite3-binary workaround has **negligible performance impact**:
- ✅ Same SQLite functionality
- ✅ No query speed difference
- ✅ No memory overhead
- ✅ Binary wheels are optimized

This is the **recommended solution** for production environments where you cannot upgrade system SQLite.

## Alternative: LanceDB Migration (Future)

If this workaround becomes problematic, consider migrating to **LanceDB** (see `CHROMADB-ALTERNATIVES-RESEARCH-REPORT.md`):
- No SQLite dependency
- Better performance (100x faster)
- Drop-in replacement for ChromaDB
- Migration time: 3-5 hours

## Support

For issues, check:
1. This installation guide
2. `CHROMADB-ALTERNATIVES-RESEARCH-REPORT.md` (alternative solutions)
3. ChromaDB docs: https://docs.trychroma.com/
4. pysqlite3-binary PyPI: https://pypi.org/project/pysqlite3-binary/

---

**Created:** 2025-11-03
**Status:** Tested and production-ready
**Author:** Claude Code
