"""
Test Search API Endpoints
Testet die neu implementierte RAG-Search API mit Grundschul-Queries
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def get_auth_token():
    """Login und Token holen"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "admin@gs-musterberg.de", "password": "test1234"}
    )
    return response.json()["access_token"]


def test_rag_health(token):
    """RAG Health Check testen"""
    print("\n" + "="*60)
    print("TEST 1: RAG Health Check")
    print("="*60)

    response = requests.get(
        f"{BASE_URL}/api/v1/search/health",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    return response.status_code == 200


def test_quick_search(token):
    """Quick Search (GET) testen"""
    print("\n" + "="*60)
    print("TEST 2: Quick Search - 'Tablets für Grundschule'")
    print("="*60)

    response = requests.get(
        f"{BASE_URL}/api/v1/search/quick",
        params={"q": "Tablets für Grundschule", "limit": 3},
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Query: {data['query']}")
    print(f"Total Results: {data['total_results']}")
    print(f"Retrieval Time: {data['retrieval_time_ms']:.2f}ms")
    print(f"Pipeline Config: {data['pipeline_config']}")

    print("\nTop 3 Results:")
    for i, result in enumerate(data['results'], 1):
        print(f"\n  [{i}] Score: {result['score']:.4f}")
        print(f"      Funding ID: {result['funding_id']}")
        print(f"      Text: {result['text'][:200]}...")
        print(f"      Metadata: {result['metadata']}")

    return response.status_code == 200


def test_advanced_search(token):
    """Advanced Search (POST) mit allen Features testen"""
    print("\n" + "="*60)
    print("TEST 3: Advanced Search - 'Leseförderung Grundschule Berlin'")
    print("="*60)

    request_body = {
        "query": "Leseförderung Grundschule Berlin",
        "top_k": 5,
        "region": "Berlin",
        "expand_queries": True,
        "rerank_results": True
    }

    print(f"Request Body: {json.dumps(request_body, indent=2)}")

    start = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/search/",
        json=request_body,
        headers={"Authorization": f"Bearer {token}"}
    )
    duration = (time.time() - start) * 1000

    print(f"\nStatus Code: {response.status_code}")
    print(f"Total Request Time: {duration:.2f}ms")

    data = response.json()
    print(f"Query: {data['query']}")
    print(f"Total Results: {data['total_results']}")
    print(f"Retrieval Time (server): {data['retrieval_time_ms']:.2f}ms")
    print(f"Pipeline Config: {data['pipeline_config']}")

    print("\nTop 5 Results:")
    for i, result in enumerate(data['results'], 1):
        print(f"\n  [{i}] Score: {result['score']:.4f}")
        print(f"      Funding ID: {result['funding_id']}")
        print(f"      Text: {result['text'][:250]}...")
        print(f"      Metadata: {result['metadata']}")

    return response.status_code == 200


def test_grundschule_specific_queries(token):
    """Mehrere Grundschul-spezifische Queries testen"""
    print("\n" + "="*60)
    print("TEST 4: Grundschul-spezifische Queries")
    print("="*60)

    queries = [
        "Musikunterricht Grundschule NRW",
        "Tablets und digitale Medien",
        "Sportprogramme für Grundschulen",
        "MINT-Bildung Grundschule",
        "Umweltbildung nachhaltige Entwicklung"
    ]

    results = []
    for query in queries:
        print(f"\nQuery: '{query}'")

        response = requests.post(
            f"{BASE_URL}/api/v1/search/",
            json={
                "query": query,
                "top_k": 3,
                "expand_queries": False,  # Faster
                "rerank_results": False   # Faster
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Found {data['total_results']} results in {data['retrieval_time_ms']:.2f}ms")
            if data['results']:
                top_result = data['results'][0]
                print(f"  Top Result: Score={top_result['score']:.4f}, Text={top_result['text'][:100]}...")
            results.append(True)
        else:
            print(f"  ❌ Error: {response.status_code}")
            results.append(False)

    return all(results)


def main():
    """Alle Tests durchführen"""
    print("\n" + "="*80)
    print(" RAG SEARCH API TEST SUITE - Förder-Finder Grundschule")
    print("="*80)

    # Login
    print("\n[SETUP] Authenticating...")
    try:
        token = get_auth_token()
        print(f"✅ Token received: {token[:20]}...")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    # Run Tests
    test_results = []

    try:
        test_results.append(("RAG Health Check", test_rag_health(token)))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        test_results.append(("RAG Health Check", False))

    try:
        test_results.append(("Quick Search", test_quick_search(token)))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        test_results.append(("Quick Search", False))

    try:
        test_results.append(("Advanced Search", test_advanced_search(token)))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        test_results.append(("Advanced Search", False))

    try:
        test_results.append(("Grundschule Queries", test_grundschule_specific_queries(token)))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        test_results.append(("Grundschule Queries", False))

    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)

    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed in test_results if passed)

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.0f}%)")

    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! RAG Search API is ready for production!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")


if __name__ == "__main__":
    main()
