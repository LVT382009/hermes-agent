"""
Comprehensive NOX V2 Test Suite

Tests all V2 features:
- Intelligence enhancement
- Information preservation
- Chain-of-thought integrity
- Semantic verification
- Reversibility checks
- Completeness verification
- Performance metrics
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, List
from statistics import mean, median

# Import NOX V2
from plugins.nox.nox_v2 import (
    NOXCompilerV2,
    compile_nox_v2,
    ReasoningTemplate,
    ReasoningQuality,
    SemanticEquivalenceResult,
    ReversibilityResult,
    CompletenessResult,
    NOXV2Result
)

# Test cases
test_cases = [
    {
        "name": "Simple Fact",
        "input": "fact[X is true].",
        "expected_preservation": True,
        "expected_compression": 0.3,  # 30% compression target
    },
    {
        "name": "Rule with Implication",
        "input": "rule[A->B].",
        "expected_preservation": True,
        "expected_compression": 0.3,
    },
    {
        "name": "Conditional Statement",
        "input": "if C then D.",
        "expected_preservation": True,
        "expected_compression": 0.3,
    },
    {
        "name": "Implication Statement",
        "input": "E implies F.",
        "expected_preservation": True,
        "expected_compression": 0.3,
    },
    {
        "name": "Complex Chain",
        "input": "fact[A is true]. rule[A->B]. rule[B->C].",
        "expected_preservation": True,
        "expected_compression": 0.3,
    },
    {
        "name": "Long Chain",
        "input": "fact[X is true]. rule[X->Y]. rule[Y->Z]. rule[Z->W]. rule[W->V].",
        "expected_preservation": True,
        "expected_compression": 0.3,
    },
]

def test_v2_compilation():
    """Test NOX V2 compilation."""
    print("\n" + "="*80)
    print("NOX V2 COMPILATION TEST")
    print("="*80)
    
    compiler = NOXCompilerV2()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Input: {test_case['input']}")
        
        try:
            result = compiler.compile(test_case['input'])
            
            print(f"✅ Compilation successful")
            print(f"   Output: {result.optimized}")
            print(f"   Time: {result.time_ms:.2f}ms")
            print(f"   Success: {result.success}")
            print(f"   Fallback: {result.fallback_triggered}")
            
            # V2-specific results
            print(f"   Semantic Confidence: {result.semantic_equivalence.confidence:.2f}")
            print(f"   Reversibility Quality: {result.reversibility.reconstruction_quality:.2f}")
            print(f"   Completeness Score: {result.completeness.completeness_score:.2f}")
            print(f"   Lost Elements: {result.semantic_equivalence.lost_elements}")
            print(f"   Missing Elements: {result.reversibility.missing_elements}")
            
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            import traceback
            traceback.print_exc()

def test_v2_intelligence_enhancement():
    """Test NOX V2 intelligence enhancement features."""
    print("\n" + "="*80)
    print("NOX V2 INTELLIGENCE ENHANCEMENT TEST")
    print("="*80)
    
    compiler = NOXCompilerV2()
    
    # Test reasoning templates
    print("\nTesting Reasoning Templates:")
    for template in ReasoningTemplate:
        print(f"  - {template.value}")
    
    # Test quality metrics
    print("\nTesting Quality Metrics:")
    test_input = "fact[A is true]. rule[A->B]."
    result = compiler.compile(test_input)
    
    quality = result.quality_metrics
    print(f"  Logical Consistency: {quality.logical_consistency:.2f}")
    print(f"  Evidence Quality: {quality.evidence_quality:.2f}")
    print(f"  Clarity: {quality.clarity:.2f}")
    print(f"  Reasoning Depth: {quality.reasoning_depth:.2f}")
    print(f"  Overall Score: {quality.quality_score:.2f}")

def test_v2_information_preservation():
    """Test NOX V2 information preservation."""
    print("\n" + "="*80)
    print("NOX V2 INFORMATION PRESERVATION TEST")
    print("="*80)
    
    compiler = NOXCompilerV2()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        
        result = compiler.compile(test_case['input'])
        
        semantic = result.semantic_equivalence
        reversibility = result.reversibility
        completeness = result.completeness
        
        print(f"  Semantic Confidence: {semantic.confidence:.2f}")
        print(f"  Equivalent: {semantic.equivalent}")
        print(f"  Preserved Elements: {len(semantic.preserved_elements)}")
        print(f"  Lost Elements: {len(semantic.lost_elements)}")
        
        print(f"  Reversibility Quality: {reversibility.reconstruction_quality:.2f}")
        print(f"  Can Reconstruct: {reversibility.reversible}")
        print(f"  Reconstruction Accuracy: {reversibility.reconstruction_quality:.2f}")
        
        print(f"  Completeness Score: {completeness.completeness_score:.2f}")
        print(f"  Complete: {completeness.complete}")
        print(f"  Missing Elements: {completeness.missing_elements}")
        print(f"  Preserved Elements: {len(completeness.preserved_elements)}")

def test_v2_chain_of_thought():
    """Test NOX V2 chain-of-thought preservation."""
    print("\n" + "="*80)
    print("NOX V2 CHAIN-OF-THOUGHT PRESERVATION TEST")
    print("="*80)
    
    compiler = NOXCompilerV2()
    
    # Test chain preservation
    chain_tests = [
        "fact[A is true]. rule[A->B].",
        "fact[A is true]. rule[A->B]. rule[B->C].",
        "fact[A is true]. rule[A->B]. rule[B->C]. rule[C->D].",
    ]
    
    for i, chain in enumerate(chain_tests, 1):
        print(f"\nChain Test {i}:")
        print(f"Input: {chain}")
        
        result = compiler.compile(chain)
        
        print(f"Output: {result.optimized}")
        
        completeness = result.completeness
        print(f"  Missing Elements: {completeness.missing_elements}")
        
        if not completeness.missing_elements:
            print(f"  ✅ Chain-of-thought preserved")
        else:
            print(f"  ❌ Chain-of-thought broken")

def test_v2_performance():
    """Test NOX V2 performance metrics."""
    print("\n" + "="*80)
    print("NOX V2 PERFORMANCE TEST")
    print("="*80)
    
    compiler = NOXCompilerV2()
    
    times = []
    successes = 0
    fallbacks = 0
    
    for test_case in test_cases:
        start = time.time()
        result = compiler.compile(test_case['input'])
        end = time.time()
        
        elapsed_ms = (end - start) * 1000
        times.append(elapsed_ms)
        
        if result.success:
            successes += 1
        if result.fallback_triggered:
            fallbacks += 1
    
    avg_time = mean(times)
    median_time = median(times)
    min_time = min(times)
    max_time = max(times)
    success_rate = (successes / len(test_cases)) * 100
    fallback_rate = (fallbacks / len(test_cases)) * 100
    
    print(f"\nPerformance Metrics:")
    print(f"  Average Time: {avg_time:.2f}ms (target: <75ms)")
    print(f"  Median Time: {median_time:.2f}ms")
    print(f"  Min Time: {min_time:.2f}ms")
    print(f"  Max Time: {max_time:.2f}ms (hard ceiling: <100ms)")
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"  Fallback Rate: {fallback_rate:.1f}%")
    
    # Check targets
    print(f"\nTarget Checks:")
    print(f"  Average Time < 75ms: {'✅' if avg_time < 75 else '❌'}")
    print(f"  Max Time < 100ms: {'✅' if max_time < 100 else '❌'}")
    print(f"  Success Rate >= 80%: {'✅' if success_rate >= 80 else '❌'}")
    print(f"  Fallback Rate <= 20%: {'✅' if fallback_rate <= 20 else '❌'}")

def test_v2_quality_metrics():
    """Test NOX V2 quality metrics."""
    print("\n" + "="*80)
    print("NOX V2 QUALITY METRICS TEST")
    print("="*80)
    
    compiler = NOXCompilerV2()
    
    semantic_confidences = []
    reversibility_qualities = []
    completeness_scores = []
    lost_elements = []
    missing_elements = []
    
    for test_case in test_cases:
        result = compiler.compile(test_case['input'])
        
        semantic_confidences.append(result.semantic_equivalence.confidence)
        reversibility_qualities.append(result.reversibility.reconstruction_quality)
        completeness_scores.append(result.completeness.completeness_score)
        lost_elements.append(len(result.semantic_equivalence.lost_elements))
        missing_elements.append(len(result.completeness.missing_elements))
    
    if semantic_confidences:
        avg_semantic = mean(semantic_confidences)
        print(f"\nSemantic Confidence:")
        print(f"  Average: {avg_semantic:.2f} (target: >=0.80)")
        print(f"  Target Met: {'✅' if avg_semantic >= 0.80 else '❌'}")
    
    if reversibility_qualities:
        avg_reversibility = mean(reversibility_qualities)
        print(f"\nReversibility Quality:")
        print(f"  Average: {avg_reversibility:.2f} (target: >=0.80)")
        print(f"  Target Met: {'✅' if avg_reversibility >= 0.80 else '❌'}")
    
    if completeness_scores:
        avg_completeness = mean(completeness_scores)
        total_lost = sum(lost_elements)
        total_missing = sum(missing_elements)
        
        print(f"\nCompleteness Score:")
        print(f"  Average: {avg_completeness:.2f} (target: >=0.95)")
        print(f"  Target Met: {'✅' if avg_completeness >= 0.95 else '❌'}")
        print(f"\nInformation Loss:")
        print(f"  Total Lost Elements: {total_lost} (target: 0)")
        print(f"  Total Missing Elements: {total_missing} (target: 0)")
        print(f"  No Loss: {'✅' if total_lost == 0 and total_missing == 0 else '❌'}")

def test_v2_edge_cases():
    """Test NOX V2 edge cases."""
    print("\n" + "="*80)
    print("NOX V2 EDGE CASES TEST")
    print("="*80)
    
    compiler = NOXCompilerV2()
    
    edge_cases = [
        {
            "name": "Empty Input",
            "input": "",
        },
        {
            "name": "Very Long Chain",
            "input": "fact[A is true]. " + " ".join([f"rule[X{i}->X{i+1}]." for i in range(10)]),
        },
        {
            "name": "Complex Nested",
            "input": "fact[A is true]. rule[A->B]. rule[B->C]. rule[C->D]. rule[D->E]. rule[E->F].",
        },
    ]
    
    for i, edge_case in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}: {edge_case['name']}")
        print(f"Input: {edge_case['input'][:100]}...")
        
        try:
            result = compiler.compile(edge_case['input'])
            
            print(f"✅ Handled successfully")
            print(f"   Success: {result.success}")
            print(f"   Fallback: {result.fallback_triggered}")
            print(f"   Time: {result.time_ms:.2f}ms")
            
        except Exception as e:
            print(f"❌ Failed: {e}")

def main():
    """Run all NOX V2 tests."""
    print("\n" + "="*80)
    print("NOX V2 COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Run all tests
    test_v2_compilation()
    test_v2_intelligence_enhancement()
    test_v2_information_preservation()
    test_v2_chain_of_thought()
    test_v2_performance()
    test_v2_quality_metrics()
    test_v2_edge_cases()
    
    print("\n" + "="*80)
    print("NOX V2 TEST SUITE COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
