# apps/code-analyst-agent/app/models.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------
# 📍 Shared Base
# ---------------------------------------------------------
class CodeLocation(BaseModel):
    file_path: str = Field(..., description="Path to the source file inside the repo")
    start: int = Field(..., description="Start line number of the code block")
    end: int = Field(..., description="End line number of the code block")


# ---------------------------------------------------------
# 📌 Extracted Snippet
# ---------------------------------------------------------
class CodeSnippetResponse(BaseModel):
    file_path: str
    snippet: str
    start: int
    end: int
    context: int = 3


# ---------------------------------------------------------
# 🧠 Static Function Analysis Model
# ---------------------------------------------------------
class FunctionAnalysis(BaseModel):
    file_path: str
    code: str
    structure: Dict[str, Any] = Field(
        ..., description="AST structural features (branches, loops, calls, returns count, etc.)"
    )
    # Example keys:
    # {
    #   "has_loops": true,
    #   "has_conditionals": false,
    #   "returns_count": 2,
    #   "calls": ["load_config", "validate"]
    # }


# ---------------------------------------------------------
# 🏛 Class / Component Design Pattern Detection
# ---------------------------------------------------------
class ClassPatternAnalysis(BaseModel):
    file_path: str
    code: str
    patterns_detected: List[str] = Field(
        ..., description="Detected design patterns, or ['none_detected']"
    )


# ---------------------------------------------------------
# 💬 LLM Explanation Response
# ---------------------------------------------------------
class ImplementationExplanation(BaseModel):
    file_path: str
    explanation: Optional[str] = None
    code: str
    error: Optional[str] = None
    details: Optional[str] = None
    fallback_prompt: Optional[str] = None


# ---------------------------------------------------------
# ⚖️ Comparison between two implementations (LLM-backed)
# ---------------------------------------------------------
class ImplementationComparison(BaseModel):
    implementation_a: str
    implementation_b: str
    comparison: Optional[str] = None
    error: Optional[str] = None
    fallback_prompt: Optional[str] = None


# ---------------------------------------------------------
# ❗ Error Model (Graceful Failures)
# ---------------------------------------------------------
class LLMErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    fallback_prompt: Optional[str] = None
