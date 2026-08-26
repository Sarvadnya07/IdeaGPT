import json
import re
from typing import Optional, Tuple
from app.ai.schemas.response import AIResponseModel

class OutputValidator:
    @staticmethod
    def clean_json_string(text: str) -> str:
        """
        Cleans LLM response formatting (e.g. ```json markdown blocks) to extract raw JSON.
        """
        # Match standard json code blocks
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # Fallback to finding first brace and last brace
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx:end_idx + 1].strip()
            
        return text.strip()

    @classmethod
    def validate_and_repair(cls, raw_text) -> Tuple[Optional[AIResponseModel], Optional[str]]:
        """
        Attempts to parse and validate raw model response text or dict.
        Returns a tuple of (parsed_model, error_message).
        """
        if isinstance(raw_text, dict):
            parsed_json = raw_text
        else:
            cleaned = cls.clean_json_string(raw_text)
            try:
                parsed_json = json.loads(cleaned)
            except json.JSONDecodeError as je:
                return None, f"JSON parsing failed: {str(je)}"

        # Validate required top-level items and patch if necessary
        try:
            if "summary" not in parsed_json:
                parsed_json["summary"] = parsed_json.get("market_analysis", "Summary of evaluation.")

            # Enforce fallbacks for missing list keys
            for list_key in ["strengths", "weaknesses", "recommendations"]:
                if list_key not in parsed_json or not isinstance(parsed_json[list_key], list):
                    parsed_json[list_key] = []
                    
            # Normalize confidence (handles string 'medium', 'high', 'low' from various LLMs)
            if "confidence" in parsed_json:
                if isinstance(parsed_json["confidence"], str):
                    c_str = parsed_json["confidence"].lower()
                    if "high" in c_str:
                        parsed_json["confidence"] = 0.9
                    elif "low" in c_str:
                        parsed_json["confidence"] = 0.5
                    elif "med" in c_str:
                        parsed_json["confidence"] = 0.75
                    else:
                        try:
                            parsed_json["confidence"] = float(parsed_json["confidence"])
                        except (ValueError, TypeError):
                            parsed_json["confidence"] = 0.8
            else:
                parsed_json["confidence"] = 0.8
                
            # Normalize score
            if "score" in parsed_json:
                try:
                    parsed_json["score"] = int(float(parsed_json["score"]))
                except (ValueError, TypeError):
                    parsed_json["score"] = 70
            else:
                parsed_json["score"] = 70

            # Verify and construct dimensions sub-object
            if "dimensions" not in parsed_json or not isinstance(parsed_json["dimensions"], dict):
                parsed_json["dimensions"] = {
                    "innovation": 70,
                    "market_potential": 70,
                    "technical_feasibility": 70,
                    "business_viability": 70,
                    "scalability": 70,
                    "execution_complexity": 70,
                    "competitive_differentiation": 70
                }
            else:
                dims = parsed_json["dimensions"]
                required_dims = [
                    "innovation", "market_potential", "technical_feasibility", 
                    "business_viability", "scalability", "execution_complexity", "competitive_differentiation"
                ]
                for d in required_dims:
                    if d not in dims:
                        dims[d] = 70
                    else:
                        # Force integer bounds
                        try:
                            val = int(dims[d])
                            dims[d] = max(0, min(100, val))
                        except:
                            dims[d] = 70
                            
            # Construct Pydantic model
            validated = AIResponseModel(**parsed_json)
            return validated, None
            
        except Exception as ve:
            return None, f"Schema validation failed: {str(ve)}"
