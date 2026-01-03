"""
Cost Architect Agent
Analyzes use cases and recommends optimal model choices with cost calculations.
"""
import sys
from pathlib import Path
import os
from typing import List, Dict, Any, Optional, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pricing_knowledge_base import PricingKnowledgeBase

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class CostArchitect:
    """
    The Architect Agent: Analyzes use cases and recommends optimal models.
    Calculates cost savings and provides detailed reasoning.
    """

    def __init__(
        self,
        kb: Optional[PricingKnowledgeBase] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.3
    ):
        """
        Initialize the Cost Architect.

        Args:
            kb: PricingKnowledgeBase instance
            model: LLM model for analysis
            temperature: LLM temperature
        """
        self.kb = kb or PricingKnowledgeBase()
        self.model = model
        self.temperature = temperature

        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.llm_available = LITELLM_AVAILABLE and bool(self.api_key)

    def extract_requirements(
        self,
        use_case_description: str
    ) -> Dict[str, Any]:
        """
        Extract technical requirements from use case description using LLM.

        Args:
            use_case_description: Natural language description of the use case

        Returns:
            Dict: Extracted requirements
        """
        if not self.llm_available:
            return self._extract_requirements_fallback(use_case_description)

        try:
            system_prompt = """You are a technical requirements analyst. Extract key requirements from use case descriptions.

Return a JSON object with these fields (use null for unknown):
{
  "needs_function_calling": true/false/null,
  "needs_vision": true/false/null,
  "needs_large_context": true/false/null,
  "max_latency_tolerance": "low"/"medium"/"high"/null,
  "quality_requirement": "high"/"medium"/"low",
  "budget_priority": "high"/"medium"/"low"
}

Examples:
- "chatbot for customer support" -> quality: medium, latency: low, function_calling: true
- "analyze PDFs with images" -> vision: true, large_context: true
- "simple text classification" -> quality: low, budget_priority: high"""

            user_prompt = f"Use case: {use_case_description}\n\nExtract requirements as JSON:"

            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=300
            )

            content = response.choices[0].message.content

            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                requirements = json.loads(json_str)
            else:
                requirements = json.loads(content)

            return requirements

        except Exception as e:
            print(f"⚠️  Requirements extraction failed: {str(e)}")
            return self._extract_requirements_fallback(use_case_description)

    def _extract_requirements_fallback(
        self,
        use_case_description: str
    ) -> Dict[str, Any]:
        """
        Fallback requirements extraction using keyword matching.

        Args:
            use_case_description: Use case description

        Returns:
            Dict: Basic requirements
        """
        desc_lower = use_case_description.lower()

        requirements = {
            "needs_function_calling": None,
            "needs_vision": None,
            "needs_large_context": None,
            "max_latency_tolerance": "medium",
            "quality_requirement": "medium",
            "budget_priority": "medium"
        }

        if any(word in desc_lower for word in ["image", "vision", "photo", "visual", "pdf"]):
            requirements["needs_vision"] = True

        if any(word in desc_lower for word in ["function", "tool", "api", "action"]):
            requirements["needs_function_calling"] = True

        if any(word in desc_lower for word in ["long", "large", "context", "document", "book"]):
            requirements["needs_large_context"] = True

        if any(word in desc_lower for word in ["fast", "real-time", "instant", "low latency"]):
            requirements["max_latency_tolerance"] = "low"

        if any(word in desc_lower for word in ["cheap", "budget", "cost-effective", "affordable"]):
            requirements["budget_priority"] = "high"
            requirements["quality_requirement"] = "low"

        if any(word in desc_lower for word in ["high quality", "accurate", "best", "premium"]):
            requirements["quality_requirement"] = "high"

        return requirements

    def find_candidates(
        self,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find model candidates from knowledge base based on requirements.

        Args:
            requirements: Extracted requirements

        Returns:
            List[Dict]: Candidate models with metadata
        """
        all_models = self.kb.get_all_models()

        if not all_models:
            return []

        candidates = []

        for model in all_models:
            score = 0
            reasons = []

            meta = model

            if requirements.get("needs_vision") and meta.get("supports_vision"):
                score += 100
                reasons.append("Supports vision")
            elif requirements.get("needs_vision") and not meta.get("supports_vision"):
                continue

            if requirements.get("needs_function_calling") and meta.get("supports_function_calling"):
                score += 50
                reasons.append("Supports function calling")

            if requirements.get("needs_large_context"):
                context = meta.get("context_window", 0)
                if context >= 100000:
                    score += 75
                    reasons.append(f"Large context ({context:,} tokens)")
                elif context < 10000:
                    score -= 25

            budget_priority = requirements.get("budget_priority", "medium")
            input_cost = meta.get("input_cost", 0)

            if budget_priority == "high":
                if input_cost < 1.0:
                    score += 100
                    reasons.append("Very affordable")
                elif input_cost > 20:
                    score -= 50
            elif budget_priority == "low":
                if input_cost > 20:
                    score += 50
                    reasons.append("Premium model")

            quality_req = requirements.get("quality_requirement", "medium")
            if quality_req == "high" and input_cost > 5:
                score += 50
                reasons.append("High-quality model")
            elif quality_req == "low" and input_cost < 1:
                score += 30
                reasons.append("Efficient for simple tasks")

            candidates.append({
                **meta,
                "match_score": score,
                "match_reasons": reasons
            })

        candidates.sort(key=lambda x: x["match_score"], reverse=True)

        return candidates[:5]

    def calculate_cost(
        self,
        model: Dict[str, Any],
        monthly_input_tokens: int,
        monthly_output_tokens: int
    ) -> float:
        """
        Calculate monthly cost for a model.

        Args:
            model: Model metadata with pricing
            monthly_input_tokens: Estimated monthly input tokens
            monthly_output_tokens: Estimated monthly output tokens

        Returns:
            float: Monthly cost in USD
        """
        input_cost_per_1m = model.get("input_cost", 0)
        output_cost_per_1m = model.get("output_cost", 0)

        input_cost = (monthly_input_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (monthly_output_tokens / 1_000_000) * output_cost_per_1m

        return round(input_cost + output_cost, 2)

    def analyze_and_optimize(
        self,
        use_case_description: str,
        monthly_input_tokens: int,
        monthly_output_tokens: Optional[int] = None,
        current_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main method: Analyze use case and recommend optimal model.

        Args:
            use_case_description: Description of the use case
            monthly_input_tokens: Estimated monthly input tokens
            monthly_output_tokens: Estimated monthly output tokens (default: 20% of input)
            current_model: Current model name (optional)

        Returns:
            Dict: Analysis with recommendations and cost savings
        """
        if monthly_output_tokens is None:
            monthly_output_tokens = int(monthly_input_tokens * 0.2)

        print(f"🔍 Analyzing use case: '{use_case_description}'")
        print(f"   Volume: {monthly_input_tokens:,} input / {monthly_output_tokens:,} output tokens/month")

        requirements = self.extract_requirements(use_case_description)
        print(f"✓ Requirements extracted")

        candidates = self.find_candidates(requirements)

        if not candidates:
            return {
                "status": "error",
                "message": "No suitable models found in knowledge base. Run scraper first."
            }

        print(f"✓ Found {len(candidates)} candidate models")

        best_model = candidates[0]
        best_cost = self.calculate_cost(best_model, monthly_input_tokens, monthly_output_tokens)

        current_cost = None
        if current_model:
            current_models = [m for m in self.kb.get_all_models() if m["model_name"].lower() == current_model.lower()]
            if current_models:
                current_cost = self.calculate_cost(current_models[0], monthly_input_tokens, monthly_output_tokens)

        alternatives = []
        for candidate in candidates[:3]:
            cost = self.calculate_cost(candidate, monthly_input_tokens, monthly_output_tokens)
            alternatives.append({
                "provider": candidate["provider"],
                "model_name": candidate["model_name"],
                "monthly_cost": f"${cost:,.2f}",
                "monthly_cost_raw": cost,
                "input_cost_per_1m": f"${candidate['input_cost']:.2f}",
                "output_cost_per_1m": f"${candidate['output_cost']:.2f}",
                "match_score": candidate["match_score"],
                "reasons": candidate.get("match_reasons", []),
                "context_window": candidate.get("context_window"),
                "supports_function_calling": candidate.get("supports_function_calling"),
                "supports_vision": candidate.get("supports_vision")
            })

        result = {
            "status": "success",
            "use_case": use_case_description,
            "requirements": requirements,
            "recommendation": {
                "model": f"{best_model['provider']} {best_model['model_name']}",
                "monthly_cost": f"${best_cost:,.2f}",
                "monthly_cost_raw": best_cost,
                "reasoning": " | ".join(best_model.get("match_reasons", ["Best match"]))
            },
            "alternatives": alternatives,
            "volume": {
                "monthly_input_tokens": monthly_input_tokens,
                "monthly_output_tokens": monthly_output_tokens
            }
        }

        if current_cost:
            savings = current_cost - best_cost
            savings_pct = (savings / current_cost * 100) if current_cost > 0 else 0

            result["current_model"] = {
                "name": current_model,
                "monthly_cost": f"${current_cost:,.2f}",
                "monthly_cost_raw": current_cost
            }

            result["savings"] = {
                "monthly": f"${savings:,.2f}",
                "monthly_raw": savings,
                "annual": f"${savings * 12:,.2f}",
                "annual_raw": savings * 12,
                "percentage": f"{savings_pct:.1f}%"
            }

            if savings > 0:
                result["recommendation"]["action"] = f"Switch to {best_model['model_name']} to save ${savings:,.2f}/month"
            else:
                result["recommendation"]["action"] = f"Current model is already cost-effective"

        return result

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a human-readable report from analysis.

        Args:
            analysis: Analysis results

        Returns:
            str: Formatted report
        """
        if analysis.get("status") != "success":
            return f"Error: {analysis.get('message', 'Unknown error')}"

        lines = []
        lines.append("="*60)
        lines.append("Cost Optimization Report")
        lines.append("="*60)
        lines.append("")
        lines.append(f"Use Case: {analysis['use_case']}")
        lines.append(f"Volume: {analysis['volume']['monthly_input_tokens']:,} input / "
                    f"{analysis['volume']['monthly_output_tokens']:,} output tokens/month")
        lines.append("")

        if "current_model" in analysis:
            lines.append(f"Current Model: {analysis['current_model']['name']}")
            lines.append(f"Current Cost: {analysis['current_model']['monthly_cost']}/month")
            lines.append("")

        rec = analysis["recommendation"]
        lines.append(f"Recommended: {rec['model']}")
        lines.append(f"Estimated Cost: {rec['monthly_cost']}/month")
        lines.append(f"Reasoning: {rec['reasoning']}")
        lines.append("")

        if "savings" in analysis and analysis["savings"]["monthly_raw"] > 0:
            sav = analysis["savings"]
            lines.append(f"💰 SAVINGS:")
            lines.append(f"   Monthly: {sav['monthly']} ({sav['percentage']})")
            lines.append(f"   Annual: {sav['annual']}")
            lines.append("")

        lines.append("Alternative Options:")
        for idx, alt in enumerate(analysis["alternatives"][:3], 1):
            lines.append(f"  {idx}. {alt['provider']} {alt['model_name']}: {alt['monthly_cost']}/month")
            if alt.get("reasons"):
                lines.append(f"     • {', '.join(alt['reasons'])}")

        lines.append("")
        lines.append("="*60)

        return "\n".join(lines)


if __name__ == "__main__":
    print("\n🏗️  Testing Cost Architect...\n")

    kb = PricingKnowledgeBase()

    if kb.collection.count() == 0:
        print("⚠️  Knowledge base is empty. Populating with seed data...")
        from agents.scraper import OpenAIPricingScraper
        scraper = OpenAIPricingScraper(kb)
        scraper.run()
        print()

    architect = CostArchitect(kb)

    test_case = "I need a chatbot for customer support that can call functions"
    monthly_tokens = 10_000_000

    print(f"Test Case: {test_case}")
    print(f"Volume: {monthly_tokens:,} tokens/month\n")

    analysis = architect.analyze_and_optimize(
        use_case_description=test_case,
        monthly_input_tokens=monthly_tokens,
        current_model="gpt-4"
    )

    report = architect.generate_report(analysis)
    print(report)
