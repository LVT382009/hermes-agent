"""
NOX Plugin Benchmark - NOX-Compatible Test Cases

Compares performance with and without NOX enabled using NOX-compatible responses.
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
    
    def generate_nox_compatible_responses(self) -> List[str]:
        """Generate NOX-compatible test responses."""
        responses = []
        
        # Short responses with NOX patterns (fast path)
        responses.extend([
            "fact[X is true].",
            "fact[Y is valid].",
            "fact[Z is correct].",
            "rule[A->B].",
            "rule[C->D].",
            "rule[E->F].",
            "if G then H.",
            "if I then J.",
            "if K then L.",
            "M implies N.",
            "O means P.",
            "Q results in R.",
        ])
        
        # Medium responses with NOX patterns (fast path)
        responses.extend([
            "fact[X is true]. fact[Y is valid]. rule[X->Y].",
            "fact[A is correct]. rule[A->B]. fact[B is true].",
            "fact[C is valid]. rule[C->D]. rule[D->E].",
            "if P then Q. fact[Q is true].",
            "if R then S. rule[R->S].",
            "T implies U. fact[U is valid].",
            "V means W. rule[V->W].",
            "X results in Y. fact[Y is true].",
        ])
        
        # Long responses with NOX patterns (deep path)
        responses.extend([
            "fact[A is true]. fact[B is valid]. rule[A->B]. fact[C is correct]. rule[B->C]. fact[D is true]. rule[C->D].",
            "fact[E is valid]. fact[F is correct]. rule[E->F]. fact[G is true]. rule[F->G]. fact[H is valid]. rule[G->H].",
            "if I then J. fact[J is true]. if K then L. fact[L is valid]. if M then N. fact[N is correct].",
            "P implies Q. fact[Q is true]. R means S. fact[S is valid]. T results in U. fact[U is correct].",
            "fact[V is true]. rule[V->W]. fact[W is valid]. rule[W->X]. fact[X is correct]. rule[X->Y]. fact[Y is true].",
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
        print("\n🚀 Running NOX benchmark with NOX-compatible test responses...")
        
        # Generate test responses
        responses = self.generate_nox_compatible_responses()
        
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
