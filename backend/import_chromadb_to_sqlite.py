#!/usr/bin/env python3
"""
Import unique Funding Opportunities from ChromaDB into SQLite database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import chromadb
import sqlite3
import uuid
from datetime import datetime
from collections import defaultdict

def generate_id():
    """Generate UUID without dashes"""
    return str(uuid.uuid4()).replace('-', '').upper()


def extract_funding_from_chromadb(chroma_path='./chroma_db_dev'):
    """
    Extract unique funding opportunities from ChromaDB metadata
    """
    print(f"📖 Reading ChromaDB from {chroma_path}...")

    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection(name='funding_docs')

    total_docs = collection.count()
    print(f"✅ Found {total_docs:,} documents in ChromaDB")

    # Get all documents with metadata
    results = collection.get(include=['metadatas', 'documents'])

    # Group by funding source to create unique opportunities
    funding_map = defaultdict(lambda: {
        'texts': [],
        'metadata': {}
    })

    for doc, meta in zip(results['documents'], results['metadatas']):
        title = meta.get('title', 'Unknown')
        provider = meta.get('provider', 'Unknown')

        key = f"{provider}|{title}"
        funding_map[key]['texts'].append(doc)
        funding_map[key]['metadata'] = meta

    unique_funding = []

    for key, data in funding_map.items():
        meta = data['metadata']
        texts = data['texts']

        # Combine all text chunks for this funding
        combined_text = '\n\n---\n\n'.join(texts)

        funding = {
            'funding_id': generate_id(),
            'title': meta.get('title', 'Unknown'),
            'provider': meta.get('provider', 'Unknown'),
            'description': texts[0][:500] if texts else '',  # First chunk as description
            'eligibility': '',  # Extract from chunks if available
            'categories': meta.get('category', ''),
            'target_groups': 'Grundschulen',
            'min_funding_amount': meta.get('min_amount'),
            'max_funding_amount': meta.get('max_amount'),
            'source_url': meta.get('url', ''),
            'application_deadline': meta.get('deadline', ''),
            'deadline': meta.get('deadline', ''),
            'region': meta.get('region', 'Bundesweit'),
            'cleaned_text': combined_text,
            'scraped_at': datetime.now().isoformat()
        }

        unique_funding.append(funding)

    print(f"✅ Extracted {len(unique_funding)} unique funding opportunities")
    return unique_funding


def import_to_sqlite(funding_list, db_path='./dev_database.db'):
    """
    Import funding opportunities into SQLite database
    """
    print(f"\n📝 Importing to SQLite database...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing funding opportunities (except demo data we want to keep)
    print("🗑️  Clearing old funding data...")
    cursor.execute("DELETE FROM FUNDING_OPPORTUNITIES WHERE funding_id NOT IN (?, ?, ?)",
                   ('61448BAC31054F4487C50F7B44A722B2',
                    'B49FCD4535D143BB879070C43243BEAE',
                    'F3F33056D5AD4C62A9CBEC1A8E3361BD'))

    # Insert new funding opportunities
    insert_query = """
    INSERT INTO FUNDING_OPPORTUNITIES (
        funding_id, title, provider, description, eligibility,
        categories, target_groups, funding_amount_min, funding_amount_max,
        source_url, deadline, region, cleaned_text, last_scraped
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    inserted = 0
    for funding in funding_list:
        try:
            cursor.execute(insert_query, (
                funding['funding_id'],
                funding['title'],
                funding['provider'],
                funding['description'],
                funding['eligibility'],
                funding['categories'],
                funding['target_groups'],
                funding['min_funding_amount'],
                funding['max_funding_amount'],
                funding['source_url'],
                funding['deadline'],
                funding['region'],
                funding['cleaned_text'],
                funding['scraped_at']
            ))
            inserted += 1
        except Exception as e:
            print(f"⚠️  Error inserting {funding['title']}: {e}")

    conn.commit()
    conn.close()

    print(f"✅ Imported {inserted} funding opportunities")

    return inserted


def main():
    """
    Main execution
    """
    print("="* 80)
    print("ChromaDB to SQLite Import")
    print("="* 80)

    # Extract from ChromaDB
    funding_list = extract_funding_from_chromadb()

    # Import to SQLite
    imported = import_to_sqlite(funding_list)

    print("\n" + "="* 80)
    print(f"✅ SUCCESS! Imported {imported} unique funding opportunities")
    print("="* 80)

    # Verify
    conn = sqlite3.connect('./dev_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM FUNDING_OPPORTUNITIES")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT provider) FROM FUNDING_OPPORTUNITIES")
    providers = cursor.fetchone()[0]
    conn.close()

    print(f"\n📊 Database now contains:")
    print(f"   - {total} total funding opportunities")
    print(f"   - {providers} unique providers")
    print(f"   - 2,209 documents in ChromaDB for RAG search")


if __name__ == '__main__':
    main()
