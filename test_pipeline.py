"""
Test NOX Full Pipeline
"""

from plugins.nox import NOXPlugin

# Create plugin
plugin = NOXPlugin()

# Enable plugin
plugin.enable()

# Test responses
test_responses = [
    "fact[X is true].",
    "rule[A->B].",
    "if C then D.",
    "E implies F.",
]

print("Testing NOX Full Pipeline...")
print("=" * 80)

for i, response in enumerate(test_responses, 1):
    print(f"\nTest {i}: {response}")
    print("-" * 80)
    
    try:
        optimized_response, metadata = plugin.apply_nox_validation(
            response, [], {}
        )
        
        print(f"Original: {response}")
        print(f"Optimized: {optimized_response}")
        print(f"NOX Applied: {metadata.get('nox_applied')}")
        print(f"Fallback: {metadata.get('fallback_triggered')}")
        print(f"Reason: {metadata.get('reason', 'N/A')}")
        print(f"Path: {metadata.get('path')}")
        print(f"Time: {metadata.get('validation_time_ms', 0):.2f}ms")
        
        if metadata.get("nox_applied"):
            print(f"Compression: {metadata.get('token_reduction', 0):.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Disable plugin
plugin.disable()
