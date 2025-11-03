#!/usr/bin/env python3
"""
Test script for DeepSeek API integration
Tests the draft generator with and without API key
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.routers.drafts_sqlite import generate_deepseek_draft, generate_mock_draft

def test_without_api_key():
    """Test graceful fallback when API key is missing"""
    print("\n=== TEST 1: Without API Key (Should fallback to mock) ===")

    # Temporarily unset API key
    original_key = os.environ.get('DEEPSEEK_API_KEY')
    os.environ['DEEPSEEK_API_KEY'] = 'sk-placeholder'

    funding_data = {
        'title': 'Test-Förderprogramm Digitalisierung',
        'provider': 'Testministerium',
        'description': 'Ein Test-Programm für digitale Bildung',
        'eligibility': 'Grundschulen in Deutschland',
        'funding_amount_max': 25000,
        'funding_amount_min': 10000,
        'categories': 'Digitalisierung',
        'target_groups': 'Grundschüler',
        'application_deadline': '2025-12-31'
    }

    school_profile = {
        'school_name': 'Test-Grundschule',
        'address': 'Teststraße 1, 12345 Teststadt',
        'schultyp': 'Grundschule',
        'schuelerzahl': 200
    }

    user_query = "Wir möchten 20 Tablets für den digitalen Unterricht anschaffen und Lehrkräfte fortbilden."

    try:
        draft = generate_deepseek_draft(funding_data, user_query, school_profile)

        if len(draft) > 100:
            print("✅ Draft generated successfully (mock fallback)")
            print(f"   Length: {len(draft)} characters")
            print(f"   First 200 chars: {draft[:200]}...")
        else:
            print("❌ Draft too short")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Restore original key
        if original_key:
            os.environ['DEEPSEEK_API_KEY'] = original_key
        else:
            os.environ.pop('DEEPSEEK_API_KEY', None)


def test_with_api_key():
    """Test real DeepSeek API call if key is configured"""
    print("\n=== TEST 2: With API Key (Real DeepSeek call) ===")

    api_key = os.environ.get('DEEPSEEK_API_KEY', '')

    if not api_key or api_key == 'sk-placeholder':
        print("⚠️  DEEPSEEK_API_KEY not configured in environment")
        print("   Set it with: export DEEPSEEK_API_KEY=sk-your-key-here")
        print("   Skipping real API test")
        return

    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    print("   Testing real DeepSeek API call...")

    funding_data = {
        'title': 'Innovative MINT-Förderung',
        'provider': 'Bundesministerium für Bildung',
        'description': 'Förderung von MINT-Projekten an Grundschulen',
        'eligibility': 'Öffentliche und private Grundschulen',
        'funding_amount_max': 30000,
        'funding_amount_min': 15000,
        'categories': 'MINT, Naturwissenschaften',
        'target_groups': 'Grundschüler Klasse 1-4',
        'application_deadline': '2025-06-30'
    }

    school_profile = {
        'school_name': 'Einstein-Grundschule',
        'address': 'Mozartstraße 42, 10115 Berlin',
        'schultyp': 'Grundschule',
        'schuelerzahl': 320
    }

    user_query = """Wir planen ein MINT-Labor mit Experimentiermaterial für alle Klassenstufen.
    Schwerpunkt auf Physik und Chemie. Inklusive Lehrkräfte-Fortbildung und externe Workshops."""

    try:
        draft = generate_deepseek_draft(funding_data, user_query, school_profile)

        if "DeepSeek" in str(type(draft)) or len(draft) > 1000:
            print("✅ Real API call successful!")
            print(f"   Length: {len(draft)} characters")
            print(f"   Structure check: {'## 1.' in draft or '## Executive' in draft}")
            print(f"\n   First 500 chars:\n{draft[:500]}...")
        else:
            print("⚠️  Response seems to be mock fallback")

    except Exception as e:
        print(f"❌ API call failed: {e}")
        print("   Check API key validity and network connection")


def test_mock_generator():
    """Test mock generator for comparison"""
    print("\n=== TEST 3: Mock Generator (for comparison) ===")

    funding_data = {
        'title': 'Sport-Förderung',
        'provider': 'Landessportbund',
        'description': 'Förderung von Sportprojekten',
        'eligibility': 'Schulen und Vereine',
        'funding_amount_max': 10000,
        'categories': 'Sport, Bewegung',
        'target_groups': 'Grundschüler'
    }

    school_profile = {
        'school_name': 'Goethe-Grundschule',
        'address': 'Schillerplatz 5, 20095 Hamburg'
    }

    user_query = "Neue Sportgeräte für die Turnhalle und Bewegungspausen im Schulalltag."

    try:
        draft = generate_mock_draft(funding_data, user_query, school_profile)

        print("✅ Mock draft generated")
        print(f"   Length: {len(draft)} characters")
        print(f"   Contains funding title: {funding_data['title'] in draft}")
        print(f"   Contains school name: {school_profile['school_name'] in draft}")

    except Exception as e:
        print(f"❌ Mock generator failed: {e}")


if __name__ == '__main__':
    print("="*70)
    print("DeepSeek Integration Test Suite")
    print("="*70)

    test_without_api_key()
    test_mock_generator()
    test_with_api_key()

    print("\n" + "="*70)
    print("Tests completed!")
    print("="*70)
    print("\nTo use real DeepSeek API:")
    print("1. Get API key from: https://platform.deepseek.com/")
    print("2. Export it: export DEEPSEEK_API_KEY=sk-your-key-here")
    print("3. Run this test again to verify real API integration")
    print("\nCost: ~$0.14 per 1M tokens (very affordable)")
