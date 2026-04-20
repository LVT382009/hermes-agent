"""
Debug NOX V2 Output
"""

from plugins.nox.nox_v2 import compile_nox_v2

# Test simple input
test_input = "fact[A is true]."
result = compile_nox_v2(test_input)

print(f"Input: {test_input}")
print(f"Output: {result.optimized}")
print(f"Success: {result.success}")
print(f"Fallback: {result.fallback_triggered}")
print(f"Time: {result.time_ms:.2f}ms")
print()

# Test rule input
test_input = "rule[A->B]."
result = compile_nox_v2(test_input)

print(f"Input: {test_input}")
print(f"Output: {result.optimized}")
print(f"Success: {result.success}")
print(f"Fallback: {result.fallback_triggered}")
print(f"Time: {result.time_ms:.2f}ms")
print()

# Test complex input
test_input = "fact[A is true]. rule[A->B]."
result = compile_nox_v2(test_input)

print(f"Input: {test_input}")
print(f"Output: {result.optimized}")
print(f"Success: {result.success}")
print(f"Fallback: {result.fallback_triggered}")
print(f"Time: {result.time_ms:.2f}ms")
