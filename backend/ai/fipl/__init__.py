"""Forensic Intelligence Prompt Layer (FIPL)."""
from .autopsy_prompt import forensic_autopsy_prompt
from .cctv_prompt import cctv_log_analysis_prompt
from .correlation_prompt import timeline_correlation_prompt
from .risk_prompt import risk_explanation_prompt
from .tod_prompt import tod_refinement_prompt

__all__ = [
    "forensic_autopsy_prompt",
    "cctv_log_analysis_prompt",
    "timeline_correlation_prompt",
    "risk_explanation_prompt",
    "tod_refinement_prompt",
]
