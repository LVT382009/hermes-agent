"""
Debug NOX V2 IR
"""

from plugins.nox.nox_v2 import NOXCompilerV2
from plugins.nox.parser import NOXParser
from plugins.nox.ir import create_ir_from_program

# Create compiler
compiler = NOXCompilerV2()

# Test simple input
test_input = "fact[A is true]."
print(f"Input: {test_input}")

# Parse
parse_result = compiler.parser.parse(test_input, path="fast")
print(f"Parse result: {parse_result.program}")

# Create IR
ir = create_ir_from_program(parse_result.program, path="fast")
print(f"IR nodes: {len(ir.nodes)}")
for i, node in enumerate(ir.nodes):
    print(f"  Node {i}: {node.expr}")
    print(f"    Type: {type(node.expr)}")
    if hasattr(node.expr, 'expr'):
        print(f"    Expr: {node.expr.expr}")
        print(f"    Expr Type: {type(node.expr.expr)}")

# Decode
output = compiler._decode_ir(ir)
print(f"Output: {output}")
print()

# Test rule input
test_input = "rule[A->B]."
print(f"Input: {test_input}")

# Parse
parse_result = compiler.parser.parse(test_input, path="fast")
print(f"Parse result: {parse_result.program}")

# Create IR
ir = create_ir_from_program(parse_result.program, path="fast")
print(f"IR nodes: {len(ir.nodes)}")
for i, node in enumerate(ir.nodes):
    print(f"  Node {i}: {node.expr}")
    print(f"    Type: {type(node.expr)}")
    if hasattr(node.expr, 'condition'):
        print(f"    Condition: {node.expr.condition}")
    if hasattr(node.expr, 'consequence'):
        print(f"    Consequence: {node.expr.consequence}")

# Decode
output = compiler._decode_ir(ir)
print(f"Output: {output}")
