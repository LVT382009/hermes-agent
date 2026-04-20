"""
Tests for NOX V2 Plugin
"""

import pytest
from plugins.nox.nox_v2 import (
    NOXCompilerV2,
    compile_nox_v2,
    ReasoningTemplate,
    ReasoningQuality,
    SemanticEquivalenceResult,
    ReversibilityResult,
    CompletenessResult,
    QualityMetrics
)


@pytest.fixture
def nox_v2_compiler():
    """Create NOX V2 compiler instance."""
    return NOXCompilerV2()


class TestNOXV2Compilation:
    """Test NOX V2 compilation."""
    
    def test_basic_compilation(self, nox_v2_compiler):
        """Test basic compilation."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        assert result.original == text
        assert result.optimized is not None
        assert result.time_ms > 0
        assert result.semantic_equivalence is not None
        assert result.reversibility is not None
        assert result.completeness is not None
        assert result.quality_metrics is not None
    
    def test_compilation_with_template(self, nox_v2_compiler):
        """Test compilation with reasoning template."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(
            text,
            path="fast",
            template=ReasoningTemplate.BASIC_COT
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.BASIC_COT
        # Check that template was applied
        assert "step by step" in result.optimized.lower() or result.optimized != text
    
    def test_compilation_preserves_relationships(self, nox_v2_compiler):
        """Test that compilation preserves relationships."""
        text = "rule[A->B]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        # V2 should preserve the relationship A->B
        assert "->" in result.optimized or "A" in result.optimized and "B" in result.optimized
        # Should NOT lose the relationship like V1 did
        assert not (result.optimized == "A" or result.optimized == "A.")
    
    def test_compilation_preserves_chain_of_thought(self, nox_v2_compiler):
        """Test that compilation preserves chain-of-thought."""
        text = "if C then D."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        # V2 should preserve the conditional relationship
        assert "C" in result.optimized and "D" in result.optimized
        # Should NOT lose the consequence like V1 did
        assert not (result.optimized == "C" or result.optimized == "C.")
    
    def test_semantic_equivalence_check(self, nox_v2_compiler):
        """Test semantic equivalence verification."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.semantic_equivalence is not None
        assert result.semantic_equivalence.equivalent
        assert result.semantic_equivalence.confidence >= 0.8
        # V2 should not have lost elements
        assert len(result.semantic_equivalence.lost_elements) == 0
    
    def test_reversibility_check(self, nox_v2_compiler):
        """Test reversibility verification."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.reversibility is not None
        assert result.reversibility.reversible
        assert result.reversibility.reconstruction_quality >= 0.8
        # V2 should be reversible
        assert result.reversibility.reconstruction is not None
    
    def test_completeness_check(self, nox_v2_compiler):
        """Test completeness verification."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.completeness is not None
        assert result.completeness.complete
        assert result.completeness.completeness_score >= 0.95
        # V2 should preserve all information
        assert len(result.completeness.missing_elements) == 0
    
    def test_quality_analysis(self, nox_v2_compiler):
        """Test quality analysis."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.quality_metrics is not None
        assert result.quality_metrics.overall_quality in [
            ReasoningQuality.EXCELLENT,
            ReasoningQuality.GOOD,
            ReasoningQuality.FAIR,
            ReasoningQuality.POOR
        ]
        assert result.quality_metrics.quality_score >= 0
        assert result.quality_metrics.quality_score <= 100
        assert result.quality_metrics.logical_consistency >= 0
        assert result.quality_metrics.evidence_quality >= 0
        assert result.quality_metrics.reasoning_depth >= 0
        assert result.quality_metrics.clarity >= 0
    
    def test_v2_requirements_check(self, nox_v2_compiler):
        """Test that V2 requirements are met."""
        text = "rule[A->B]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        # V2 requirements:
        # 1. Semantic equivalence >= 80%
        assert result.semantic_equivalence.confidence >= 0.8
        
        # 2. Reversibility >= 80%
        assert result.reversibility.reconstruction_quality >= 0.8
        
        # 3. Completeness >= 95%
        assert result.completeness.completeness_score >= 0.95
        
        # 4. No lost elements
        assert len(result.semantic_equivalence.lost_elements) == 0
    
    def test_fallback_on_v2_violation(self, nox_v2_compiler):
        """Test fallback when V2 requirements are not met."""
        # This test would require a case where V2 requirements are not met
        # For now, we test that fallback mechanism exists
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        # Check that fallback fields exist
        assert hasattr(result, 'fallback_triggered')
        assert hasattr(result, 'fallback_reason')
    
    def test_compression_ratio_v2(self, nox_v2_compiler):
        """Test that V2 compression is more conservative."""
        text = "rule[A->B]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        # V2 target: 30-50% compression (not 79.5% like V1)
        assert result.compression_ratio >= 0.5  # At most 50% compression
        assert result.compression_ratio <= 1.0  # At least 0% compression
        # V2 should preserve more information
        assert result.compression_ratio > 0.3  # At least 30% preserved


class TestNOXV2ReasoningEnhancement:
    """Test NOX V2 reasoning enhancement."""
    
    def test_basic_cot_template(self, nox_v2_compiler):
        """Test basic chain-of-thought template."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(
            text,
            path="fast",
            template=ReasoningTemplate.BASIC_COT
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.BASIC_COT
        # Check that template was applied
        assert "step" in result.optimized.lower()
    
    def test_verification_template(self, nox_v2_compiler):
        """Test verification template."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(
            text,
            path="fast",
            template=ReasoningTemplate.VERIFICATION
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.VERIFICATION
        # Check that template was applied
        assert "verify" in result.optimized.lower()
    
    def test_self_reflection_template(self, nox_v2_compiler):
        """Test self-reflection template."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(
            text,
            path="fast",
            template=ReasoningTemplate.SELF_REFLECTION
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.SELF_REFLECTION
        # Check that template was applied
        assert "reflect" in result.optimized.lower()
    
    def test_analogical_template(self, nox_v2_compiler):
        """Test analogical reasoning template."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(
            text,
            path="fast",
            template=ReasoningTemplate.ANALOGICAL
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.ANALOGICAL
        # Check that template was applied
        assert "similar" in result.optimized.lower()
    
    def test_causal_template(self, nox_v2_compiler):
        """Test causal reasoning template."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(
            text,
            path="fast",
            template=ReasoningTemplate.CAUSAL
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.CAUSAL
        # Check that template was applied
        assert "cause" in result.optimized.lower()
    
    def test_deductive_template(self, nox_v2_compiler):
        """Test deductive reasoning template."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(
            text,
            path="fast",
            template=ReasoningTemplate.DEDUCTIVE
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.DEDUCTIVE
        # Check that template was applied
        assert "deduce" in result.optimized.lower() or "premise" in result.optimized.lower()
    
    def test_inductive_template(self, nox_v2_compiler):
        """Test inductive reasoning template."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(
            text,
            path="fast",
            template=ReasoningTemplate.INDUCTIVE
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.INDUCTIVE
        # Check that template was applied
        assert "induct" in result.optimized.lower() or "pattern" in result.optimized.lower()


class TestNOXV2ConvenienceFunction:
    """Test NOX V2 convenience function."""
    
    def test_compile_nox_v2_function(self):
        """Test compile_nox_v2 convenience function."""
        text = "fact[X is true]."
        result = compile_nox_v2(text, path="fast")
        
        assert result.success
        assert result.original == text
        assert result.optimized is not None
        assert result.time_ms > 0
    
    def test_compile_nox_v2_with_template(self):
        """Test compile_nox_v2 with template."""
        text = "fact[X is true]."
        result = compile_nox_v2(
            text,
            path="fast",
            template=ReasoningTemplate.BASIC_COT
        )
        
        assert result.success
        assert result.reasoning_template == ReasoningTemplate.BASIC_COT


class TestNOXV2InformationPreservation:
    """Test that NOX V2 preserves information."""
    
    def test_preserve_implication_relationship(self, nox_v2_compiler):
        """Test that implication relationships are preserved."""
        text = "rule[A->B]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        # V2 should preserve A->B relationship
        assert "A" in result.optimized
        assert "B" in result.optimized
        # Should NOT be just "A" like V1
        assert result.optimized != "A"
        assert result.optimized != "A."
    
    def test_preserve_conditional_relationship(self, nox_v2_compiler):
        """Test that conditional relationships are preserved."""
        text = "if C then D."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        # V2 should preserve C and D
        assert "C" in result.optimized
        assert "D" in result.optimized
        # Should NOT be just "C" like V1
        assert result.optimized != "C"
        assert result.optimized != "C."
    
    def test_preserve_chain_of_thought(self, nox_v2_compiler):
        """Test that chain-of-thought is preserved."""
        text = "A implies B. B implies C. Therefore, A implies C."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        # V2 should preserve all elements
        assert "A" in result.optimized
        assert "B" in result.optimized
        assert "C" in result.optimized
        # Should preserve the chain
        assert len(result.completeness.missing_elements) == 0
    
    def test_no_information_loss(self, nox_v2_compiler):
        """Test that no information is lost."""
        text = "fact[X is true]. rule[A->B]. if C then D."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        # V2 should preserve all information
        assert len(result.semantic_equivalence.lost_elements) == 0
        assert len(result.completeness.missing_elements) == 0
        assert result.semantic_equivalence.equivalent
        assert result.completeness.complete


class TestNOXV2Performance:
    """Test NOX V2 performance."""
    
    def test_fast_path_performance(self, nox_v2_compiler):
        """Test fast path performance."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        # V2 fast path should still be fast
        assert result.time_ms < 100  # Hard ceiling
        assert result.time_ms < 75  # Target
    
    def test_deep_path_performance(self, nox_v2_compiler):
        """Test deep path performance."""
        text = "fact[X is true]."
        result = nox_v2_compiler.compile(text, path="deep")
        
        assert result.success
        # V2 deep path should still be fast
        assert result.time_ms < 100  # Hard ceiling
    
    def test_compression_ratio_v2(self, nox_v2_compiler):
        """Test that V2 compression is more conservative."""
        text = "rule[A->B]."
        result = nox_v2_compiler.compile(text, path="fast")
        
        assert result.success
        # V2 target: 30-50% compression (not 79.5% like V1)
        assert result.compression_ratio >= 0.5  # At most 50% compression
        assert result.compression_ratio <= 1.0  # At least 0% compression


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
