"""
Debug Test 1 - fact[X is true]
"""

from plugins.nox.parser import NOXParser
from plugins.nox.ir import create_ir_from_program

# Create parser
parser = NOXParser()

# Parse Test 1
response = "fact[X is true]."
parse_result = parser.parse(response, path="fast")

print(f"Parse result: {parse_result}")
print(f"Program: {parse_result.program}")
print(f"Statements: {parse_result.program.statements}")

for stmt in parse_result.program.statements:
    print(f"\nStatement: {stmt}")
    print(f"Type: {type(stmt)}")
    if hasattr(stmt, 'expr'):
        print(f"Expression: {stmt.expr}")
        print(f"Expression type: {type(stmt.expr)}")
        if hasattr(stmt.expr, 'name'):
            print(f"Name: '{stmt.expr.name}'")
            print(f"Is identifier: {stmt.expr.name.isidentifier()}")

# Create IR
ir = create_ir_from_program(parse_result.program, path="fast")

print(f"\nIR nodes: {len(ir.nodes)}")
for node in ir.nodes:
    print(f"Node {node.id}: {node.expr}")
    print(f"  Type: {type(node.expr)}")
    if hasattr(node.expr, 'name'):
        print(f"  Name: '{node.expr.name}'")
        print(f"  Is identifier: {node.expr.name.isidentifier()}")
