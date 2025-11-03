# ChromaDB Alternatives for Vector Search - Research Report

**Date:** 2025-11-03
**Project:** Förder-Finder Grundschule
**Context:** SQLite version conflict (requires 3.35+, system incompatible)
**Current Setup:** ChromaDB disabled, need replacement for RAG search
**Scale:** ~50-100 funding documents, small-scale production

---

## Executive Summary

**Top Recommendation:** **LanceDB** (Best overall for your use case)
**Runner-up:** **FAISS** (Simplest, fastest setup)
**Production Alternative:** **Qdrant** (Most feature-complete)

Based on your requirements (Python, no SQLite issues, Oracle Cloud VM, 50-100 docs, sentence-transformers), **LanceDB** offers the best balance of simplicity, performance, and zero-dependency issues. It's a drop-in replacement for ChromaDB with better performance and no SQLite requirements.

---

## Detailed Comparison

### 1. LanceDB ⭐ **RECOMMENDED**

**Overview:**
Open-source, embedded vector database using the Lance columnar format. Rust-based, Python-native, serverless architecture.

#### Installation Complexity: ⭐⭐⭐⭐⭐ (Excellent)
```bash
pip install lancedb
pip install sentence-transformers
```

**No external dependencies**, no SQLite, no server setup required.

#### Performance Characteristics:
- **Query Speed:** 100x faster than Parquet for vector search
- **Search 1B vectors:** <100ms on MacBook (128 dimensions)
- **Disk-based:** Low memory footprint, massive scalability
- **Multimodal:** Text, images, audio support (Lance format)

#### Pros vs ChromaDB:
✅ **No SQLite dependency** - Uses Lance format (Parquet-based)
✅ **Better performance** - Faster scans, efficient storage
✅ **Embedded & serverless** - Same simplicity as ChromaDB
✅ **Zero-copy versioning** - Git-like data versioning
✅ **Multimodal support** - Beyond just text vectors
✅ **Production-ready** - Used at scale by companies
✅ **Excellent Python integration** - pandas, numpy, arrow compatible
✅ **Active development** - Strong community, frequent updates

#### Cons vs ChromaDB:
⚠️ Relatively new (but mature enough for production)
⚠️ Less extensive documentation than Chroma (but improving)

#### Migration Effort from ChromaDB: ⭐⭐⭐⭐ (Easy)
- **Similarity:** 90% - Both embedded, Python-first
- **Code Changes:** Minimal - Adjust client initialization and query syntax
- **Data Migration:** Re-index required (no direct import)
- **Estimated Time:** 2-4 hours

**Migration Code Example:**
```python
import lancedb
from sentence_transformers import SentenceTransformer

# Setup (replaces ChromaDB PersistentClient)
db = lancedb.connect('/opt/lance_db')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Create table (replaces ChromaDB collection)
data = [
    {"text": "Sample document", "metadata": {"funding_id": "123"}},
]
embeddings = model.encode([d['text'] for d in data])
for i, d in enumerate(data):
    d['vector'] = embeddings[i]

table = db.create_table("funding_docs", data=data, mode="overwrite")

# Search (replaces ChromaDB query)
query_vector = model.encode(["tablets for schools"])[0]
results = table.search(query_vector).limit(5).to_pandas()
```

#### Cost: **FREE** ✅
Open-source, no hosted service needed.

#### Oracle Cloud VM Compatibility:
✅ **Perfect fit** - Lightweight, file-based storage
✅ Works on ARM (A1.Flex) and x86
✅ Mount on block volume like ChromaDB

---

### 2. FAISS (Facebook AI Similarity Search)

**Overview:**
C++ library with Python bindings, optimized for billion-scale similarity search. Industry standard for vector search.

#### Installation Complexity: ⭐⭐⭐⭐ (Very Good)
```bash
pip install faiss-cpu
# OR for GPU support
pip install faiss-gpu
```

Single package, no external services.

#### Performance Characteristics:
- **Query Speed:** **8.5x faster** than previous state-of-the-art
- **Optimized for:** Billion-scale datasets
- **Hardware:** Multi-core CPU optimization, optional GPU acceleration
- **Memory:** Requires vectors in RAM (compressed formats available)

#### Pros vs ChromaDB:
✅ **No SQLite dependency** - Pure in-memory or file-based
✅ **Fastest search** - Industry-leading performance
✅ **Battle-tested** - Meta's production library
✅ **Flexible indexing** - IVF, HNSW, PQ, many options
✅ **GPU support** - Optional massive speedup
✅ **Minimal footprint** - Library, not database
✅ **Half-precision (float16)** - Speed boost with minimal accuracy loss

#### Cons vs ChromaDB:
⚠️ **Lower-level API** - More boilerplate code required
⚠️ **No built-in metadata** - Must manage separately (e.g., dict or SQLite)
⚠️ **Manual persistence** - Save/load index yourself
⚠️ **No built-in chunking** - Must implement text splitting separately
⚠️ **Requires more code** - Less "batteries included" than ChromaDB

#### Migration Effort from ChromaDB: ⭐⭐⭐ (Moderate)
- **Similarity:** 50% - Library vs database paradigm
- **Code Changes:** Significant - Rewrite retrieval logic
- **Data Migration:** Re-index + build metadata store
- **Estimated Time:** 4-8 hours

**Migration Code Example:**
```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Assume docs = [{'id': 'X', 'text': 'Y', 'metadata': {}}]
texts = [d['text'] for d in docs]
embeddings = model.encode(texts, normalize_embeddings=True)
embeddings_np = np.array(embeddings).astype('float32')

# Build index
dimension = embeddings_np.shape[1]  # 384 for all-MiniLM-L6-v2
index = faiss.IndexFlatIP(dimension)  # Inner Product (for normalized vectors)
index.add(embeddings_np)

# Store metadata separately
metadata_store = {i: docs[i] for i in range(len(docs))}

# Save
faiss.write_index(index, '/opt/faiss_index.bin')

# Search
query_vector = model.encode(["tablets for schools"], normalize_embeddings=True)
query_np = np.array(query_vector).astype('float32')
distances, indices = index.search(query_np, k=5)

results = [metadata_store[i] for i in indices[0]]
```

#### Cost: **FREE** ✅
Open-source library.

#### Oracle Cloud VM Compatibility:
✅ Works perfectly on CPU (faiss-cpu)
⚠️ GPU requires NVIDIA GPU (not available on A1.Flex)
✅ Lightweight, minimal dependencies

---

### 3. Qdrant

**Overview:**
High-performance, Rust-based vector database with RESTful + gRPC APIs. Designed for production AI applications.

#### Installation Complexity: ⭐⭐⭐ (Good - Docker Required)
```bash
# Docker deployment (recommended)
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Python client
pip install qdrant-client
```

Requires Docker + persistent volume.

#### Performance Characteristics:
- **Query Speed:** Optimized for sub-100ms latency
- **Scale:** Production-grade, handles millions of vectors
- **Filtering:** Advanced metadata filtering (better than Chroma)
- **APIs:** REST + gRPC (fast, efficient)

#### Pros vs ChromaDB:
✅ **No SQLite dependency** - Custom storage engine (RocksDB-based)
✅ **Production-ready** - Used by enterprises
✅ **Advanced filtering** - Complex metadata queries
✅ **High performance** - Written in Rust
✅ **RESTful API** - Language-agnostic
✅ **Rich ecosystem** - LangChain, LlamaIndex integration
✅ **Distributed option** - Scalability path
✅ **Active development** - Strong community

#### Cons vs ChromaDB:
⚠️ **Requires Docker** - More deployment complexity
⚠️ **Separate service** - Not embedded like Chroma
⚠️ **Memory footprint** - Higher than embedded options
⚠️ **Overkill for 50-100 docs** - Designed for larger scale

#### Migration Effort from ChromaDB: ⭐⭐⭐⭐ (Easy)
- **Similarity:** 80% - Similar API patterns
- **Code Changes:** Moderate - Client initialization, query syntax
- **Data Migration:** Re-index required
- **Estimated Time:** 3-5 hours

**Migration Code Example:**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Setup
client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Create collection (replaces ChromaDB collection)
collection_name = "funding_docs"
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Index documents
points = []
for i, doc in enumerate(docs):
    vector = model.encode(doc['text'])
    points.append(PointStruct(
        id=i,
        vector=vector.tolist(),
        payload={
            "funding_id": doc['funding_id'],
            "title": doc['title'],
            "text": doc['text']
        }
    ))

client.upsert(collection_name=collection_name, points=points)

# Search
query_vector = model.encode("tablets for schools")
results = client.search(
    collection_name=collection_name,
    query_vector=query_vector.tolist(),
    limit=5
)
```

#### Cost: **FREE** (Self-hosted) ✅
Open-source, or managed cloud option (paid).

#### Oracle Cloud VM Compatibility:
✅ Docker support on OCI VM
✅ Works on ARM (A1.Flex)
✅ Persistent storage via volume mount
⚠️ Requires ~512MB-1GB RAM (more than embedded options)

---

### 4. Milvus Lite

**Overview:**
Lightweight version of Milvus, Python library for local vector search. Embedded mode, API-compatible with full Milvus.

#### Installation Complexity: ⭐⭐⭐⭐⭐ (Excellent)
```bash
pip install pymilvus>=2.4.3  # Includes Milvus Lite
```

Zero external dependencies.

#### Performance Characteristics:
- **Query Speed:** Fast for small datasets (<1M vectors)
- **Scale Limit:** Designed for <1M vectors (perfect for your use case)
- **API:** Same as full Milvus (upgrade path)

#### Pros vs ChromaDB:
✅ **No SQLite dependency** - Custom storage
✅ **Embedded** - Python library, no server
✅ **LangChain/LlamaIndex** - Built-in integrations
✅ **Upgrade path** - Migrate to full Milvus if needed
✅ **Simple API** - Similar to ChromaDB

#### Cons vs ChromaDB:
⚠️ **Windows not supported** (fine for Linux VM)
⚠️ **Newer project** - Less mature than alternatives
⚠️ **Scale limit** - Not for billion-scale (not your use case)

#### Migration Effort from ChromaDB: ⭐⭐⭐⭐ (Easy)
- **Similarity:** 85% - Very similar embedded approach
- **Code Changes:** Minimal API adjustments
- **Data Migration:** Re-index required
- **Estimated Time:** 2-4 hours

#### Cost: **FREE** ✅

#### Oracle Cloud VM Compatibility:
✅ Linux compatible (no Windows support needed)
✅ Lightweight, embedded

---

### 5. pgvector (PostgreSQL Extension)

**Overview:**
PostgreSQL extension adding vector similarity search. Turns PostgreSQL into a vector database.

#### Installation Complexity: ⭐⭐ (Complex - Requires PostgreSQL Setup)
```bash
# Install PostgreSQL + pgvector extension
# On Oracle DB (autonomous): pgvector may not be available
# Requires separate PostgreSQL instance or cloud service
```

Requires PostgreSQL installation/setup.

#### Performance Characteristics:
- **Query Speed:** Moderate (1.7x slower than FAISS in benchmarks)
- **Loading:** ~9.5ms per vector (slower than specialized DBs)
- **Optimized for:** Combined relational + vector queries

#### Pros vs ChromaDB:
✅ **No SQLite dependency** - Uses PostgreSQL
✅ **Unified database** - Relational + vector in one DB
✅ **ACID transactions** - Full PostgreSQL guarantees
✅ **Advanced filtering** - SQL WHERE clauses
✅ **Mature ecosystem** - PostgreSQL tools/integrations
✅ **IVFFlat + HNSW** - Efficient indexing options

#### Cons vs ChromaDB:
⚠️ **Requires PostgreSQL** - Can't use your Oracle DB
⚠️ **Additional infrastructure** - Separate DB instance needed
⚠️ **Slower than specialized** - Not optimized for pure vector search
⚠️ **Setup complexity** - Extension installation, schema setup
⚠️ **Cost** - PostgreSQL hosting (unless self-hosted)

#### Migration Effort from ChromaDB: ⭐⭐ (Difficult)
- **Similarity:** 40% - Different paradigm (DB vs library)
- **Code Changes:** Significant - SQL-based queries
- **Data Migration:** Schema setup + data import
- **Estimated Time:** 8-12 hours (includes PostgreSQL setup)

#### Cost: **FREE** (Self-hosted) or **$10-50/month** (Cloud PostgreSQL)

#### Oracle Cloud VM Compatibility:
✅ Can install PostgreSQL on VM
⚠️ Additional memory footprint (~256MB minimum)
⚠️ **Complexity:** Adds another database to manage

**Not recommended** - Adds unnecessary complexity when you already have Oracle DB.

---

### 6. Weaviate

**Overview:**
Production vector database with GraphQL API. Feature-rich, cloud-native, designed for large-scale deployments.

#### Installation Complexity: ⭐⭐ (Complex - Docker + Config Required)
```bash
# Requires Docker Compose with extensive configuration
docker-compose up -d
pip install weaviate-client
```

Heavy setup, many configuration options.

#### Performance Characteristics:
- **Query Speed:** Fast, optimized for production
- **Scale:** Enterprise-grade (millions to billions of vectors)
- **Features:** Auto-schema, modules, GraphQL, multi-tenancy

#### Pros vs ChromaDB:
✅ **No SQLite dependency**
✅ **Production-ready** - Enterprise features
✅ **GraphQL API** - Flexible querying
✅ **Modules** - Built-in text2vec, reranking, etc.
✅ **Multi-tenant** - Native support

#### Cons vs ChromaDB:
⚠️ **Heavy** - Docker + extensive config
⚠️ **Overkill** - Enterprise features you don't need
⚠️ **Complexity** - Steep learning curve
⚠️ **Resource-intensive** - High memory/CPU usage

#### Migration Effort: ⭐⭐ (Difficult)
- **Estimated Time:** 10-15 hours

#### Cost: **FREE** (Self-hosted) or **Managed Cloud** (paid)

#### Oracle Cloud VM Compatibility:
✅ Docker support
⚠️ **Not recommended** - Too heavy for your scale

---

### 7. ChromaDB with pysqlite3-binary Workaround ⚙️

**Overview:**
Fix the SQLite issue instead of switching databases.

#### Installation Complexity: ⭐⭐⭐⭐ (Very Good)
```bash
pip install pysqlite3-binary
```

Then add at top of your code (before importing chromadb):
```python
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb  # Now works!
```

#### Pros:
✅ **Zero migration** - Keep existing code
✅ **Well-tested** - Common workaround in 2025
✅ **Works on Streamlit, Azure, most platforms**

#### Cons:
⚠️ **Hacky solution** - Module substitution
⚠️ **Dependency on pysqlite3-binary** - Adds another package
⚠️ **May break** - Future ChromaDB updates could cause issues

#### Cost: **FREE** ✅

#### Oracle Cloud VM Compatibility:
✅ Should work on Linux VM

**Worth trying first** if you want to avoid migration work.

---

## Comparison Matrix

| Feature | LanceDB | FAISS | Qdrant | Milvus Lite | pgvector | Weaviate | ChromaDB+Fix |
|---------|---------|-------|--------|-------------|----------|----------|--------------|
| **No SQLite Dependency** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ Workaround |
| **Setup Complexity** | Very Easy | Easy | Medium | Very Easy | Hard | Hard | Very Easy |
| **Performance (50-100 docs)** | Excellent | Excellent | Excellent | Good | Good | Good | Good |
| **Migration Effort** | Low | Medium | Low | Low | High | High | None |
| **Memory Footprint** | Low | Low | Medium | Low | Medium | High | Low |
| **Production Readiness** | High | Very High | Very High | Medium | High | Very High | Medium |
| **Python Integration** | Excellent | Good | Excellent | Excellent | Good | Good | Excellent |
| **Scalability Path** | Excellent | Limited | Excellent | Good | Good | Excellent | Limited |
| **Community Support** | Growing | Mature | Strong | Growing | Mature | Strong | Strong |
| **Cost** | Free | Free | Free | Free | Free/Paid | Free/Paid | Free |
| **Docs Quality** | Good | Excellent | Excellent | Good | Excellent | Excellent | Excellent |

---

## Recommendations

### 🥇 **Primary Recommendation: LanceDB**

**Why:**
1. **Zero SQLite issues** - Uses Lance format (Parquet evolution)
2. **Drop-in simplicity** - Embedded like ChromaDB, minimal code changes
3. **Better performance** - 100x faster than Parquet for vector search
4. **Future-proof** - Multimodal support, disk-based scalability
5. **Perfect for your scale** - Handles 50-100 docs effortlessly
6. **Oracle Cloud compatible** - Lightweight, file-based, ARM-friendly

**Best for:** Teams wanting ChromaDB simplicity without SQLite headaches + performance boost.

**Next Steps:**
1. Install: `pip install lancedb sentence-transformers`
2. Migrate indexer code (2-3 hours)
3. Update search router (1-2 hours)
4. Test on dev environment
5. Deploy to OCI VM

---

### 🥈 **Runner-up: FAISS**

**Why:**
1. **Fastest search** - Industry standard performance
2. **Battle-tested** - Meta's production library
3. **Minimal dependencies** - Just one pip install
4. **Flexible** - Many indexing algorithms

**But:**
- Requires more boilerplate (manual metadata management)
- Lower-level API (more code to write)

**Best for:** Teams prioritizing raw speed over convenience, comfortable writing more code.

---

### 🥉 **Production Alternative: Qdrant**

**Why:**
1. **Production-grade** - Enterprise features out of the box
2. **Advanced filtering** - Better than ChromaDB
3. **Scalability** - Grow beyond 100 docs easily

**But:**
- Requires Docker (added complexity)
- Higher resource usage
- Overkill for current scale

**Best for:** Planning to scale significantly, want a "forever solution."

---

### 🔧 **Quick Fix: ChromaDB + pysqlite3-binary**

**Try this first** if you want to avoid migration:

```python
# Add at top of build_index.py and search.py
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```

```bash
pip install pysqlite3-binary
```

**Pros:** Zero migration, might just work
**Cons:** Hacky, may break later

**Recommendation:** Test this first (15 minutes), but have LanceDB as backup plan.

---

## Migration Effort Comparison

| Solution | Time Investment | Risk | Long-term Benefit |
|----------|----------------|------|-------------------|
| **LanceDB** | 3-5 hours | Low | High (better performance, no SQLite) |
| **FAISS** | 5-8 hours | Medium | Medium (fast but manual) |
| **Qdrant** | 4-6 hours | Low | High (production features) |
| **Milvus Lite** | 3-5 hours | Low | Medium (good but newer) |
| **ChromaDB Fix** | 15 mins | Medium | Low (temporary workaround) |

---

## Decision Framework

**Choose LanceDB if:**
- ✅ You want simplicity + performance
- ✅ You like ChromaDB's API but need better tech
- ✅ You want multimodal support (future-proofing)
- ✅ You prefer file-based storage (like ChromaDB)

**Choose FAISS if:**
- ✅ You prioritize raw speed above all
- ✅ You're comfortable writing more code
- ✅ You don't need complex metadata filtering
- ✅ You want the most battle-tested solution

**Choose Qdrant if:**
- ✅ You expect to scale significantly
- ✅ You want production features (monitoring, clustering)
- ✅ You're comfortable with Docker deployments
- ✅ You need advanced filtering

**Try ChromaDB Fix if:**
- ✅ You want to avoid migration work
- ✅ You're willing to risk future breakage
- ✅ You need a solution NOW (15 minutes)

---

## Implementation Plan: LanceDB Migration

### Phase 1: Setup (30 mins)
```bash
# Install dependencies
pip install lancedb
pip install sentence-transformers

# Create directory
mkdir -p /opt/lance_db
```

### Phase 2: Update Indexer (2 hours)
Modify `/backend/rag_indexer/build_index.py`:
- Replace ChromaDB client with LanceDB connection
- Adjust collection creation to table creation
- Update upsert logic
- Test indexing

### Phase 3: Update Search API (1-2 hours)
Modify `/backend/api/routers/search.py`:
- Update imports
- Replace ChromaDB queries with LanceDB searches
- Test search endpoint

### Phase 4: Update Advanced RAG (1 hour)
Check `/backend/rag_indexer/advanced_rag_pipeline.py`:
- Update hybrid searcher to use LanceDB
- Test RAG pipeline

### Phase 5: Testing & Deployment (1 hour)
- Run tests
- Verify on dev environment
- Deploy to OCI VM
- Monitor health endpoint

**Total Time:** 5-6 hours

---

## Code Migration Guide (LanceDB)

### Before (ChromaDB):
```python
import chromadb
from chromadb.config import Settings

# Setup
client = chromadb.PersistentClient(
    path='/opt/chroma_db',
    settings=Settings(anonymized_telemetry=False)
)
collection = client.get_or_create_collection(name='funding_docs')

# Index
collection.upsert(
    ids=['doc1', 'doc2'],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=['text1', 'text2'],
    metadatas=[{'funding_id': '123'}, {'funding_id': '456'}]
)

# Search
results = collection.query(
    query_embeddings=[[0.5, 0.6, ...]],
    n_results=5,
    where={'funding_id': '123'}
)
```

### After (LanceDB):
```python
import lancedb
from sentence_transformers import SentenceTransformer

# Setup
db = lancedb.connect('/opt/lance_db')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Index
data = [
    {
        'id': 'doc1',
        'text': 'text1',
        'vector': [0.1, 0.2, ...],
        'funding_id': '123'
    },
    {
        'id': 'doc2',
        'text': 'text2',
        'vector': [0.3, 0.4, ...],
        'funding_id': '456'
    }
]
table = db.create_table('funding_docs', data=data, mode='overwrite')

# Search
query_vector = [0.5, 0.6, ...]
results = table.search(query_vector) \
    .where("funding_id = '123'") \
    .limit(5) \
    .to_pandas()
```

**Key Differences:**
1. `PersistentClient` → `lancedb.connect()`
2. `collection` → `table`
3. `upsert()` → `create_table()` or `add()`
4. `query()` → `search().where().limit()`
5. Results: dict → pandas DataFrame

---

## Conclusion

**For Förder-Finder Grundschule, I recommend:**

1. **Quick Test (15 mins):** Try ChromaDB + pysqlite3-binary workaround first
2. **If that fails or feels unstable:** Migrate to **LanceDB** (3-5 hours)
3. **Alternative:** If you need maximum speed and don't mind more code, use **FAISS**

**LanceDB is the sweet spot:** Solves your SQLite problem, keeps simplicity, adds performance, and future-proofs with multimodal support. It's the modern ChromaDB replacement.

---

## Additional Resources

### LanceDB
- Docs: https://lancedb.github.io/lancedb/
- GitHub: https://github.com/lancedb/lancedb
- Sentence Transformers Integration: https://lancedb.github.io/lancedb/embeddings/

### FAISS
- GitHub: https://github.com/facebookresearch/faiss
- Docs: https://faiss.ai/
- Tutorial: https://www.pinecone.io/learn/series/faiss/faiss-tutorial/

### Qdrant
- Docs: https://qdrant.tech/documentation/
- Quickstart: https://qdrant.tech/documentation/quickstart/
- Python Client: https://github.com/qdrant/qdrant-client

### pysqlite3-binary Workaround
- PyPI: https://pypi.org/project/pysqlite3-binary/
- Stack Overflow: https://stackoverflow.com/questions/76958817/

---

**Report Generated:** 2025-11-03
**Author:** Claude Code Research
**Status:** Ready for implementation decision
