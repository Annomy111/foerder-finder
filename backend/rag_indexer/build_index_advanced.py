#!/usr/bin/env python3
"""
Advanced RAG Index Builder
Builds both Dense (ChromaDB with BGE-M3) and Sparse (BM25) indices

Usage:
    python build_index_advanced.py --rebuild  # Full rebuild
    python build_index_advanced.py --incremental  # Update only new docs
"""

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

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

from utils.db_adapter import get_db_cursor
from rag_indexer.advanced_embedder import AdvancedEmbedder
from rag_indexer.hybrid_searcher import HybridSearcher

load_dotenv()


class AdvancedIndexBuilder:
    """Build advanced RAG indices (Dense + Sparse)"""

    def __init__(self):
        """Initialize builder"""
        # ChromaDB Setup
        self.chroma_path = os.getenv('CHROMA_DB_PATH', '/opt/chroma_db')
        self.collection_name = os.getenv('CHROMA_COLLECTION_NAME', 'funding_docs')

        print(f'[INFO] ChromaDB Path: {self.chroma_path}')
        print(f'[INFO] Collection: {self.collection_name}')

        # Create ChromaDB Client
        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={'description': 'Fördermittel-Dokumente für Advanced RAG'}
        )

        # Advanced Embedder (BGE-M3 or fallback)
        print('[INFO] Loading embedding model...')
        self.embedder = AdvancedEmbedder()

        print('[SUCCESS] Index builder initialized')

    def fetch_funding_documents(self) -> List[Dict]:
        """
        Fetch all active funding documents from database

        Returns:
            List of document dicts
        """
        print('[INFO] Fetching funding documents from Oracle DB...')

        # Adapt query for SQLite (no RAWTOHEX, no is_active column)
        use_sqlite = os.getenv('USE_SQLITE', 'false').lower() == 'true'

        if use_sqlite:
            query = """
            SELECT
                funding_id,
                title,
                cleaned_text,
                provider,
                region,
                funding_area
            FROM FUNDING_OPPORTUNITIES
            WHERE cleaned_text IS NOT NULL
              AND LENGTH(cleaned_text) > 100
            ORDER BY last_scraped DESC
            """
        else:
            query = """
            SELECT
                RAWTOHEX(funding_id) as funding_id,
                title,
                cleaned_text,
                provider,
                region,
                funding_area
            FROM FUNDING_OPPORTUNITIES
            WHERE is_active = 1
              AND cleaned_text IS NOT NULL
              AND LENGTH(cleaned_text) > 100
            ORDER BY scraped_at DESC
            """

        documents = []
        with get_db_cursor() as cursor:
            cursor.execute(query)

            columns = [col[0].lower() for col in cursor.description]

            for row in cursor:
                doc = dict(zip(columns, row))
                documents.append(doc)

        print(f'[INFO] Fetched {len(documents)} funding documents')
        return documents

    def chunk_document(self, doc: Dict) -> List[Dict]:
        """
        Chunk document into smaller pieces

        For now, using simple character-based chunking
        TODO: Implement semantic chunking with DeepSeek

        Args:
            doc: Document dict

        Returns:
            List of chunk dicts
        """
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        text = doc['cleaned_text']
        if not text or len(text) < 10:
            return []

        # Character-based chunking (to be replaced with semantic)
        chunk_size = int(os.getenv('RAG_CHUNK_SIZE', 1000))
        chunk_overlap = int(os.getenv('RAG_CHUNK_OVERLAP', 200))

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=['\n\n', '\n', '. ', ' ', '']
        )

        chunks = text_splitter.split_text(text)

        # Create chunk dicts
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                'chunk_id': f"{doc['funding_id']}_chunk_{i}",
                'funding_id': doc['funding_id'],
                'title': doc['title'],
                'chunk_text': chunk_text,
                'chunk_index': i,
                'provider': doc.get('provider', ''),
                'region': doc.get('region', ''),
                'funding_area': doc.get('funding_area', '')
            }
            chunk_dicts.append(chunk_dict)

        return chunk_dicts

    def index_chunks_dense(self, chunks: List[Dict]) -> None:
        """
        Index chunks in ChromaDB (dense vectors)

        Args:
            chunks: List of chunk dicts
        """
        if not chunks:
            return

        print(f'[INFO] Indexing {len(chunks)} chunks in ChromaDB (dense)...')

        # Extract texts
        texts = [chunk['chunk_text'] for chunk in chunks]

        # Generate embeddings (batch)
        print('[INFO] Generating embeddings with BGE-M3...')
        embeddings = self.embedder.embed_documents(texts, batch_size=32, show_progress=True)

        # Prepare for ChromaDB
        ids = [chunk['chunk_id'] for chunk in chunks]
        metadatas = [
            {
                'funding_id': chunk['funding_id'],
                'title': chunk['title'],
                'chunk_index': chunk['chunk_index'],
                'provider': chunk['provider'],
                'region': chunk['region'],
                'funding_area': chunk['funding_area']
            }
            for chunk in chunks
        ]

        # Upsert in ChromaDB
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )

        print(f'[SUCCESS] Indexed {len(chunks)} chunks in ChromaDB')

    def build_bm25_index(self, all_chunks: List[Dict]) -> None:
        """
        Build BM25 sparse index

        Args:
            all_chunks: All chunks from all documents
        """
        print(f'[INFO] Building BM25 index for {len(all_chunks)} chunks...')

        # Prepare documents for BM25
        bm25_docs = [
            {
                'id': chunk['chunk_id'],
                'text': chunk['chunk_text']
            }
            for chunk in all_chunks
        ]

        # Build BM25 index using HybridSearcher
        searcher = HybridSearcher()
        searcher.build_bm25_index(bm25_docs)

        print('[SUCCESS] BM25 index built')

    def rebuild_index(self) -> None:
        """Rebuild complete index (Dense + Sparse)"""
        print('[START] Rebuilding Advanced RAG Index...')
        start_time = datetime.now()

        # 1. Fetch documents
        documents = self.fetch_funding_documents()

        if not documents:
            print('[WARNING] No documents found!')
            return

        # 2. Chunk all documents
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
            print(f'[INFO] Chunked "{doc["title"][:50]}..." -> {len(chunks)} chunks')

        print(f'[INFO] Total chunks: {len(all_chunks)}')

        # 3. Index in ChromaDB (batches)
        batch_size = 500
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            print(f'[INFO] Indexing batch {i // batch_size + 1}/{(len(all_chunks) // batch_size) + 1}')
            self.index_chunks_dense(batch)

        # 4. Build BM25 Index
        self.build_bm25_index(all_chunks)

        # 5. Stats
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        collection_count = self.collection.count()
        print(f'\n[SUCCESS] Advanced RAG Index rebuild complete!')
        print(f'[STATS] Total documents: {len(documents)}')
        print(f'[STATS] Total chunks: {len(all_chunks)}')
        print(f'[STATS] ChromaDB collection count: {collection_count}')
        print(f'[STATS] Duration: {duration:.2f} seconds')
        print(f'[STATS] Embedder: {self.embedder.get_model_info()["model_name"]}')


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Build Advanced RAG Index')
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Full rebuild of indices'
    )
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Incremental update (TODO: not implemented yet)'
    )

    args = parser.parse_args()

    builder = AdvancedIndexBuilder()

    if args.rebuild or not args.incremental:
        builder.rebuild_index()
    else:
        print('[ERROR] Incremental update not implemented yet')
        print('[INFO] Use --rebuild for full rebuild')


if __name__ == '__main__':
    main()
