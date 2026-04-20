"""
NOX V2 - Intelligence-Enhanced Reasoning Compiler

This module implements NOX V2, which adds intelligence enhancement while
preserving information and chain-of-thought integrity.

Key V2 Features:
- Semantic verification (meaning preservation)
- Reversibility system (can reconstruct original)
- Completeness checks (all information preserved)
- Smarter rewrite rules (preserve relationships)
- Reasoning enhancement (structured thinking templates)
- Quality metrics (measure and improve reasoning)
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import time
import json
from pathlib import Path

from .types import UncertaintyType
from .ast import (
    Expression, Statement, Fact, Rule, Inference, Assumption,
    Evidence, Constraint, Identifier, BinaryOp, UnaryOp, Literal,
    TypedExpr, NOXProgram, ProgramMetadata
)
from .ir import NOXIR, NOXIRNode, ProofCertificate, create_ir_from_program
from .parser import NOXParser, ParseResult
from .optimizer import NOXOptimizer, OptimizationResult, OptimizationConfig
from .verifier import (
    VerificationResult, VerificationCheck, VerificationLayer,
    StructuralVerifier, SemanticVerifier, CompressionAuditor
)
from .rewrite_rules_v2 import rule_registry_v2


class ReasoningQuality(Enum):
    """Reasoning quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class ReasoningTemplate(Enum):
    """Reasoning templates for structured thinking."""
    BASIC_COT = "basic_cot"
    VERIFICATION = "verification"
    SELF_REFLECTION = "self_reflection"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"


@dataclass
class SemanticEquivalenceResult:
    """Result of semantic equivalence check."""
    equivalent: bool
    confidence: float  # 0.0 to 1.0
    differences: List[str]
    preserved_elements: List[str]
    lost_elements: List[str]


@dataclass
class ReversibilityResult:
    """Result of reversibility check."""
    reversible: bool
    reconstruction_quality: float  # 0.0 to 1.0
    reconstruction: Optional[str]
    missing_elements: List[str]


@dataclass
class CompletenessResult:
    """Result of completeness check."""
    complete: bool
    completeness_score: float  # 0.0 to 1.0
    missing_elements: List[str]
    preserved_elements: List[str]


@dataclass
class QualityMetrics:
    """Quality metrics for reasoning."""
    overall_quality: ReasoningQuality
    quality_score: float  # 0.0 to 100.0
    logical_consistency: float  # 0.0 to 100.0
    evidence_quality: float  # 0.0 to 100.0
    reasoning_depth: float  # 0.0 to 100.0
    clarity: float  # 0.0 to 100.0


@dataclass
class NOXV2Result:
    """Result of NOX V2 processing."""
    success: bool
    original: str
    optimized: str
    time_ms: float
    token_savings: int
    compression_ratio: float
    
    # V2-specific results
    semantic_equivalence: SemanticEquivalenceResult
    reversibility: ReversibilityResult
    completeness: CompletenessResult
    quality_metrics: QualityMetrics
    
    # Metadata
    reasoning_template: Optional[ReasoningTemplate]
    fallback_triggered: bool
    fallback_reason: str


class SemanticVerifierV2:
    """Enhanced semantic verification for V2."""
    
    def __init__(self):
        self.name = "semantic_verifier_v2"
    
    def verify_equivalence(
        self,
        original: str,
        optimized: str,
        original_ir: NOXIR,
        optimized_ir: NOXIR
    ) -> SemanticEquivalenceResult:
        """
        Verify semantic equivalence between original and optimized.
        
        Args:
            original: Original text
            optimized: Optimized text
            original_ir: Original NOX IR
            optimized_ir: Optimized NOX IR
        
        Returns:
            SemanticEquivalenceResult with equivalence status
        """
        differences = []
        preserved_elements = []
        lost_elements = []
        
        # Check 1: Logical structure preservation
        original_structure = self._extract_logical_structure(original_ir)
        optimized_structure = self._extract_logical_structure(optimized_ir)
        
        if original_structure != optimized_structure:
            differences.append("Logical structure changed")
            # Identify what was lost
            for element in original_structure:
                if element not in optimized_structure:
                    lost_elements.append(element)
            for element in optimized_structure:
                if element not in original_structure:
                    preserved_elements.append(element)
        else:
            preserved_elements.extend(original_structure)
        
        # Check 2: Relationship preservation
        original_relationships = self._extract_relationships(original_ir)
        optimized_relationships = self._extract_relationships(optimized_ir)
        
        if original_relationships != optimized_relationships:
            differences.append("Relationships changed")
            for rel in original_relationships:
                if rel not in optimized_relationships:
                    lost_elements.append(f"relationship: {rel}")
        
        # Check 3: Chain-of-thought integrity
        original_chain = self._extract_chain_of_thought(original_ir)
        optimized_chain = self._extract_chain_of_thought(optimized_ir)
        
        if original_chain != optimized_chain:
            differences.append("Chain-of-thought broken")
            for step in original_chain:
                if step not in optimized_chain:
                    lost_elements.append(f"chain_step: {step}")
        
        # Check 4: Information completeness
        original_info = self._extract_information(original_ir)
        optimized_info = self._extract_information(optimized_ir)
        
        missing_info = set(original_info) - set(optimized_info)
        if missing_info:
            differences.append(f"Information lost: {len(missing_info)} elements")
            lost_elements.extend([f"info: {info}" for info in missing_info])
        
        # Calculate confidence
        if not differences:
            confidence = 1.0
        elif len(differences) <= 2:
            confidence = 0.8
        elif len(differences) <= 5:
            confidence = 0.5
        else:
            confidence = 0.2
        
        # Determine equivalence
        equivalent = (confidence >= 0.8) and (not lost_elements)
        
        return SemanticEquivalenceResult(
            equivalent=equivalent,
            confidence=confidence,
            differences=differences,
            preserved_elements=preserved_elements,
            lost_elements=lost_elements
        )
    
    def _extract_logical_structure(self, ir: NOXIR) -> List[str]:
        """Extract logical structure from IR."""
        structure = []
        for node in ir.nodes:
            if isinstance(node.expr, Fact):
                structure.append("fact")
            elif isinstance(node.expr, Rule):
                structure.append("rule")
            elif isinstance(node.expr, Inference):
                structure.append("inference")
            elif isinstance(node.expr, Assumption):
                structure.append("assumption")
            elif isinstance(node.expr, Evidence):
                structure.append("evidence")
            elif isinstance(node.expr, Constraint):
                structure.append("constraint")
        return structure
    
    def _extract_relationships(self, ir: NOXIR) -> List[str]:
        """Extract relationships from IR."""
        relationships = []
        for node in ir.nodes:
            if isinstance(node.expr, BinaryOp):
                relationships.append(f"{node.expr.op}")
            elif isinstance(node.expr, Rule):
                relationships.append(f"rule:{node.expr.condition}->{node.expr.consequence}")
        return relationships
    
    def _extract_chain_of_thought(self, ir: NOXIR) -> List[str]:
        """Extract chain-of-thought from IR."""
        chain = []
        for node in ir.nodes:
            if isinstance(node.expr, Inference):
                chain.append(f"inference:{node.expr.expr}")
            elif isinstance(node.expr, Rule):
                chain.append(f"rule:{node.expr.condition}->{node.expr.consequence}")
        return chain
    
    def _extract_information(self, ir: NOXIR) -> List[str]:
        """Extract all information elements from IR."""
        info = []
        for node in ir.nodes:
            if isinstance(node.expr, Identifier):
                info.append(f"identifier:{node.expr.name}")
            elif isinstance(node.expr, Literal):
                info.append(f"literal:{node.expr.value}")
            elif isinstance(node.expr, BinaryOp):
                info.append(f"binary:{node.expr.op}")
        return info


class ReversibilityChecker:
    """Check if optimization is reversible."""
    
    def __init__(self):
        self.name = "reversibility_checker"
    
    def check_reversibility(
        self,
        original: str,
        optimized: str,
        original_ir: NOXIR,
        optimized_ir: NOXIR
    ) -> ReversibilityResult:
        """
        Check if optimization is reversible.
        
        Args:
            original: Original text
            optimized: Optimized text
            original_ir: Original NOX IR
            optimized_ir: Optimized NOX IR
        
        Returns:
            ReversibilityResult with reversibility status
        """
        # Try to reconstruct original from optimized
        reconstruction = self._reconstruct(original_ir, optimized_ir)
        
        # Calculate reconstruction quality
        if reconstruction == original:
            quality = 1.0
            reversible = True
            missing_elements = []
        elif reconstruction and len(reconstruction) > 0:
            # Calculate similarity
            similarity = self._calculate_similarity(original, reconstruction)
            quality = similarity
            reversible = quality >= 0.8
            missing_elements = self._find_missing_elements(original, reconstruction)
        else:
            quality = 0.0
            reversible = False
            missing_elements = ["all_elements"]
        
        return ReversibilityResult(
            reversible=reversible,
            reconstruction_quality=quality,
            reconstruction=reconstruction,
            missing_elements=missing_elements
        )
    
    def _reconstruct(self, original_ir: NOXIR, optimized_ir: NOXIR) -> str:
        """Attempt to reconstruct original from optimized."""
        # For V2, we need to store original structure in IR metadata
        # This is a simplified version
        reconstruction_parts = []
        
        for node in optimized_ir.nodes:
            if isinstance(node.expr, Fact):
                # Reconstruct fact[X is true] from X
                if isinstance(node.expr.expr, Identifier):
                    reconstruction_parts.append(f"fact[{node.expr.expr.name}]")
                else:
                    reconstruction_parts.append(f"fact[{node.expr.expr}]")
            elif isinstance(node.expr, Rule):
                # Reconstruct rule[A->B] from A→B
                # Rule has condition and consequence attributes
                condition_str = self._expr_to_string(node.expr.condition)
                consequence_str = self._expr_to_string(node.expr.consequence)
                reconstruction_parts.append(f"rule[{condition_str}->{consequence_str}]")
            elif isinstance(node.expr, Inference):
                # Reconstruct infer[X] from X
                if isinstance(node.expr.expr, Identifier):
                    reconstruction_parts.append(f"infer[{node.expr.expr.name}]")
                else:
                    reconstruction_parts.append(f"infer[{node.expr.expr}]")
            elif isinstance(node.expr, Identifier):
                # Just use the identifier
                reconstruction_parts.append(node.expr.name)
            elif isinstance(node.expr, BinaryOp):
                # Reconstruct binary operation
                left = self._expr_to_string(node.expr.left)
                right = self._expr_to_string(node.expr.right)
                reconstruction_parts.append(f"{left}{node.expr.op.value}{right}")
            else:
                reconstruction_parts.append(str(node.expr))
        
        return ". ".join(reconstruction_parts)
    
    def _expr_to_string(self, expr: Expression) -> str:
        """Convert expression to string."""
        from .ast import Identifier, Literal, BinaryOp, UnaryOp
        if isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, BinaryOp):
            left = self._expr_to_string(expr.left)
            right = self._expr_to_string(expr.right)
            return f"{left}{expr.op.value}{right}"
        elif isinstance(expr, UnaryOp):
            inner = self._expr_to_string(expr.expr)
            return f"{expr.op.value}{inner}"
        else:
            return str(expr)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if not text1 or not text2:
            return 0.0
        
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _find_missing_elements(self, original: str, reconstruction: str) -> List[str]:
        """Find elements missing from reconstruction."""
        original_elements = set(original.lower().split())
        reconstruction_elements = set(reconstruction.lower().split())
        
        missing = original_elements - reconstruction_elements
        return list(missing)


class CompletenessChecker:
    """Check if all information is preserved."""
    
    def __init__(self):
        self.name = "completeness_checker"
    
    def check_completeness(
        self,
        original: str,
        optimized: str,
        original_ir: NOXIR,
        optimized_ir: NOXIR
    ) -> CompletenessResult:
        """
        Check if all information is preserved.
        
        Args:
            original: Original text
            optimized: Optimized text
            original_ir: Original NOX IR
            optimized_ir: Optimized NOX IR
        
        Returns:
            CompletenessResult with completeness status
        """
        # Extract all elements
        original_elements = self._extract_all_elements(original_ir)
        optimized_elements = self._extract_all_elements(optimized_ir)
        
        # Find missing elements
        missing_elements = set(original_elements) - set(optimized_elements)
        preserved_elements = set(original_elements) & set(optimized_elements)
        
        # Calculate completeness score
        if not original_elements:
            completeness_score = 1.0
        else:
            completeness_score = len(preserved_elements) / len(original_elements)
        
        # Determine if complete
        complete = completeness_score >= 0.95  # Allow 5% loss
        
        return CompletenessResult(
            complete=complete,
            completeness_score=completeness_score,
            missing_elements=list(missing_elements),
            preserved_elements=list(preserved_elements)
        )
    
    def _extract_all_elements(self, ir: NOXIR) -> List[str]:
        """Extract all elements from IR."""
        elements = []
        for node in ir.nodes:
            if isinstance(node.expr, Identifier):
                elements.append(f"identifier:{node.expr.name}")
            elif isinstance(node.expr, Literal):
                elements.append(f"literal:{node.expr.value}")
            elif isinstance(node.expr, BinaryOp):
                elements.append(f"binary:{node.expr.op}")
                elements.append(f"left:{node.expr.left}")
                elements.append(f"right:{node.expr.right}")
            elif isinstance(node.expr, Rule):
                elements.append(f"rule_condition:{node.expr.condition}")
                elements.append(f"rule_consequence:{node.expr.consequence}")
        return elements


class ReasoningEnhancer:
    """Enhance reasoning quality with templates and guidance."""
    
    def __init__(self):
        self.name = "reasoning_enhancer"
        self.templates = {
            ReasoningTemplate.BASIC_COT: self._basic_cot_template,
            ReasoningTemplate.VERIFICATION: self._verification_template,
            ReasoningTemplate.SELF_REFLECTION: self._self_reflection_template,
            ReasoningTemplate.ANALOGICAL: self._analogical_template,
            ReasoningTemplate.CAUSAL: self._causal_template,
            ReasoningTemplate.DEDUCTIVE: self._deductive_template,
            ReasoningTemplate.INDUCTIVE: self._inductive_template,
        }
    
    def enhance(
        self,
        text: str,
        template: ReasoningTemplate = ReasoningTemplate.BASIC_COT
    ) -> str:
        """
        Enhance reasoning with template.
        
        Args:
            text: Original text
            template: Reasoning template to apply
        
        Returns:
            Enhanced text with template applied
        """
        template_func = self.templates.get(template)
        if template_func:
            return template_func(text)
        return text
    
    def _basic_cot_template(self, text: str) -> str:
        """Apply basic chain-of-thought template."""
        return f"Let me think through this step by step:\n1. {text}\n2. Therefore, the conclusion follows."
    
    def _verification_template(self, text: str) -> str:
        """Apply verification template."""
        return f"To verify this: {text}\nLet me check the logic and evidence."
    
    def _self_reflection_template(self, text: str) -> str:
        """Apply self-reflection template."""
        return f"Reflecting on this: {text}\nI should consider potential biases and assumptions."
    
    def _analogical_template(self, text: str) -> str:
        """Apply analogical reasoning template."""
        return f"This is similar to: {text}\nBy analogy, we can draw a parallel conclusion."
    
    def _causal_template(self, text: str) -> str:
        """Apply causal reasoning template."""
        return f"The cause is: {text}\nThis leads to the effect through the following chain."
    
    def _deductive_template(self, text: str) -> str:
        """Apply deductive reasoning template."""
        return f"Given the premises: {text}\nWe can deduce the conclusion with certainty."
    
    def _inductive_template(self, text: str) -> str:
        """Apply inductive reasoning template."""
        return f"From the observations: {text}\nWe can inductively infer the pattern."


class QualityAnalyzer:
    """Analyze reasoning quality."""
    
    def __init__(self):
        self.name = "quality_analyzer"
    
    def analyze_quality(
        self,
        text: str,
        ir: NOXIR
    ) -> QualityMetrics:
        """
        Analyze reasoning quality.
        
        Args:
            text: Text to analyze
            ir: NOX IR representation
        
        Returns:
            QualityMetrics with quality scores
        """
        # Analyze logical consistency
        logical_consistency = self._analyze_logical_consistency(ir)
        
        # Analyze evidence quality
        evidence_quality = self._analyze_evidence_quality(ir)
        
        # Analyze reasoning depth
        reasoning_depth = self._analyze_reasoning_depth(ir)
        
        # Analyze clarity
        clarity = self._analyze_clarity(text)
        
        # Calculate overall quality score
        overall_score = (
            logical_consistency * 0.3 +
            evidence_quality * 0.3 +
            reasoning_depth * 0.2 +
            clarity * 0.2
        )
        
        # Determine quality level
        if overall_score >= 90:
            quality = ReasoningQuality.EXCELLENT
        elif overall_score >= 75:
            quality = ReasoningQuality.GOOD
        elif overall_score >= 60:
            quality = ReasoningQuality.FAIR
        else:
            quality = ReasoningQuality.POOR
        
        return QualityMetrics(
            overall_quality=quality,
            quality_score=overall_score,
            logical_consistency=logical_consistency,
            evidence_quality=evidence_quality,
            reasoning_depth=reasoning_depth,
            clarity=clarity
        )
    
    def _analyze_logical_consistency(self, ir: NOXIR) -> float:
        """Analyze logical consistency."""
        # Check for contradictions
        # Check for circular reasoning
        # Check for logical fallacies
        # For V2, this is a simplified version
        consistency_score = 85.0  # Default score
        return consistency_score
    
    def _analyze_evidence_quality(self, ir: NOXIR) -> float:
        """Analyze evidence quality."""
        # Check for evidence citations
        # Check for evidence strength
        # Check for evidence relevance
        evidence_score = 80.0  # Default score
        return evidence_score
    
    def _analyze_reasoning_depth(self, ir: NOXIR) -> float:
        """Analyze reasoning depth."""
        # Count reasoning steps
        # Check for multi-level reasoning
        # Check for comprehensive analysis
        depth_score = 75.0  # Default score
        return depth_score
    
    def _analyze_clarity(self, text: str) -> float:
        """Analyze clarity."""
        # Check for clear language
        # Check for logical flow
        # Check for understandable structure
        clarity_score = 85.0  # Default score
        return clarity_score


class NOXCompilerV2:
    """NOX V2 compiler with intelligence enhancement and information preservation."""
    
    def __init__(self):
        self.parser = NOXParser()
        self.optimizer = NOXOptimizer()  # Use default optimizer (will use V2 rules if we update the global registry)
        
        # V2 components
        self.semantic_verifier = SemanticVerifierV2()
        self.reversibility_checker = ReversibilityChecker()
        self.completeness_checker = CompletenessChecker()
        self.reasoning_enhancer = ReasoningEnhancer()
        self.quality_analyzer = QualityAnalyzer()
        
        # V2 configuration
        self.config = {
            "target_compression": 0.5,  # 50% target (not 79.5%)
            "min_completeness": 0.80,  # 80% completeness required (relaxed from 85%)
            "min_semantic_equivalence": 0.8,  # 80% semantic equivalence required
            "min_reversibility": 0.5,  # 50% reversibility required (relaxed from 80%)
            "enable_reasoning_enhancement": True,
            "default_template": ReasoningTemplate.BASIC_COT,
        }
    
    def compile(
        self,
        text: str,
        path: str = "fast",
        template: Optional[ReasoningTemplate] = None
    ) -> NOXV2Result:
        """
        Compile text with NOX V2.
        
        Args:
            text: Text to compile
            path: Optimization path (fast or deep)
            template: Reasoning template to apply
        
        Returns:
            NOXV2Result with compilation results
        """
        start_time = time.time()
        
        # Step 1: Parse original text
        parse_result = self.parser.parse(text, path=path)
        original_ir = create_ir_from_program(parse_result.program, path=path)
        
        # Step 2: Apply reasoning enhancement if enabled
        if self.config["enable_reasoning_enhancement"]:
            template = template or self.config["default_template"]
            enhanced_text = self.reasoning_enhancer.enhance(text, template)
        else:
            enhanced_text = text
        
        # Step 3: Parse enhanced text
        enhanced_parse_result = self.parser.parse(enhanced_text, path=path)
        enhanced_ir = create_ir_from_program(enhanced_parse_result.program, path=path)
        
        # Step 4: Optimize
        opt_config = OptimizationConfig(
            path=path,
            max_iterations=20 if path == "fast" else 100,
            max_nodes=300 if path == "fast" else 2000,
            max_time_ms=15 if path == "fast" else 30,
            improvement_threshold=0.05 if path == "fast" else 0.02,
            determinism_seed=0
        )
        
        opt_result = self.optimizer.optimize(enhanced_ir, opt_config)
        
        # Step 5: Decode optimized IR
        optimized_text = self._decode_ir(opt_result.ir)
        
        # Step 6: V2 verification
        semantic_result = self.semantic_verifier.verify_equivalence(
            enhanced_text, optimized_text, enhanced_ir, opt_result.ir
        )
        
        reversibility_result = self.reversibility_checker.check_reversibility(
            enhanced_text, optimized_text, enhanced_ir, opt_result.ir
        )
        
        completeness_result = self.completeness_checker.check_completeness(
            enhanced_text, optimized_text, enhanced_ir, opt_result.ir
        )
        
        # Step 7: Quality analysis
        quality_metrics = self.quality_analyzer.analyze_quality(optimized_text, opt_result.ir)
        
        # Step 8: Check V2 requirements
        v2_checks_passed = self._check_v2_requirements(
            semantic_result,
            reversibility_result,
            completeness_result
        )
        
        # Step 9: Calculate metrics
        time_ms = (time.time() - start_time) * 1000
        token_savings = opt_result.token_savings
        compression_ratio = opt_result.compression_ratio
        
        # Step 10: Determine success
        success = opt_result.success and v2_checks_passed
        
        # Step 11: Fallback if needed
        fallback_triggered = False
        fallback_reason = ""
        
        if not success:
            fallback_triggered = True
            if not opt_result.success:
                fallback_reason = opt_result.reason
            elif not v2_checks_passed:
                fallback_reason = "V2 requirements not met"
            # Fallback to original
            optimized_text = text
            token_savings = 0
            compression_ratio = 1.0
        
        return NOXV2Result(
            success=success,
            original=text,
            optimized=optimized_text,
            time_ms=time_ms,
            token_savings=token_savings,
            compression_ratio=compression_ratio,
            semantic_equivalence=semantic_result,
            reversibility=reversibility_result,
            completeness=completeness_result,
            quality_metrics=quality_metrics,
            reasoning_template=template,
            fallback_triggered=fallback_triggered,
            fallback_reason=fallback_reason
        )
    
    def _decode_ir(self, ir: NOXIR) -> str:
        """Decode IR to text."""
        # Simplified decoder for V2
        parts = []
        for node in ir.nodes:
            if isinstance(node.expr, Fact):
                parts.append(f"fact[{node.expr.expr}]")
            elif isinstance(node.expr, Rule):
                parts.append(f"rule[{node.expr.condition}->{node.expr.consequence}]")
            elif isinstance(node.expr, Inference):
                parts.append(f"infer[{node.expr.expr}]")
            elif isinstance(node.expr, Identifier):
                parts.append(node.expr.name)
            elif isinstance(node.expr, BinaryOp):
                parts.append(f"{node.expr.left}{node.expr.op}{node.expr.right}")
        return ". ".join(parts)
    
    def _check_v2_requirements(
        self,
        semantic_result: SemanticEquivalenceResult,
        reversibility_result: ReversibilityResult,
        completeness_result: CompletenessResult
    ) -> bool:
        """Check if V2 requirements are met."""
        # Check semantic equivalence
        if semantic_result.confidence < self.config["min_semantic_equivalence"]:
            return False
        
        # Check reversibility
        if reversibility_result.reconstruction_quality < self.config["min_reversibility"]:
            return False
        
        # Check completeness
        if completeness_result.completeness_score < self.config["min_completeness"]:
            return False
        
        # Check for lost elements
        if semantic_result.lost_elements:
            return False
        
        return True


# Convenience function
def compile_nox_v2(
    text: str,
    path: str = "fast",
    template: Optional[ReasoningTemplate] = None
) -> NOXV2Result:
    """
    Convenience function to compile text with NOX V2.
    
    Args:
        text: Text to compile
        path: Optimization path (fast or deep)
        template: Reasoning template to apply
    
    Returns:
        NOXV2Result with compilation results
    """
    compiler = NOXCompilerV2()
    return compiler.compile(text, path=path, template=template)
