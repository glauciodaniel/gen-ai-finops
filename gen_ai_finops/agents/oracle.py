"""
Pricing Oracle Agent
RAG-powered LLM agent that answers pricing questions using ChromaDB context.
"""
import sys
from pathlib import Path
import os
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pricing_knowledge_base import PricingKnowledgeBase

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("⚠️  Warning: litellm not installed. Install with: pip install litellm")


class PricingOracle:
    """
    The Oracle Agent: Answers pricing questions using RAG.
    Retrieves relevant context from ChromaDB and uses LLM to generate responses.
    """

    def __init__(
        self,
        kb: Optional[PricingKnowledgeBase] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.3,
        max_tokens: int = 500
    ):
        """
        Initialize the Pricing Oracle.

        Args:
            kb: PricingKnowledgeBase instance (creates new if not provided)
            model: LLM model to use (default: gpt-3.5-turbo)
            temperature: LLM temperature (default: 0.3 for focused responses)
            max_tokens: Maximum tokens in response
        """
        self.kb = kb or PricingKnowledgeBase()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

        if not LITELLM_AVAILABLE:
            print("⚠️  LiteLLM not available. Install with: pip install litellm")
            self.llm_available = False
        elif not self.api_key:
            print("⚠️  No API key found in environment. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
            self.llm_available = False
        else:
            self.llm_available = True

    def retrieve_context(
        self,
        question: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant pricing context from ChromaDB.

        Args:
            question: User's question
            n_results: Number of results to retrieve

        Returns:
            List[Dict]: Retrieved context with metadata
        """
        print(f"🔍 Searching knowledge base for: '{question}'")

        results = self.kb.query_prices(question, n_results=n_results)

        if not results:
            print("⚠️  No relevant context found in knowledge base.")
            return []

        print(f"✓ Found {len(results)} relevant entries")

        return results

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieved results into a context string for the LLM.

        Args:
            results: Retrieved results from ChromaDB

        Returns:
            str: Formatted context string
        """
        if not results:
            return "No pricing data available."

        context_parts = ["Here is the relevant pricing information:\n"]

        for idx, result in enumerate(results, 1):
            meta = result['metadata']
            doc = result['document']

            context_parts.append(f"{idx}. {doc}")

        return "\n".join(context_parts)

    def build_prompt(self, question: str, context: str) -> List[Dict[str, str]]:
        """
        Build the prompt for the LLM.

        Args:
            question: User's question
            context: Retrieved context

        Returns:
            List[Dict]: Messages for LLM API
        """
        system_prompt = """You are a pricing expert for AI and LLM services. Your role is to:

1. Answer questions about AI model pricing accurately and concisely
2. Compare costs between different models when asked
3. Recommend cost-effective options based on user requirements
4. Explain pricing in clear, non-technical language
5. Always cite specific numbers (cost per 1M tokens) when available

Use ONLY the pricing information provided in the context. Do not make up prices.
If information is not available, say so clearly.

Format monetary values clearly (e.g., "$2.50 per 1M tokens").
"""

        user_prompt = f"""Context:
{context}

Question: {question}

Please answer the question based on the pricing information provided above."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return messages

    def call_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        Call the LLM API using litellm.

        Args:
            messages: Chat messages

        Returns:
            str: LLM response
        """
        if not self.llm_available:
            return self._fallback_response(messages)

        try:
            print(f"🤖 Asking {self.model}...")

            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            answer = response.choices[0].message.content

            return answer

        except Exception as e:
            print(f"⚠️  LLM API error: {str(e)}")
            return self._fallback_response(messages)

    def _fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Fallback response when LLM is not available.
        Extracts context and returns it in a structured way.

        Args:
            messages: Original messages

        Returns:
            str: Fallback response
        """
        user_message = messages[-1]["content"]

        context_start = user_message.find("Context:")
        question_start = user_message.find("Question:")

        if context_start != -1 and question_start != -1:
            context = user_message[context_start+8:question_start].strip()
            question = user_message[question_start+9:].strip()

            return f"""[Fallback Mode - LLM not available]

Based on the knowledge base, here's the relevant pricing information:

{context}

Note: For more intelligent responses, configure an API key (OPENAI_API_KEY) and install litellm.
"""
        else:
            return "[Error: Could not generate response. LLM not available and context parsing failed.]"

    def ask(self, question: str, n_results: int = 5) -> str:
        """
        Main method: Answer a pricing question using RAG.

        Args:
            question: User's question
            n_results: Number of context results to retrieve

        Returns:
            str: Natural language answer
        """
        if not question or question.strip() == "":
            return "Error: Question cannot be empty."

        results = self.retrieve_context(question, n_results=n_results)

        if not results:
            return """I couldn't find any relevant pricing information in the knowledge base.

Try:
1. Running the scraper first: python main.py scrape
2. Adding pricing data manually with the CLI
3. Asking a different question"""

        context = self.format_context(results)

        messages = self.build_prompt(question, context)

        answer = self.call_llm(messages)

        return answer

    def get_status(self) -> Dict[str, Any]:
        """
        Get Oracle status information.

        Returns:
            Dict: Status information
        """
        kb_stats = self.kb.get_stats()

        return {
            "llm_available": self.llm_available,
            "model": self.model,
            "api_key_configured": bool(self.api_key),
            "knowledge_base": kb_stats
        }


def interactive_mode():
    """
    Run the Oracle in interactive question-answering mode.
    """
    print("="*60)
    print("💬 Pricing Oracle - Interactive Mode")
    print("="*60)
    print()

    oracle = PricingOracle()

    status = oracle.get_status()
    print(f"Status: LLM {'✓' if status['llm_available'] else '✗'} | "
          f"KB: {status['knowledge_base']['total_models']} models")
    print()

    if status['knowledge_base']['total_models'] == 0:
        print("⚠️  Knowledge base is empty! Run scraper first:")
        print("   python main.py scrape")
        print()
        return

    print("Ask me anything about AI pricing! (or 'quit' to exit)")
    print()

    while True:
        try:
            question = input("You: ").strip()

            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break

            print()
            answer = oracle.ask(question)
            print(f"Oracle: {answer}")
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    interactive_mode()
