"""
Test NOX V2 Directly
"""

from plugins.nox.nox_v2 import compile_nox_v2

# Test responses
test_responses = [
    "fact[X is true].",
    "rule[A->B].",
    "if C then D.",
    "E implies F.",
]

for i, response in enumerate(test_responses, 1):
    print(f"\nTest {i}: {response}")
    
    result = compile_nox_v2(response, path="fast")
    
    print(f"  Success: {result.success}")
    print(f"  Fallback: {result.fallback_triggered}")
    print(f"  Fallback Reason: {result.fallback_reason}")
    print(f"  Original: {result.original}")
    print(f"  Optimized: {result.optimized}")
    print(f"  Token Savings: {result.token_savings}")
    print(f"  Compression: {result.compression_ratio}")
    print(f"  Semantic Confidence: {result.semantic_equivalence.confidence}")
    print(f"  Reversibility Quality: {result.reversibility.reconstruction_quality}")
    print(f"  Completeness Score: {result.completeness.completeness_score}")
    print(f"  Lost Elements: {result.semantic_equivalence.lost_elements}")
    print(f"  Missing Elements: {result.completeness.missing_elements}")
