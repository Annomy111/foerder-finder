#!/usr/bin/env python3
"""
RAG Indexing Service - ChromaDB Indexierung
Liest Fördermittel-Texte aus Oracle DB, chunked sie und erstellt Vektor-Index

WICHTIG: Muss NACH dem Scraper laufen (cronjob: 30 Min später)
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

# Import parent modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

from utils.database import get_db_cursor

load_dotenv()


class RAGIndexer:
    """RAG Indexing Service für Fördermittel-Texte"""

    def __init__(self):
        """Initialisiert den Indexer"""
        # ChromaDB Setup
        self.chroma_path = os.getenv('CHROMA_DB_PATH', '/opt/chroma_db')
        self.collection_name = os.getenv('CHROMA_COLLECTION_NAME', 'funding_docs')

        print(f'[INFO] ChromaDB Pfad: {self.chroma_path}')
        print(f'[INFO] Collection: {self.collection_name}')

        # Erstelle ChromaDB Client (persistent)
        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )

        # Hole oder erstelle Collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={'description': 'Fördermittel-Dokumente für RAG'}
        )

        # Embedding Model (MUSS identisch mit API sein!)
        model_name = os.getenv('EMBEDDING_MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2')
        print(f'[INFO] Lade Embedding-Modell: {model_name}')
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # Text Splitter
        chunk_size = int(os.getenv('RAG_CHUNK_SIZE', 1000))
        chunk_overlap = int(os.getenv('RAG_CHUNK_OVERLAP', 200))
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=['\n\n', '\n', '. ', ' ', '']
        )

        print(f'[INFO] Text Splitter: chunk_size={chunk_size}, overlap={chunk_overlap}')

    def fetch_funding_documents(self) -> List[Dict]:
        """
        Holt alle aktiven Fördermittel aus der Datenbank

        Returns:
            Liste von Dicts mit funding_id, title, cleaned_text
        """
        print('[INFO] Fetching funding documents from Oracle DB...')

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

            # Hole Column-Namen
            columns = [col[0].lower() for col in cursor.description]

            # Fetch alle Rows
            for row in cursor:
                doc = dict(zip(columns, row))
                documents.append(doc)

        print(f'[INFO] Fetched {len(documents)} funding documents')
        return documents

    def chunk_document(self, doc: Dict) -> List[Dict]:
        """
        Chunked ein Dokument in kleinere Textabschnitte

        Args:
            doc: Dokument-Dict mit cleaned_text

        Returns:
            Liste von Chunk-Dicts
        """
        text = doc['cleaned_text']
        if not text or len(text) < 10:
            return []

        # Erstelle Chunks
        chunks = self.text_splitter.split_text(text)

        # Erstelle Chunk-Dicts mit Metadaten
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

    def index_chunks(self, chunks: List[Dict]) -> None:
        """
        Erstellt Embeddings und speichert Chunks in ChromaDB

        Args:
            chunks: Liste von Chunk-Dicts
        """
        if not chunks:
            return

        print(f'[INFO] Indexing {len(chunks)} chunks...')

        # Extrahiere Texte für Embedding
        texts = [chunk['chunk_text'] for chunk in chunks]

        # Erstelle Embeddings (batch)
        print('[INFO] Generating embeddings...')
        embeddings = self.embeddings.embed_documents(texts)

        # Prepare für ChromaDB
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

        # Upsert in ChromaDB (ersetzt existierende IDs)
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        print(f'[INFO] Successfully indexed {len(chunks)} chunks')

    def rebuild_index(self) -> None:
        """
        Baut den kompletten Index neu auf (alle Dokumente)
        """
        print('[START] Rebuilding ChromaDB index...')
        start_time = datetime.now()

        # 1. Fetch alle Dokumente
        documents = self.fetch_funding_documents()

        if not documents:
            print('[WARNING] Keine Dokumente gefunden!')
            return

        # 2. Chunk alle Dokumente
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
            print(f'[INFO] Chunked "{doc["title"][:50]}..." -> {len(chunks)} chunks')

        print(f'[INFO] Total chunks: {len(all_chunks)}')

        # 3. Index in batches (ChromaDB limit: ~1000 per batch)
        batch_size = 500
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            print(f'[INFO] Indexing batch {i // batch_size + 1}/{(len(all_chunks) // batch_size) + 1}')
            self.index_chunks(batch)

        # 4. Stats
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        collection_count = self.collection.count()
        print(f'\n[SUCCESS] Index rebuild complete!')
        print(f'[STATS] Total documents: {len(documents)}')
        print(f'[STATS] Total chunks: {len(all_chunks)}')
        print(f'[STATS] Collection count: {collection_count}')
        print(f'[STATS] Duration: {duration:.2f} seconds')

    def test_search(self, query: str, funding_id: str = None) -> None:
        """
        Testet die Vektor-Suche

        Args:
            query: Suchquery
            funding_id: Optional - filtere nach funding_id
        """
        print(f'\n[TEST] Searching for: "{query}"')
        if funding_id:
            print(f'[TEST] Filtered by funding_id: {funding_id}')

        # Embedde Query
        query_embedding = self.embeddings.embed_query(query)

        # Suche
        where_filter = {'funding_id': funding_id} if funding_id else None
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where=where_filter
        )

        # Print Results
        print(f'\n[RESULTS] Found {len(results["documents"][0])} results:')
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f'\n--- Result {i + 1} ---')
            print(f'Title: {metadata["title"]}')
            print(f'Provider: {metadata["provider"]}')
            print(f'Chunk: {doc[:200]}...')


def main():
    """Main Entry Point"""
    indexer = RAGIndexer()

    # Rebuild Index
    indexer.rebuild_index()

    # Optional: Test Search (uncomment für Testing)
    # indexer.test_search('Tablets für Grundschule')


if __name__ == '__main__':
    main()
