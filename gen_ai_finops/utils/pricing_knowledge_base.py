"""
Pricing Knowledge Base - The "Brain" of GenAIFinOps
Manages the ChromaDB vector database for semantic pricing queries.
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from utils.data_normalizer import pricing_to_text, normalize_pricing_data


class PricingKnowledgeBase:
    """
    Wrapper class for ChromaDB that manages LLM pricing information.
    Provides semantic search capabilities over pricing data using vector embeddings.
    """

    def __init__(
        self,
        persist_directory: str = "./data/chroma_db",
        collection_name: str = "pricing_models"
    ):
        """
        Initialize the Pricing Knowledge Base with ChromaDB.

        Args:
            persist_directory: Path to persist ChromaDB data (default: ./data/chroma_db)
            collection_name: Name of the ChromaDB collection (default: pricing_models)
        """
        self.persist_directory = Path(persist_directory).resolve()
        self.collection_name = collection_name

        self.persist_directory.mkdir(parents=True, exist_ok=True)

        print(f"Initializing ChromaDB at: {self.persist_directory}")

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "LLM pricing information from multiple providers"}
        )

        print(f"ChromaDB collection '{self.collection_name}' ready.")
        print(f"Current document count: {self.collection.count()}")

    def add_prices(self, pricing_data: List[Dict[str, Any]]) -> int:
        """
        Add pricing information to the knowledge base.
        Converts pricing data to text, generates embeddings, and stores in ChromaDB.

        Args:
            pricing_data: List of pricing dictionaries (must follow schema)

        Returns:
            int: Number of entries successfully added

        Example:
            >>> kb = PricingKnowledgeBase()
            >>> data = [{
            ...     "provider": "OpenAI",
            ...     "model_name": "gpt-4",
            ...     "input_cost_per_1m_tokens": 30.0,
            ...     "output_cost_per_1m_tokens": 60.0
            ... }]
            >>> kb.add_prices(data)
            1
        """
        if not pricing_data:
            print("Warning: No pricing data provided.")
            return 0

        if isinstance(pricing_data, dict):
            pricing_data = [pricing_data]

        documents = []
        metadatas = []
        ids = []

        for idx, data in enumerate(pricing_data):
            try:
                normalized = normalize_pricing_data(data)

                text_representation = pricing_to_text(normalized)
                documents.append(text_representation)

                metadata = {
                    "provider": normalized["provider"],
                    "model_name": normalized["model_name"],
                    "input_cost": normalized["input_cost_per_1m_tokens"],
                    "output_cost": normalized["output_cost_per_1m_tokens"],
                    "last_updated": normalized["last_updated"]
                }
                metadatas.append(metadata)

                doc_id = f"{normalized['provider']}_{normalized['model_name']}_{datetime.now().timestamp()}"
                ids.append(doc_id)

            except Exception as e:
                print(f"Error processing entry {idx}: {str(e)}")
                continue

        if not documents:
            print("No valid documents to add.")
            return 0

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully added {len(documents)} pricing entries to ChromaDB.")
            return len(documents)

        except Exception as e:
            print(f"Error adding documents to ChromaDB: {str(e)}")
            return 0

    def query_prices(
        self,
        query_text: str,
        n_results: int = 5,
        filter_provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base using natural language.
        Performs semantic search to find relevant pricing information.

        Args:
            query_text: Natural language query (e.g., "quanto custa o GPT-4?")
            n_results: Number of results to return (default: 5)
            filter_provider: Optional provider filter (e.g., "OpenAI")

        Returns:
            List[Dict]: List of relevant pricing results with metadata

        Example:
            >>> kb = PricingKnowledgeBase()
            >>> results = kb.query_prices("What is the cheapest model?")
            >>> for result in results:
            ...     print(result['metadata']['model_name'], result['metadata']['input_cost'])
        """
        if not query_text or query_text.strip() == "":
            print("Error: Query text cannot be empty.")
            return []

        try:
            where_clause = None
            if filter_provider:
                where_clause = {"provider": filter_provider}

            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_clause
            )

            formatted_results = []
            if results and results['documents'] and len(results['documents']) > 0:
                for idx in range(len(results['documents'][0])):
                    formatted_results.append({
                        "document": results['documents'][0][idx],
                        "metadata": results['metadatas'][0][idx],
                        "distance": results['distances'][0][idx] if 'distances' in results else None
                    })

            return formatted_results

        except Exception as e:
            print(f"Error querying ChromaDB: {str(e)}")
            return []

    def get_all_providers(self) -> List[str]:
        """
        Get a list of all unique providers in the knowledge base.

        Returns:
            List[str]: List of provider names
        """
        try:
            all_data = self.collection.get()
            if all_data and all_data['metadatas']:
                providers = set(meta.get('provider', 'Unknown') for meta in all_data['metadatas'])
                return sorted(list(providers))
            return []
        except Exception as e:
            print(f"Error retrieving providers: {str(e)}")
            return []

    def get_all_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all models in the knowledge base, optionally filtered by provider.

        Args:
            provider: Optional provider filter

        Returns:
            List[Dict]: List of model information
        """
        try:
            where_clause = {"provider": provider} if provider else None
            results = self.collection.get(where=where_clause)

            if results and results['metadatas']:
                return results['metadatas']
            return []
        except Exception as e:
            print(f"Error retrieving models: {str(e)}")
            return []

    def delete_by_provider(self, provider: str) -> bool:
        """
        Delete all entries for a specific provider.

        Args:
            provider: Provider name to delete

        Returns:
            bool: True if successful
        """
        try:
            results = self.collection.get(where={"provider": provider})
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted {len(results['ids'])} entries for provider: {provider}")
                return True
            print(f"No entries found for provider: {provider}")
            return False
        except Exception as e:
            print(f"Error deleting entries: {str(e)}")
            return False

    def clear_all(self) -> bool:
        """
        Clear all data from the knowledge base.
        USE WITH CAUTION!

        Returns:
            bool: True if successful
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"Knowledge base cleared successfully.")
            return True
        except Exception as e:
            print(f"Error clearing knowledge base: {str(e)}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.

        Returns:
            Dict: Statistics including count, providers, etc.
        """
        try:
            count = self.collection.count()
            providers = self.get_all_providers()

            return {
                "total_models": count,
                "providers": providers,
                "provider_count": len(providers),
                "collection_name": self.collection_name,
                "persist_directory": str(self.persist_directory)
            }
        except Exception as e:
            print(f"Error retrieving stats: {str(e)}")
            return {}


if __name__ == "__main__":
    print("=== Testing PricingKnowledgeBase ===\n")

    kb = PricingKnowledgeBase()

    sample_data = [
        {
            "provider": "OpenAI",
            "model_name": "gpt-4",
            "input_cost_per_1m_tokens": 30.0,
            "output_cost_per_1m_tokens": 60.0,
            "context_window": 8192,
            "supports_function_calling": True
        },
        {
            "provider": "OpenAI",
            "model_name": "gpt-3.5-turbo",
            "input_cost_per_1m_tokens": 0.5,
            "output_cost_per_1m_tokens": 1.5,
            "context_window": 16385,
            "supports_function_calling": True
        },
        {
            "provider": "Anthropic",
            "model_name": "claude-3-opus",
            "input_cost_per_1m_tokens": 15.0,
            "output_cost_per_1m_tokens": 75.0,
            "context_window": 200000
        }
    ]

    print("Adding sample data...")
    kb.add_prices(sample_data)

    print("\n=== Testing Queries ===\n")

    print("Query: 'What is the cheapest model?'")
    results = kb.query_prices("What is the cheapest model?", n_results=3)
    for result in results:
        print(f"  - {result['metadata']['model_name']}: ${result['metadata']['input_cost']}/1M tokens")

    print("\n" + "="*50 + "\n")
    print("Stats:", json.dumps(kb.get_stats(), indent=2))
