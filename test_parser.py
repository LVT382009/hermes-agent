"""
Test NOX Parser Directly
"""

from plugins.nox.parser import NOXParser

# Create parser
parser = NOXParser()

# Test responses
test_responses = [
    "fact[X is true].",
    "rule[A->B].",
    "if C then D.",
    "E implies F.",
]

print("Testing NOX Parser...")
print("=" * 80)

for i, response in enumerate(test_responses, 1):
    print(f"\nTest {i}: {response}")
    print("-" * 80)
    
    try:
        result = parser.parse(response, path="fast")
        print(f"✅ Parse successful!")
        print(f"Program: {result.program}")
        print(f"Errors: {result.errors}")
        print(f"Warnings: {result.warnings}")
    except Exception as e:
        print(f"❌ Parse failed: {e}")
