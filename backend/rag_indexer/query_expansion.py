#!/usr/bin/env python3
"""
Query Expansion using DeepSeek
Generates multiple query variants for better retrieval (RAG Fusion)

Research shows query expansion improves recall by 20-30%
"""

import os
import sys
import json
import httpx
from typing import List, Dict
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

load_dotenv()


class QueryExpander:
    """
    Query expansion using DeepSeek LLM
    Generates semantic variations of user queries
    """

    def __init__(
        self,
        api_url: str = None,
        api_key: str = None,
        model: str = None,
        num_variants: int = 3
    ):
        """
        Initialize query expander

        Args:
            api_url: DeepSeek API URL
            api_key: DeepSeek API key
            model: Model name
            num_variants: Default number of variants to generate
        """
        self.api_url = api_url or os.getenv(
            'DEEPSEEK_API_URL',
            'https://api.deepseek.com/v1/chat/completions'
        )
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.model = model or os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        self.default_num_variants = num_variants

        print(f'[INFO] Query Expander initialized (model: {self.model})')

    async def expand_query(
        self,
        query: str,
        num_variants: int = None,
        context: str = "Schul-Fördermittel"
    ) -> List[str]:
        """
        Generate query variants using DeepSeek

        Args:
            query: Original user query
            num_variants: Number of variants (default: self.default_num_variants)
            context: Domain context for better variants

        Returns:
            List of query variants (including original)
        """
        num_variants = num_variants or self.default_num_variants

        prompt = f"""
Generiere {num_variants} alternative Formulierungen für folgende Suchanfrage im Kontext von {context}.

ORIGINAL QUERY: "{query}"

REGELN:
1. Behalte die Kernbedeutung und Intention bei
2. Verwende Synonyme und verwandte Begriffe
3. Variiere zwischen spezifisch und allgemein
4. Decke verschiedene Aspekte ab (z.B. Ziel, Methode, Zielgruppe, Fördergeber)
5. Verwende deutsche Fachbegriffe aus dem Bildungsbereich

OUTPUT FORMAT (JSON):
{{
    "variants": [
        "Variante 1",
        "Variante 2",
        "Variante {num_variants}"
    ]
}}

BEISPIELE:

ORIGINAL: "Tablets für Grundschüler"
VARIANTS:
- "Digitale Endgeräte für Primarschule"
- "iPad Förderung Grundschule"
- "Hardware Ausstattung Klasse 1-4"

ORIGINAL: "MINT-Projekt Förderung"
VARIANTS:
- "Naturwissenschaftliche Bildung finanzieren"
- "Mathematik Informatik Technik Zuschuss"
- "BMBF Förderung Technik und Naturwissenschaften"

WICHTIG: Gib NUR das JSON zurück, keine zusätzlichen Erklärungen.
        """.strip()

        try:
            # Call DeepSeek API
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Du bist ein Experte für Suchanfragen-Optimierung im deutschen Bildungsbereich.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,  # Higher for diversity
                'max_tokens': 500
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()

            # Parse response
            response_data = response.json()
            generated_text = response_data['choices'][0]['message']['content']

            # Extract JSON
            # Try to find JSON in response (in case LLM adds text around it)
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = generated_text[json_start:json_end]
                variants_data = json.loads(json_str)
                variants = variants_data.get('variants', [])
            else:
                print('[WARNING] No JSON found in response, using original query only')
                variants = []

            # Include original query
            all_queries = [query] + variants

            return all_queries

        except Exception as e:
            print(f'[ERROR] Query expansion failed: {e}')
            # Fallback: return original query only
            return [query]

    async def extract_metadata_filters(
        self,
        query: str,
        available_filters: Dict[str, List[str]] = None
    ) -> Dict:
        """
        Extract metadata filters from natural language query
        (Self-Querying Retrieval)

        Args:
            query: User query
            available_filters: Dict of available filter options

        Returns:
            Dict with 'filters' and 'cleaned_query'
        """
        # Default available filters
        if available_filters is None:
            available_filters = {
                'region': ['Berlin', 'Brandenburg', 'Bayern', 'Bundesweit', 'Sachsen'],
                'funding_area': ['Bildung', 'Digitalisierung', 'MINT-Bildung', 'Bildungsprojekte'],
                'provider': ['BMBF', 'Land Berlin', 'Land Brandenburg', 'Deutsche Telekom Stiftung']
            }

        prompt = f"""
Analysiere folgende Suchanfrage und extrahiere Metadaten-Filter für eine Datenbank-Suche.

SUCHANFRAGE: "{query}"

VERFÜGBARE FILTER:
{json.dumps(available_filters, indent=2, ensure_ascii=False)}

ZUSÄTZLICHE FILTER:
- min_amount: Mindestfördersumme (Zahl in Euro)
- max_amount: Höchstfördersumme (Zahl in Euro)
- deadline_after: Deadline nach diesem Datum (ISO format YYYY-MM-DD)

OUTPUT FORMAT (JSON):
{{
    "filters": {{
        "region": "Wert aus Liste oder null",
        "funding_area": "Wert aus Liste oder null",
        "provider": "Wert aus Liste oder null",
        "min_amount": Zahl oder null,
        "max_amount": Zahl oder null
    }},
    "cleaned_query": "Suchanfrage ohne die Metadaten-Informationen"
}}

BEISPIELE:

QUERY: "Tablets für Grundschule in Berlin bis 5000 Euro"
OUTPUT:
{{
    "filters": {{
        "region": "Berlin",
        "funding_area": "Digitalisierung",
        "max_amount": 5000
    }},
    "cleaned_query": "Tablets für Grundschule"
}}

QUERY: "BMBF Förderung für MINT Projekte"
OUTPUT:
{{
    "filters": {{
        "provider": "BMBF",
        "funding_area": "MINT-Bildung"
    }},
    "cleaned_query": "Förderung für MINT Projekte"
}}

WICHTIG:
- Verwende NUR Werte aus den verfügbaren Listen
- Wenn kein passender Wert existiert, setze null
- Gib NUR das JSON zurück
        """.strip()

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Du bist ein Experte für strukturierte Datenextraktion aus Suchanfragen.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.3,  # Lower for accuracy
                'max_tokens': 300
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()

            response_data = response.json()
            generated_text = response_data['choices'][0]['message']['content']

            # Extract JSON
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = generated_text[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = {'filters': {}, 'cleaned_query': query}

            # Remove null values from filters
            filters = {k: v for k, v in result.get('filters', {}).items() if v is not None}
            result['filters'] = filters

            return result

        except Exception as e:
            print(f'[ERROR] Metadata extraction failed: {e}')
            return {'filters': {}, 'cleaned_query': query}


async def test_query_expansion():
    """Test query expander"""
    print('\n[TEST] Testing Query Expansion\n')

    expander = QueryExpander()

    # Test queries
    test_queries = [
        "Tablets für Grundschule",
        "MINT-Förderung Brandenburg",
        "Digitalisierung Bildung bis 10000 Euro"
    ]

    for query in test_queries:
        print(f'\n--- Original Query: "{query}" ---')

        # Query expansion
        variants = await expander.expand_query(query, num_variants=3)
        print(f'\n[EXPANDED QUERIES] ({len(variants)} total):')
        for i, variant in enumerate(variants):
            print(f'{i+1}. {variant}')

        # Metadata extraction
        metadata_result = await expander.extract_metadata_filters(query)
        print(f'\n[METADATA FILTERS]:')
        print(json.dumps(metadata_result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_query_expansion())
