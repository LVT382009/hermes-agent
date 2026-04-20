"""
Test NOX Verification Directly
"""

from plugins.nox.parser import NOXParser
from plugins.nox.ir import create_ir_from_program
from plugins.nox.optimizer import NOXOptimizer
from plugins.nox.verifier import verify_ir

# Create components
parser = NOXParser()
optimizer = NOXOptimizer()

# Test responses
test_responses = [
    "fact[X is true].",
    "rule[A->B].",
    "if C then D.",
    "E implies F.",
]

print("Testing NOX Verification...")
print("=" * 80)

for i, response in enumerate(test_responses, 1):
    print(f"\nTest {i}: {response}")
    print("-" * 80)
    
    try:
        # Parse
        parse_result = parser.parse(response, path="fast")
        print(f"✅ Parse successful")
        print(f"Errors: {parse_result.errors}")
        
        # Create IR
        ir = create_ir_from_program(parse_result.program, path="fast")
        print(f"✅ IR created")
        print(f"Nodes: {len(ir.nodes)}")
        
        # Optimize
        opt_result = optimizer.optimize_fast_path(ir)
        print(f"✅ Optimization complete")
        print(f"Success: {opt_result.success}")
        print(f"Fallback: {opt_result.fallback_triggered}")
        print(f"Reason: {opt_result.reason}")
        
        if opt_result.success:
            # Verify
            verification_results = verify_ir(opt_result.ir)
            print(f"✅ Verification complete")
            print(f"Overall passed: {verification_results['overall']['passed']}")
            print(f"Total errors: {verification_results['overall']['total_errors']}")
            
            for layer, results in verification_results.items():
                if layer != 'overall':
                    print(f"\nLayer: {layer}")
                    if hasattr(results, 'checks'):
                        for check in results.checks:
                            print(f"  {check.name}: {check.passed}")
                            if not check.passed:
                                print(f"    Error: {check.details}")
                    else:
                        print(f"  No checks available")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
