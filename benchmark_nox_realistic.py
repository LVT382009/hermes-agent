"""
NOX Plugin Benchmark - Realistic Test Cases

Compares performance with and without NOX enabled using realistic responses.
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, List
from statistics import mean, median, stdev

from plugins.nox import NOXPlugin


class NOXBenchmark:
    """Benchmark NOX plugin performance."""
    
    def __init__(self):
        self.plugin = NOXPlugin()
        self.status_file = Path.home() / ".hermes" / "nox_status.json"
        self.plugin.status_file = self.status_file
    
    def generate_realistic_test_responses(self) -> List[str]:
        """Generate realistic test responses that NOX can parse."""
        responses = []
        
        # Short responses with reasoning patterns (fast path)
        responses.extend([
            "If X is true, then Y follows. Therefore, we can conclude Y.",
            "The data shows that A implies B. Consequently, C is true.",
            "Based on the evidence, we can infer that D is correct.",
            "The analysis indicates that E leads to F. Thus, F is the result.",
            "Given the premises, G implies H. So H must be true.",
            "The facts suggest that I causes J. Therefore, J is valid.",
            "From the information, K leads to L. As a result, L is confirmed.",
            "The reasoning shows that M results in N. Hence, N is true.",
            "The logic demonstrates that O produces P. Thus, P follows.",
            "The evidence indicates that Q implies R. So R is established.",
        ])
        
        # Medium responses with more complex reasoning (fast path)
        responses.extend([
            "The analysis of the data reveals several important patterns. First, we observe that A implies B. Second, the evidence suggests that B leads to C. Therefore, we can conclude that C is true. This conclusion is supported by multiple sources.",
            "Based on the available information, we can make several inferences. The data shows that X is related to Y. Furthermore, Y is connected to Z. Consequently, we can determine that Z is the correct answer. This reasoning is consistent with the established facts.",
            "The investigation into the matter has yielded significant results. We found that P causes Q. Additionally, Q leads to R. As a result, R is the expected outcome. This finding aligns with our initial hypothesis.",
            "The examination of the evidence provides clear insights. We determined that S implies T. Moreover, T is connected to U. Thus, we can conclude that U is valid. This conclusion is well-supported by the data.",
            "The review of the information reveals important relationships. We established that V results in W. Furthermore, W is associated with X. Therefore, X is the logical conclusion. This reasoning is sound and consistent.",
        ])
        
        # Long responses with complex reasoning chains (deep path)
        responses.extend([
            "The comprehensive analysis of the available data has produced several key findings. First, we observe that there is a clear relationship between A and B. The evidence strongly suggests that A implies B. Second, we can see that B is connected to C through multiple intermediate steps. The data indicates that B leads to C via several pathways. Third, we find that C is associated with D. The analysis shows that C results in D. Fourth, we determine that D is linked to E. The evidence demonstrates that D produces E. Finally, we can conclude that E is the correct answer. This conclusion is supported by the entire chain of reasoning from A through E. Each step in the chain is well-documented and verified.",
            "The detailed investigation into the matter has revealed significant patterns. We began by examining the relationship between P and Q. The data clearly shows that P causes Q. Next, we analyzed the connection between Q and R. Our investigation found that Q leads to R through a well-defined mechanism. We then studied the link between R and S. The evidence indicates that R results in S. Following this, we examined the relationship between S and T. Our analysis demonstrated that S implies T. Finally, we considered the connection between T and U. The data suggests that T is associated with U. Based on this comprehensive analysis, we can conclude that U is the expected outcome. This conclusion is supported by the entire chain of reasoning.",
            "The systematic review of all available information has produced important insights. We first established that V is related to W. The evidence shows that V implies W. We then determined that W is connected to X. The data indicates that W leads to X. Next, we found that X is associated with Y. The analysis demonstrates that X results in Y. We also discovered that Y is linked to Z. The evidence suggests that Y produces Z. Finally, we concluded that Z is the logical result. This conclusion is based on the complete chain of reasoning from V through Z. Each step in this chain is well-supported by the available data.",
        ])
        
        return responses
    
    def benchmark_without_nox(self, responses: List[str]) -> Dict[str, Any]:
        """Benchmark without NOX (baseline)."""
        times = []
        
        for response in responses:
            messages = []
            config = {}
            
            start = time.time()
            result = response  # No processing
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        
        return {
            "total_responses": len(responses),
            "avg_time_ms": mean(times),
            "median_time_ms": median(times),
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "std_dev_ms": stdev(times) if len(times) > 1 else 0,
            "total_time_ms": sum(times),
            "times": times
        }
    
    def benchmark_with_nox(self, responses: List[str]) -> Dict[str, Any]:
        """Benchmark with NOX enabled."""
        # Enable NOX
        self.plugin.enable()
        
        times = []
        token_savings = []
        fallback_count = 0
        nox_applied_count = 0
        
        for response in responses:
            messages = []
            config = {}
            
            start = time.time()
            optimized_response, metadata = self.plugin.apply_nox_validation(
                response, messages, config
            )
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            if metadata.get("nox_applied"):
                nox_applied_count += 1
                original_length = metadata.get("original_length", len(response))
                optimized_length = metadata.get("optimized_length", len(optimized_response))
                savings = original_length - optimized_length
                token_savings.append(savings)
            
            if metadata.get("fallback_triggered"):
                fallback_count += 1
        
        # Disable NOX
        self.plugin.disable()
        
        return {
            "total_responses": len(responses),
            "avg_time_ms": mean(times),
            "median_time_ms": median(times),
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "std_dev_ms": stdev(times) if len(times) > 1 else 0,
            "total_time_ms": sum(times),
            "times": times,
            "nox_applied_count": nox_applied_count,
            "fallback_count": fallback_count,
            "avg_token_savings": mean(token_savings) if token_savings else 0,
            "total_token_savings": sum(token_savings),
            "avg_compression_ratio": mean([s / len(r) for s, r in zip(token_savings, responses)]) if token_savings else 0
        }
    
    def compare_benchmarks(self, without_nox: Dict[str, Any], with_nox: Dict[str, Any]) -> Dict[str, Any]:
        """Compare benchmarks and calculate differences."""
        return {
            "avg_time_increase_ms": with_nox["avg_time_ms"] - without_nox["avg_time_ms"],
            "avg_time_increase_percent": ((with_nox["avg_time_ms"] - without_nox["avg_time_ms"]) / without_nox["avg_time_ms"]) * 100 if without_nox["avg_time_ms"] > 0 else 0,
            "total_time_increase_ms": with_nox["total_time_ms"] - without_nox["total_time_ms"],
            "nox_applied_rate": (with_nox["nox_applied_count"] / with_nox["total_responses"]) * 100,
            "fallback_rate": (with_nox["fallback_count"] / with_nox["total_responses"]) * 100,
            "avg_compression_percent": with_nox["avg_compression_ratio"] * 100,
            "total_token_savings": with_nox["total_token_savings"]
        }
    
    def print_benchmark_results(self, without_nox: Dict[str, Any], with_nox: Dict[str, Any], comparison: Dict[str, Any]):
        """Print formatted benchmark results."""
        print("\n" + "=" * 80)
        print("NOX Plugin Benchmark Results")
        print("=" * 80)
        
        print("\n📊 WITHOUT NOX (Baseline)")
        print("-" * 80)
        print(f"Total Responses: {without_nox['total_responses']}")
        print(f"Average Time: {without_nox['avg_time_ms']:.2f}ms")
        print(f"Median Time: {without_nox['median_time_ms']:.2f}ms")
        print(f"Min Time: {without_nox['min_time_ms']:.2f}ms")
        print(f"Max Time: {without_nox['max_time_ms']:.2f}ms")
        print(f"Std Dev: {without_nox['std_dev_ms']:.2f}ms")
        print(f"Total Time: {without_nox['total_time_ms']:.2f}ms")
        
        print("\n📊 WITH NOX (Optimized)")
        print("-" * 80)
        print(f"Total Responses: {with_nox['total_responses']}")
        print(f"Average Time: {with_nox['avg_time_ms']:.2f}ms")
        print(f"Median Time: {with_nox['median_time_ms']:.2f}ms")
        print(f"Min Time: {with_nox['min_time_ms']:.2f}ms")
        print(f"Max Time: {with_nox['max_time_ms']:.2f}ms")
        print(f"Std Dev: {with_nox['std_dev_ms']:.2f}ms")
        print(f"Total Time: {with_nox['total_time_ms']:.2f}ms")
        print(f"NOX Applied: {with_nox['nox_applied_count']} ({comparison['nox_applied_rate']:.1f}%)")
        print(f"Fallbacks: {with_nox['fallback_count']} ({comparison['fallback_rate']:.1f}%)")
        print(f"Avg Token Savings: {with_nox['avg_token_savings']:.1f} tokens")
        print(f"Total Token Savings: {with_nox['total_token_savings']} tokens")
        print(f"Avg Compression: {comparison['avg_compression_percent']:.1f}%")
        
        print("\n📊 COMPARISON")
        print("-" * 80)
        print(f"Avg Time Increase: {comparison['avg_time_increase_ms']:.2f}ms ({comparison['avg_time_increase_percent']:.1f}%)")
        print(f"Total Time Increase: {comparison['total_time_increase_ms']:.2f}ms")
        print(f"NOX Applied Rate: {comparison['nox_applied_rate']:.1f}%")
        print(f"Fallback Rate: {comparison['fallback_rate']:.1f}%")
        print(f"Average Compression: {comparison['avg_compression_percent']:.1f}%")
        print(f"Total Token Savings: {comparison['total_token_savings']} tokens")
        
        print("\n🎯 PERFORMANCE TARGETS")
        print("-" * 80)
        print(f"Target Avg Time: <75ms")
        print(f"Actual Avg Time: {with_nox['avg_time_ms']:.2f}ms {'✅' if with_nox['avg_time_ms'] < 75 else '❌'}")
        print(f"Target Hard Ceiling: <100ms")
        print(f"Actual Max Time: {with_nox['max_time_ms']:.2f}ms {'✅' if with_nox['max_time_ms'] < 100 else '❌'}")
        print(f"Target Compression: 30-50%")
        print(f"Actual Compression: {comparison['avg_compression_percent']:.1f}% {'✅' if 30 <= comparison['avg_compression_percent'] <= 50 else '❌'}")
        
        print("\n" + "=" * 80)
    
    def run_benchmark(self):
        """Run full benchmark."""
        print("\n🚀 Running NOX benchmark with realistic test responses...")
        
        # Generate test responses
        responses = self.generate_realistic_test_responses()
        
        # Benchmark without NOX
        print("\n📊 Benchmarking without NOX...")
        without_nox = self.benchmark_without_nox(responses)
        
        # Benchmark with NOX
        print("\n📊 Benchmarking with NOX...")
        with_nox = self.benchmark_with_nox(responses)
        
        # Compare
        comparison = self.compare_benchmarks(without_nox, with_nox)
        
        # Print results
        self.print_benchmark_results(without_nox, with_nox, comparison)
        
        return {
            "without_nox": without_nox,
            "with_nox": with_nox,
            "comparison": comparison
        }


def main():
    """Main benchmark entry point."""
    benchmark = NOXBenchmark()
    
    # Run benchmark
    results = benchmark.run_benchmark()
    
    # Save results to file
    results_file = Path.home() / ".hermes" / "nox_benchmark_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON-serializable format
    serializable_results = {
        "without_nox": {
            k: v for k, v in results["without_nox"].items()
            if k != "times"  # Skip raw times array
        },
        "with_nox": {
            k: v for k, v in results["with_nox"].items()
            if k != "times"  # Skip raw times array
        },
        "comparison": results["comparison"]
    }
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")


if __name__ == "__main__":
    main()
