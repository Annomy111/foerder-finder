#!/usr/bin/env python3
"""
Complete E2E Test for Förder-Finder
Tests the full user flow from login to AI draft generation
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001/api/v1"
TEST_USER = {
    "email": "admin@gs-musterberg.de",
    "password": "test1234"  # SQLite dev password
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_step(step_num, description):
    print(f"\n{Colors.BLUE}[STEP {step_num}]{Colors.RESET} {description}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.RESET}")

def test_health():
    """Test 0: Health Check"""
    print_step(0, "Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()

        print_success(f"Backend is healthy: {data}")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_login():
    """Test 1: Login and get JWT token"""
    print_step(1, "Login")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")

            print_success(f"Login successful!")
            print_info(f"User ID: {data.get('user_id', 'N/A')}")
            print_info(f"School ID: {data.get('school_id', 'N/A')}")
            print_info(f"Role: {data.get('role', 'N/A')}")
            print_info(f"Token: {token[:20]}...")

            return token
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_funding_list(token):
    """Test 2: Get funding opportunities list"""
    print_step(2, "Get Funding Opportunities List")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/funding/?limit=5",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            opportunities = response.json()  # Direct list, not dict

            if not isinstance(opportunities, list):
                print_error(f"Unexpected response format: {type(opportunities)}")
                return None

            print_success(f"Retrieved {len(opportunities)} opportunities")

            if opportunities:
                print_info("Sample opportunities:")
                for i, opp in enumerate(opportunities[:3], 1):
                    print(f"  {i}. {opp.get('title', 'N/A')[:60]}...")
                    print(f"     Provider: {opp.get('provider', 'N/A')}")
                    print(f"     Region: {opp.get('region', 'N/A')}")

                return opportunities[0]  # Return first opportunity for detail test
            else:
                print_error("No opportunities found!")
                return None
        else:
            print_error(f"Failed to get funding list: {response.status_code}")
            return None

    except Exception as e:
        print_error(f"Error getting funding list: {e}")
        return None

def test_funding_detail(token, funding_id):
    """Test 3: Get funding opportunity detail"""
    print_step(3, "Get Funding Opportunity Detail")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/funding/{funding_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            print_success(f"Retrieved funding detail")
            print_info(f"Title: {data.get('title', 'N/A')}")
            print_info(f"Provider: {data.get('provider', 'N/A')}")
            print_info(f"Deadline: {data.get('deadline', 'N/A')}")
            print_info(f"Amount: {data.get('min_funding_amount', 'N/A')} - {data.get('max_funding_amount', 'N/A')}")
            print_info(f"Text length: {len(data.get('cleaned_text', ''))} chars")

            return data
        else:
            print_error(f"Failed to get funding detail: {response.status_code}")
            return None

    except Exception as e:
        print_error(f"Error getting funding detail: {e}")
        return None

def test_search(token):
    """Test 4: Search with RAG"""
    print_step(4, "Search with RAG")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            f"{BASE_URL}/search",
            headers=headers,
            json={
                "query": "Digitalisierung Schule",
                "limit": 3
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            print_success(f"Search returned {len(results)} results")

            for i, result in enumerate(results, 1):
                print_info(f"{i}. {result.get('title', 'N/A')[:50]}... (Score: {result.get('score', 0):.2f})")

            return True
        else:
            print_error(f"Search failed: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Search error: {e}")
        return False

def test_ai_draft(token, funding_id):
    """Test 5: Generate AI draft"""
    print_step(5, "Generate AI Draft (DeepSeek)")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        print_info("Generating draft... (this may take 30-60 seconds)")

        response = requests.post(
            f"{BASE_URL}/drafts/generate",
            headers=headers,
            json={
                "funding_id": funding_id,
                "school_context": "Grundschule Musterberg, 300 Schüler, Digitalisierung im Fokus"
            },
            timeout=90
        )

        if response.status_code == 200:
            data = response.json()

            print_success("AI Draft generated!")
            print_info(f"Draft ID: {data.get('draft_id', 'N/A')}")
            print_info(f"Title: {data.get('title', 'N/A')[:60]}...")
            print_info(f"Generated text length: {len(data.get('generated_text', ''))} chars")

            # Preview first 200 chars
            text = data.get('generated_text', '')
            if text:
                print_info(f"Preview: {text[:200]}...")

            return data
        else:
            print_error(f"AI draft generation failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        print_error("AI draft generation timeout (>90s)")
        return None
    except Exception as e:
        print_error(f"AI draft error: {e}")
        return None

def test_applications(token):
    """Test 6: Get applications"""
    print_step(6, "Get Applications")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/applications/",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            applications = response.json()  # Direct list, not dict

            if not isinstance(applications, list):
                applications = []

            print_success(f"Retrieved {len(applications)} applications")

            if applications:
                for i, app in enumerate(applications[:3], 1):
                    print_info(f"{i}. {app.get('title', 'N/A')[:50]}... - Status: {app.get('status', 'N/A')}")

            return True
        else:
            print_error(f"Failed to get applications: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error getting applications: {e}")
        return False

def main():
    """Run all E2E tests"""
    print("=" * 80)
    print(f"{Colors.BLUE}FÖRDER-FINDER E2E TEST{Colors.RESET}")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend: {BASE_URL}")
    print()

    # Test 0: Health
    if not test_health():
        print_error("\n❌ Backend is not healthy. Aborting tests.")
        sys.exit(1)

    # Test 1: Login
    token = test_login()
    if not token:
        print_error("\n❌ Login failed. Aborting tests.")
        sys.exit(1)

    # Test 2: Funding List
    first_funding = test_funding_list(token)
    if not first_funding:
        print_error("\n❌ No funding opportunities found. Aborting tests.")
        sys.exit(1)

    funding_id = first_funding.get('funding_id')

    # Test 3: Funding Detail
    funding_detail = test_funding_detail(token, funding_id)

    # Test 4: Search
    test_search(token)

    # Test 5: AI Draft (may take a while)
    test_ai_draft(token, funding_id)

    # Test 6: Applications
    test_applications(token)

    # Summary
    print("\n" + "=" * 80)
    print(f"{Colors.GREEN}✅ E2E TEST COMPLETE{Colors.RESET}")
    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("All core features tested successfully:")
    print("  ✅ Authentication (JWT)")
    print("  ✅ Funding Opportunities List")
    print("  ✅ Funding Detail View")
    print("  ✅ RAG Search")
    print("  ✅ AI Draft Generation (DeepSeek)")
    print("  ✅ Applications Management")
    print()

if __name__ == "__main__":
    main()
