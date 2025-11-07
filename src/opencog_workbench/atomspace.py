"""
AtomSpace Implementation for PDRH Models

Provides OpenCog AtomSpace-based knowledge representation for
Probabilistic Delta-Reachability Hybrid (PDRH) models.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json


class AtomType(Enum):
    """Types of atoms in the knowledge graph"""
    CONCEPT = "ConceptNode"
    PREDICATE = "PredicateNode"
    VARIABLE = "VariableNode"
    NUMBER = "NumberNode"
    LINK = "Link"
    EVALUATION = "EvaluationLink"
    INHERITANCE = "InheritanceLink"
    MODEL = "ModelNode"
    MODE = "ModeNode"
    PARAMETER = "ParameterNode"
    FLOW = "FlowNode"
    JUMP = "JumpNode"
    GOAL = "GoalNode"


@dataclass
class TruthValue:
    """Probabilistic truth value for atoms"""
    strength: float  # Probability [0, 1]
    confidence: float  # Confidence in the estimate [0, 1]
    
    def __post_init__(self):
        self.strength = max(0.0, min(1.0, self.strength))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass(eq=False)
class Atom:
    """Base atom class for knowledge representation"""
    atom_type: AtomType
    name: str
    truth_value: TruthValue = field(default_factory=lambda: TruthValue(1.0, 1.0))
    attention_value: float = 0.0
    incoming: Set['Atom'] = field(default_factory=set, repr=False, hash=False, compare=False)
    outgoing: List['Atom'] = field(default_factory=list, repr=False, hash=False, compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, repr=False, hash=False, compare=False)
    
    def __hash__(self):
        return hash((self.atom_type, self.name))
    
    def __eq__(self, other):
        return isinstance(other, Atom) and \
               self.atom_type == other.atom_type and \
               self.name == other.name


@dataclass(eq=False)
class PDRHAtom(Atom):
    """Specialized atom for PDRH model components"""
    model_file: Optional[str] = field(default=None, repr=False, hash=False, compare=False)
    mode_id: Optional[int] = field(default=None, repr=False, hash=False, compare=False)
    equation: Optional[str] = field(default=None, repr=False, hash=False, compare=False)
    condition: Optional[str] = field(default=None, repr=False, hash=False, compare=False)
    bounds: Optional[tuple] = field(default=None, repr=False, hash=False, compare=False)
    
    def __post_init__(self):
        if not hasattr(self, 'metadata') or self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        if self.model_file:
            self.metadata['model_file'] = self.model_file
        if self.mode_id is not None:
            self.metadata['mode_id'] = self.mode_id


class ModelAtomSpace:
    """
    OpenCog-style AtomSpace for PDRH models
    
    Provides knowledge representation and reasoning infrastructure
    for hybrid systems with parametric uncertainty.
    """
    
    def __init__(self):
        self.atoms: Dict[str, Atom] = {}
        self.links: List[Atom] = []
        self.models: Dict[str, PDRHAtom] = {}
        
    def add_atom(self, atom: Atom) -> Atom:
        """Add an atom to the atomspace"""
        key = self._atom_key(atom)
        if key in self.atoms:
            # Merge truth values if atom already exists
            existing = self.atoms[key]
            existing.truth_value = self._merge_truth_values(
                existing.truth_value, atom.truth_value
            )
            return existing
        
        self.atoms[key] = atom
        if atom.atom_type in [AtomType.LINK, AtomType.EVALUATION, AtomType.INHERITANCE]:
            self.links.append(atom)
            # Update incoming sets
            for outgoing in atom.outgoing:
                outgoing.incoming.add(atom)
        
        return atom
    
    def add_model(self, model_name: str, model_file: str) -> PDRHAtom:
        """Add a PDRH model to the atomspace"""
        model_atom = PDRHAtom(
            atom_type=AtomType.MODEL,
            name=model_name,
            model_file=model_file,
            truth_value=TruthValue(1.0, 1.0)
        )
        self.add_atom(model_atom)
        self.models[model_name] = model_atom
        return model_atom
    
    def add_mode(self, model_name: str, mode_id: int, mode_name: str) -> PDRHAtom:
        """Add a mode to a PDRH model"""
        mode_atom = PDRHAtom(
            atom_type=AtomType.MODE,
            name=f"{model_name}_mode_{mode_id}",
            mode_id=mode_id,
            metadata={'model': model_name, 'mode_name': mode_name}
        )
        self.add_atom(mode_atom)
        
        # Create inheritance link to model
        if model_name in self.models:
            inheritance = Atom(
                atom_type=AtomType.INHERITANCE,
                name=f"mode_{mode_id}_isa_{model_name}",
                outgoing=[mode_atom, self.models[model_name]]
            )
            self.add_atom(inheritance)
        
        return mode_atom
    
    def add_parameter(self, name: str, value: float, 
                     bounds: Optional[tuple] = None,
                     uncertainty: Optional[float] = None) -> PDRHAtom:
        """Add a parameter with uncertainty bounds"""
        confidence = 1.0 if uncertainty is None else max(0.0, 1.0 - uncertainty)
        param_atom = PDRHAtom(
            atom_type=AtomType.PARAMETER,
            name=name,
            bounds=bounds,
            truth_value=TruthValue(1.0, confidence),
            metadata={'value': value, 'bounds': bounds, 'uncertainty': uncertainty}
        )
        self.add_atom(param_atom)
        return param_atom
    
    def add_flow(self, mode_name: str, variable: str, equation: str) -> PDRHAtom:
        """Add a flow equation to a mode"""
        flow_atom = PDRHAtom(
            atom_type=AtomType.FLOW,
            name=f"{mode_name}_flow_{variable}",
            equation=equation,
            metadata={'mode': mode_name, 'variable': variable}
        )
        self.add_atom(flow_atom)
        return flow_atom
    
    def add_goal(self, goal_name: str, condition: str, 
                probability: float = 0.0) -> PDRHAtom:
        """Add a reachability goal"""
        goal_atom = PDRHAtom(
            atom_type=AtomType.GOAL,
            name=goal_name,
            condition=condition,
            truth_value=TruthValue(probability, 0.5)
        )
        self.add_atom(goal_atom)
        return goal_atom
    
    def get_atom(self, atom_type: AtomType, name: str) -> Optional[Atom]:
        """Retrieve an atom by type and name"""
        key = f"{atom_type.value}:{name}"
        return self.atoms.get(key)
    
    def get_atoms_by_type(self, atom_type: AtomType) -> List[Atom]:
        """Get all atoms of a specific type"""
        return [atom for atom in self.atoms.values() 
                if atom.atom_type == atom_type]
    
    def get_incoming(self, atom: Atom) -> Set[Atom]:
        """Get all atoms linking to this atom"""
        return atom.incoming
    
    def get_outgoing(self, atom: Atom) -> List[Atom]:
        """Get all atoms this atom links to"""
        return atom.outgoing
    
    def query(self, pattern: Dict[str, Any]) -> List[Atom]:
        """Simple pattern matching query"""
        results = []
        for atom in self.atoms.values():
            if self._matches_pattern(atom, pattern):
                results.append(atom)
        return results
    
    def _matches_pattern(self, atom: Atom, pattern: Dict[str, Any]) -> bool:
        """Check if atom matches query pattern"""
        for key, value in pattern.items():
            if key == 'type' and atom.atom_type != value:
                return False
            elif key == 'name' and atom.name != value:
                return False
            elif key in atom.metadata and atom.metadata[key] != value:
                return False
        return True
    
    def _atom_key(self, atom: Atom) -> str:
        """Generate unique key for atom"""
        return f"{atom.atom_type.value}:{atom.name}"
    
    def _merge_truth_values(self, tv1: TruthValue, tv2: TruthValue) -> TruthValue:
        """Merge two truth values using revision formula"""
        # Use PLN revision formula
        w1 = tv1.confidence
        w2 = tv2.confidence
        w_total = w1 + w2
        
        if w_total == 0:
            return TruthValue(0.5, 0.0)
        
        strength = (w1 * tv1.strength + w2 * tv2.strength) / w_total
        confidence = w_total / (w_total + 1.0)  # Simple confidence merge
        
        return TruthValue(strength, confidence)
    
    def export_to_json(self) -> str:
        """Export atomspace to JSON format"""
        data = {
            'atoms': [
                {
                    'type': atom.atom_type.value,
                    'name': atom.name,
                    'truth_value': {
                        'strength': atom.truth_value.strength,
                        'confidence': atom.truth_value.confidence
                    },
                    'attention': atom.attention_value,
                    'metadata': atom.metadata
                }
                for atom in self.atoms.values()
            ]
        }
        return json.dumps(data, indent=2)
    
    def __len__(self) -> int:
        return len(self.atoms)
    
    def __repr__(self) -> str:
        return f"ModelAtomSpace(atoms={len(self.atoms)}, models={len(self.models)})"
