"""
NOX Integration Module for Hermes Agent

This module provides automatic NOX validation, token optimization, and context optimization
for agent responses when NOX is enabled via /nox enable.

The integration hooks into the agent's response pipeline to automatically apply NOX
validation before returning the final response to the user.
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# NOX status file path
NOX_STATUS_FILE = Path.home() / ".hermes" / "nox_status.json"


def is_nox_enabled() -> bool:
    """
    Check if NOX is currently enabled.
    
    Returns:
        bool: True if NOX is enabled, False otherwise.
    """
    try:
        if NOX_STATUS_FILE.exists():
            with open(NOX_STATUS_FILE, 'r') as f:
                status = json.load(f)
                return status.get("enabled", False)
    except Exception as e:
        logger.warning(f"Failed to read NOX status: {e}")
    return False


def get_nox_config() -> Dict[str, Any]:
    """
    Get NOX configuration from status file.
    
    Returns:
        Dict containing NOX configuration (mode, validation_level, etc.)
    """
    try:
        if NOX_STATUS_FILE.exists():
            with open(NOX_STATUS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read NOX config: {e}")
    return {"enabled": False, "mode": "standard", "validation_level": "strict"}


def apply_nox_validation(
    response: str,
    messages: list,
    config: Optional[Dict[str, Any]] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Apply NOX validation, token optimization, and context optimization to a response.
    
    This function:
    1. Validates the response for logical consistency and hallucinations
    2. Optimizes token usage by removing redundancy
    3. Optimizes context by ensuring proper structure
    
    Args:
        response: The agent's response to validate/optimize
        messages: The conversation history
        config: NOX configuration (optional, will read from file if not provided)
    
    Returns:
        Tuple of (optimized_response, metadata) where metadata contains:
        - validation_passed: bool
        - token_reduction: float (percentage)
        - context_optimized: bool
        - original_length: int
        - optimized_length: int
    """
    if config is None:
        config = get_nox_config()
    
    if not config.get("enabled", False):
        return response, {
            "validation_passed": True,
            "token_reduction": 0.0,
            "context_optimized": False,
            "original_length": len(response),
            "optimized_length": len(response),
            "nox_applied": False
        }
    
    metadata = {
        "validation_passed": True,
        "token_reduction": 0.0,
        "context_optimized": False,
        "original_length": len(response),
        "optimized_length": len(response),
        "nox_applied": True,
        "mode": config.get("mode", "standard"),
        "validation_level": config.get("validation_level", "strict")
    }
    
    try:
        # Import NOX validation logic from the skill
        from skills.nox.validate import validate_text, NOXConfig
        
        # Step 1: Validate response
        nox_config = NOXConfig()
        validation_result = validate_text(response, nox_config)
        
        metadata["validation_passed"] = validation_result.decision == "pass"
        metadata["overall_score"] = validation_result.overall_score
        metadata["total_time_ms"] = validation_result.total_time_ms
        metadata["validation_issues"] = [
            {"layer": layer, "issues": result.issues if result else []}
            for layer, result in validation_result.layer_results.items()
            if result and result.issues
        ]
        
        # Step 2: Optimize tokens (basic implementation)
        optimized_response = response
        if config.get("optimize_tokens", True):
            # Remove redundant whitespace and common patterns
            optimized_response = re.sub(r'\n\s*\n\s*\n+', '\n\n', optimized_response)  # Remove excessive blank lines
            optimized_response = re.sub(r' +', ' ', optimized_response)  # Remove multiple spaces
            optimized_response = optimized_response.strip()
            
            # Calculate token reduction (rough estimate based on character count)
            original_len = len(response)
            optimized_len = len(optimized_response)
            if original_len > 0:
                metadata["token_reduction"] = ((original_len - optimized_len) / original_len) * 100
            metadata["optimized_length"] = optimized_len
        
        # Step 3: Optimize context (basic implementation)
        if config.get("optimize_context", True):
            # Ensure proper structure (basic checks)
            if not optimized_response.endswith(('.', '!', '?', '}', ']', ')')):
                # Add proper ending if missing
                optimized_response = optimized_response.rstrip() + '.'
                metadata["context_optimized"] = True
            metadata["optimized_length"] = len(optimized_response)
        
        # Update final length
        metadata["optimized_length"] = len(optimized_response)
        
        logger.info(f"NOX applied: {metadata['token_reduction']:.1f}% token reduction, "
                   f"validation_passed={metadata['validation_passed']}, "
                   f"context_optimized={metadata['context_optimized']}, "
                   f"score={metadata['overall_score']:.2f}")
        
        return optimized_response, metadata
        
    except ImportError as e:
        logger.warning(f"NOX validation modules not available: {e}")
        return response, {**metadata, "nox_applied": False, "error": str(e)}
    except Exception as e:
        logger.error(f"NOX validation failed: {e}")
        return response, {**metadata, "nox_applied": False, "error": str(e)}


def should_apply_nox() -> bool:
    """
    Check if NOX should be applied to the current response.
    
    This is a convenience function that combines the enabled check with
    any additional conditions (e.g., response length, message count, etc.)
    
    Returns:
        bool: True if NOX should be applied, False otherwise.
    """
    if not is_nox_enabled():
        return False
    
    config = get_nox_config()
    
    # Additional conditions can be added here
    # For example, only apply to responses longer than a certain length
    min_length = config.get("min_response_length", 0)
    # We can't check response length here, but the caller can
    
    return True


def get_nox_metadata() -> Dict[str, Any]:
    """
    Get NOX metadata for logging and debugging.
    
    Returns:
        Dict containing NOX status and configuration.
    """
    config = get_nox_config()
    return {
        "enabled": config.get("enabled", False),
        "mode": config.get("mode", "standard"),
        "validation_level": config.get("validation_level", "strict"),
        "optimize_tokens": config.get("optimize_tokens", True),
        "optimize_context": config.get("optimize_context", True),
        "status_file": str(NOX_STATUS_FILE)
    }
