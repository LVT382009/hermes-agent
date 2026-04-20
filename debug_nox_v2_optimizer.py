"""
Debug NOX V2 Optimizer
"""

from plugins.nox.nox_v2 import NOXCompilerV2
from plugins.nox.parser import NOXParser
from plugins.nox.ir import create_ir_from_program
from plugins.nox.optimizer import OptimizationConfig

# Create compiler
compiler = NOXCompilerV2()

# Test simple input
test_input = "fact[A is true]."
print(f"Input: {test_input}")

# Parse
parse_result = compiler.parser.parse(test_input, path="fast")
original_ir = create_ir_from_program(parse_result.program, path="fast")
print(f"Original IR nodes: {len(original_ir.nodes)}")

# Optimize
opt_config = OptimizationConfig(
    path="fast",
    max_iterations=20,
    max_nodes=300,
    max_time_ms=15,
    improvement_threshold=0.05,
    determinism_seed=0
)

opt_result = compiler.optimizer.optimize(original_ir, opt_config)
print(f"Optimized IR nodes: {len(opt_result.ir.nodes)}")
print(f"Optimization success: {opt_result.success}")
print(f"Optimization reason: {opt_result.reason}")
print(f"Token savings: {opt_result.token_savings}")
print(f"Compression ratio: {opt_result.compression_ratio}")
print()

# Decode
output = compiler._decode_ir(opt_result.ir)
print(f"Output: {output}")
print(f"Original: {test_input}")
print(f"Same: {output == test_input}")
