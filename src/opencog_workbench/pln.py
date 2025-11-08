"""
Probabilistic Logic Networks (PLN) for Reasoning

Implements PLN inference rules for reasoning about model properties,
parameter uncertainty, and reachability probabilities.
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import math

from .atomspace import Atom, TruthValue, AtomType, ModelAtomSpace


@dataclass
class InferenceRule:
    """Represents a PLN inference rule"""
    name: str
    premises_pattern: List[str]
    conclusion_pattern: str
    formula: str


class PLNReasoner:
    """
    Probabilistic Logic Networks reasoning engine
    
    Provides inference capabilities for reasoning about:
    - Parameter uncertainty propagation
    - Reachability probability bounds
    - Model property satisfaction
    """
    
    def __init__(self, atomspace: ModelAtomSpace):
        self.atomspace = atomspace
        self.inference_rules = self._initialize_rules()
        
    def _initialize_rules(self) -> Dict[str, InferenceRule]:
        """Initialize standard PLN inference rules"""
        return {
            'deduction': InferenceRule(
                name='deduction',
                premises_pattern=['A->B', 'B->C'],
                conclusion_pattern='A->C',
                formula='deduction'
            ),
            'induction': InferenceRule(
                name='induction',
                premises_pattern=['A->B'],
                conclusion_pattern='B->A',
                formula='induction'
            ),
            'abduction': InferenceRule(
                name='abduction',
                premises_pattern=['A->C', 'B->C'],
                conclusion_pattern='A->B',
                formula='abduction'
            ),
            'revision': InferenceRule(
                name='revision',
                premises_pattern=['A', 'A'],
                conclusion_pattern='A',
                formula='revision'
            )
        }
    
    def deduction(self, tv_ab: TruthValue, tv_bc: TruthValue) -> TruthValue:
        """
        Deduction: If A->B and B->C, then A->C
        
        Uses PLN deduction formula for truth value calculation
        """
        s_ab, c_ab = tv_ab.strength, tv_ab.confidence
        s_bc, c_bc = tv_bc.strength, tv_bc.confidence
        
        # PLN deduction formula
        strength = s_ab * s_bc
        confidence = c_ab * c_bc * (1.0 / (1.0 + abs(s_ab - s_bc)))
        
        return TruthValue(strength, confidence)
    
    def induction(self, tv_ab: TruthValue, 
                 evidence_count: int = 10) -> TruthValue:
        """
        Induction: If A->B with evidence, infer B->A
        
        Confidence decreases as this is uncertain inference
        """
        s_ab, c_ab = tv_ab.strength, tv_ab.confidence
        
        # Induction typically has lower confidence
        strength = s_ab * 0.8  # Reduced strength for reverse implication
        confidence = c_ab * (evidence_count / (evidence_count + 10.0))
        
        return TruthValue(strength, confidence)
    
    def abduction(self, tv_ac: TruthValue, tv_bc: TruthValue) -> TruthValue:
        """
        Abduction: If A->C and B->C, infer A->B
        
        Used for hypothesis generation
        """
        s_ac, c_ac = tv_ac.strength, tv_ac.confidence
        s_bc, c_bc = tv_bc.strength, tv_bc.confidence
        
        # Abduction formula
        strength = (s_ac * s_bc) / (s_ac * s_bc + (1 - s_ac) * (1 - s_bc))
        confidence = c_ac * c_bc * 0.5  # Lower confidence for abduction
        
        return TruthValue(strength, confidence)
    
    def revision(self, tv1: TruthValue, tv2: TruthValue) -> TruthValue:
        """
        Revision: Merge two pieces of evidence about same statement
        
        Used for combining multiple sources of information
        """
        s1, c1 = tv1.strength, tv1.confidence
        s2, c2 = tv2.strength, tv2.confidence
        
        # PLN revision formula
        w1 = c1
        w2 = c2
        w_total = w1 + w2
        
        if w_total == 0:
            return TruthValue(0.5, 0.0)
        
        strength = (w1 * s1 + w2 * s2) / w_total
        confidence = w_total / (w_total + 1.0)
        
        return TruthValue(strength, confidence)
    
    def conjunction(self, tv_list: List[TruthValue]) -> TruthValue:
        """
        Conjunction: Combine multiple conditions with AND
        
        Used for complex goal conditions
        """
        if not tv_list:
            return TruthValue(1.0, 1.0)
        
        # Product of strengths, geometric mean of confidences
        strength = 1.0
        confidence_product = 1.0
        
        for tv in tv_list:
            strength *= tv.strength
            confidence_product *= tv.confidence
        
        confidence = math.pow(confidence_product, 1.0 / len(tv_list))
        
        return TruthValue(strength, confidence)
    
    def disjunction(self, tv_list: List[TruthValue]) -> TruthValue:
        """
        Disjunction: Combine multiple conditions with OR
        
        Used for alternative paths to goal
        """
        if not tv_list:
            return TruthValue(0.0, 1.0)
        
        # 1 - product of (1 - strength)
        strength = 1.0
        confidence_product = 1.0
        
        for tv in tv_list:
            strength *= (1.0 - tv.strength)
            confidence_product *= tv.confidence
        
        strength = 1.0 - strength
        confidence = math.pow(confidence_product, 1.0 / len(tv_list))
        
        return TruthValue(strength, confidence)
    
    def propagate_uncertainty(self, parameter_name: str, 
                             operation: str = 'multiply') -> TruthValue:
        """
        Propagate parameter uncertainty through model
        
        Analyzes how parameter uncertainty affects reachability
        """
        param_atom = self.atomspace.get_atom(AtomType.PARAMETER, parameter_name)
        if not param_atom:
            return TruthValue(0.5, 0.0)
        
        # Get parameter uncertainty from truth value confidence
        uncertainty = 1.0 - param_atom.truth_value.confidence
        
        # Propagate based on operation type
        if operation == 'multiply':
            # Multiplicative uncertainty propagation
            propagated_confidence = param_atom.truth_value.confidence * 0.9
        elif operation == 'add':
            # Additive uncertainty propagation
            propagated_confidence = param_atom.truth_value.confidence * 0.95
        else:
            propagated_confidence = param_atom.truth_value.confidence * 0.8
        
        return TruthValue(param_atom.truth_value.strength, propagated_confidence)
    
    def reason_about_reachability(self, goal_name: str, 
                                 evidence: List[Tuple[str, TruthValue]]) -> TruthValue:
        """
        Reason about reachability probability given evidence
        
        Combines multiple pieces of evidence to estimate goal reachability
        """
        if not evidence:
            return TruthValue(0.5, 0.0)
        
        # Start with prior from atomspace if available
        goal_atom = self.atomspace.get_atom(AtomType.GOAL, goal_name)
        if goal_atom:
            current_tv = goal_atom.truth_value
        else:
            current_tv = TruthValue(0.5, 0.1)
        
        # Update with each piece of evidence using revision
        for evidence_name, evidence_tv in evidence:
            current_tv = self.revision(current_tv, evidence_tv)
        
        return current_tv
    
    def infer_parameter_bounds(self, param_name: str, 
                              observations: List[float]) -> Tuple[float, float]:
        """
        Infer parameter bounds from observations
        
        Uses statistical reasoning to estimate bounds
        """
        if not observations:
            return (0.0, 1.0)
        
        mean = sum(observations) / len(observations)
        variance = sum((x - mean) ** 2 for x in observations) / len(observations)
        std_dev = math.sqrt(variance)
        
        # Use 2-sigma bounds
        lower = mean - 2 * std_dev
        upper = mean + 2 * std_dev
        
        return (lower, upper)
    
    def backward_chain(self, goal: Atom, max_depth: int = 3) -> List[Atom]:
        """
        Backward chaining inference from goal
        
        Find premises that would support the goal
        """
        if max_depth == 0:
            return []
        
        supporting_atoms = []
        
        # Find atoms that link to the goal
        incoming = self.atomspace.get_incoming(goal)
        
        for atom in incoming:
            supporting_atoms.append(atom)
            # Recursively find support
            if max_depth > 1:
                supporting_atoms.extend(
                    self.backward_chain(atom, max_depth - 1)
                )
        
        return supporting_atoms
    
    def forward_chain(self, premises: List[Atom], 
                     max_steps: int = 3) -> List[Atom]:
        """
        Forward chaining inference from premises
        
        Derive conclusions from given premises
        """
        conclusions = []
        current_premises = premises.copy()
        
        for step in range(max_steps):
            new_conclusions = []
            
            # Try to apply inference rules
            for premise in current_premises:
                outgoing = self.atomspace.get_outgoing(premise)
                new_conclusions.extend(outgoing)
            
            if not new_conclusions:
                break
            
            conclusions.extend(new_conclusions)
            current_premises = new_conclusions
        
        return conclusions
    
    def estimate_goal_probability(self, goal_condition: str,
                                  simulation_results: Dict[str, Any]) -> float:
        """
        Estimate goal reachability probability from simulation results
        
        Combines simulation data with logical reasoning
        """
        # Extract relevant statistics from simulation
        trajectories = simulation_results.get('trajectories', [])
        if not trajectories:
            return 0.5
        
        # Count how many trajectories satisfy goal
        satisfied = 0
        for traj in trajectories:
            # In real implementation, would evaluate goal_condition on trajectory
            satisfied += 1  # Placeholder
        
        probability = satisfied / len(trajectories)
        
        return probability
    
    def explain_inference(self, conclusion: Atom, 
                         trace: bool = True) -> Dict[str, Any]:
        """
        Explain how a conclusion was reached
        
        Provides transparency in reasoning process
        """
        explanation = {
            'conclusion': {
                'type': conclusion.atom_type.value,
                'name': conclusion.name,
                'truth_value': {
                    'strength': conclusion.truth_value.strength,
                    'confidence': conclusion.truth_value.confidence
                }
            },
            'premises': [],
            'inference_chain': []
        }
        
        # Find supporting premises
        incoming = self.atomspace.get_incoming(conclusion)
        for atom in incoming:
            explanation['premises'].append({
                'type': atom.atom_type.value,
                'name': atom.name
            })
        
        return explanation
    
    def __repr__(self):
        return f"PLNReasoner(rules={len(self.inference_rules)})"
