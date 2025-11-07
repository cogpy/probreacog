"""
Economic Attention Network (ECAN) for Task Prioritization

Implements ECAN-inspired attention allocation mechanism for
prioritizing tasks and focusing computational resources.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import math

from .atomspace import Atom, AtomType, ModelAtomSpace


@dataclass
class AttentionValue:
    """Attention value for atoms"""
    sti: float  # Short-term importance
    lti: float  # Long-term importance
    vlti: float  # Very long-term importance
    
    @property
    def total(self) -> float:
        """Total attention value"""
        return self.sti + 0.5 * self.lti + 0.25 * self.vlti


class AttentionAllocation:
    """
    ECAN-based attention allocation system
    
    Manages computational resources by:
    - Allocating attention to important atoms
    - Spreading attention through the network
    - Focusing resources on high-priority tasks
    """
    
    def __init__(self, atomspace: ModelAtomSpace, total_sti: float = 1000.0):
        self.atomspace = atomspace
        self.total_sti = total_sti  # Total STI budget
        self.attention_bank = total_sti
        self.atom_attention: Dict[str, AttentionValue] = {}
        self.attentional_focus: Set[Atom] = set()
        self.focus_boundary: float = 0.3  # Threshold for being "in focus"
        
    def initialize_attention(self):
        """Initialize attention values for all atoms"""
        atoms = list(self.atomspace.atoms.values())
        if not atoms:
            return
        
        # Distribute initial STI uniformly
        initial_sti = self.total_sti / len(atoms)
        
        for atom in atoms:
            key = self._atom_key(atom)
            self.atom_attention[key] = AttentionValue(
                sti=initial_sti,
                lti=0.0,
                vlti=0.0
            )
    
    def stimulate_atom(self, atom: Atom, amount: float):
        """Add STI to an atom (stimulus)"""
        key = self._atom_key(atom)
        if key not in self.atom_attention:
            self.atom_attention[key] = AttentionValue(0.0, 0.0, 0.0)
        
        # Transfer STI from bank to atom
        actual_amount = min(amount, self.attention_bank)
        self.atom_attention[key].sti += actual_amount
        self.attention_bank -= actual_amount
        
        # Update atom's attention value
        atom.attention_value = self.atom_attention[key].total
    
    def diffuse_attention(self, decay_rate: float = 0.1):
        """
        Diffuse attention through the network
        
        STI spreads from atoms to their neighbors
        """
        # Collect attention to diffuse
        diffusion_amounts: Dict[str, float] = {}
        
        for atom_key, attention in self.atom_attention.items():
            if attention.sti > 0:
                # Calculate diffusion amount
                diffusion = attention.sti * decay_rate
                diffusion_amounts[atom_key] = diffusion
        
        # Apply diffusion
        for atom in self.atomspace.atoms.values():
            atom_key = self._atom_key(atom)
            
            if atom_key in diffusion_amounts:
                diffusion = diffusion_amounts[atom_key]
                
                # Reduce source atom's STI
                self.atom_attention[atom_key].sti -= diffusion
                
                # Spread to neighbors
                neighbors = list(atom.incoming) + atom.outgoing
                if neighbors:
                    diffusion_per_neighbor = diffusion / len(neighbors)
                    
                    for neighbor in neighbors:
                        neighbor_key = self._atom_key(neighbor)
                        if neighbor_key in self.atom_attention:
                            self.atom_attention[neighbor_key].sti += diffusion_per_neighbor
    
    def update_lti(self, atom: Atom, learning_rate: float = 0.01):
        """
        Update long-term importance based on usage patterns
        
        Atoms that are consistently important gain LTI
        """
        key = self._atom_key(atom)
        if key not in self.atom_attention:
            return
        
        attention = self.atom_attention[key]
        
        # LTI increases when STI is high
        if attention.sti > self.focus_boundary * self.total_sti / 100:
            attention.lti += learning_rate * attention.sti
        else:
            # Decay LTI slowly when not in focus
            attention.lti *= (1.0 - learning_rate * 0.1)
    
    def normalize_sti(self):
        """
        Normalize STI values to maintain budget
        
        Ensures total STI across all atoms equals budget
        """
        total_current = sum(av.sti for av in self.atom_attention.values())
        
        if total_current == 0:
            return
        
        # Scale all STI values
        scale_factor = self.total_sti / total_current
        
        for attention in self.atom_attention.values():
            attention.sti *= scale_factor
        
        self.attention_bank = 0.0
    
    def update_attentional_focus(self):
        """
        Update the set of atoms in attentional focus
        
        Focus includes atoms with STI above threshold
        """
        self.attentional_focus.clear()
        threshold = self.focus_boundary * self.total_sti / 100
        
        for atom in self.atomspace.atoms.values():
            key = self._atom_key(atom)
            if key in self.atom_attention:
                if self.atom_attention[key].sti >= threshold:
                    self.attentional_focus.add(atom)
                    # Update atom's attention value
                    atom.attention_value = self.atom_attention[key].total
    
    def get_top_atoms(self, n: int = 10, 
                     atom_type: Optional[AtomType] = None) -> List[Atom]:
        """Get top N atoms by attention value"""
        atoms = list(self.atomspace.atoms.values())
        
        if atom_type:
            atoms = [a for a in atoms if a.atom_type == atom_type]
        
        # Sort by total attention
        atoms_with_attention = [
            (atom, self.atom_attention.get(self._atom_key(atom), 
                                          AttentionValue(0, 0, 0)).total)
            for atom in atoms
        ]
        atoms_with_attention.sort(key=lambda x: x[1], reverse=True)
        
        return [atom for atom, _ in atoms_with_attention[:n]]
    
    def focus_on_goal(self, goal_atom: Atom, intensity: float = 100.0):
        """
        Focus attention on a specific goal
        
        Stimulates goal atom and spreads attention to related atoms
        """
        # Stimulate goal
        self.stimulate_atom(goal_atom, intensity)
        
        # Stimulate related atoms
        related = list(goal_atom.incoming) + goal_atom.outgoing
        for atom in related:
            self.stimulate_atom(atom, intensity * 0.5)
        
        # Diffuse attention
        self.diffuse_attention(decay_rate=0.2)
        self.update_attentional_focus()
    
    def forget_atoms(self, threshold: float = 0.01):
        """
        Remove atoms with very low attention from focus
        
        Implements importance-based forgetting
        """
        atoms_to_forget = []
        
        for atom_key, attention in self.atom_attention.items():
            if attention.sti < threshold and attention.lti < threshold:
                atoms_to_forget.append(atom_key)
        
        # Return STI to bank before forgetting
        for atom_key in atoms_to_forget:
            attention = self.atom_attention[atom_key]
            self.attention_bank += attention.sti
            del self.atom_attention[atom_key]
        
        return len(atoms_to_forget)
    
    def calculate_importance(self, atom: Atom, 
                           context: Optional[Set[Atom]] = None) -> float:
        """
        Calculate importance of atom in given context
        
        Considers:
        - Intrinsic importance (LTI)
        - Current relevance (STI)
        - Connectivity to context
        """
        key = self._atom_key(atom)
        attention = self.atom_attention.get(key, AttentionValue(0, 0, 0))
        
        # Base importance from attention values
        importance = attention.total
        
        # Boost if connected to context
        if context:
            connections = len(context.intersection(atom.incoming)) + \
                         len(context.intersection(set(atom.outgoing)))
            importance *= (1.0 + 0.1 * connections)
        
        return importance
    
    def spread_activation(self, source_atoms: List[Atom], 
                         steps: int = 3, decay: float = 0.5):
        """
        Spread activation from source atoms through network
        
        Implements spreading activation for relevance computation
        """
        current_layer = set(source_atoms)
        activation_amounts = {self._atom_key(atom): 1.0 for atom in source_atoms}
        
        for step in range(steps):
            next_layer = set()
            current_activation = decay ** step
            
            for atom in current_layer:
                # Spread to connected atoms
                neighbors = list(atom.incoming) + atom.outgoing
                
                for neighbor in neighbors:
                    neighbor_key = self._atom_key(neighbor)
                    
                    # Add activation
                    if neighbor_key not in activation_amounts:
                        activation_amounts[neighbor_key] = 0.0
                    activation_amounts[neighbor_key] += current_activation
                    
                    next_layer.add(neighbor)
            
            current_layer = next_layer
        
        # Apply activations as STI stimulus
        for atom_key, activation in activation_amounts.items():
            for atom in self.atomspace.atoms.values():
                if self._atom_key(atom) == atom_key:
                    self.stimulate_atom(atom, activation * 10.0)
                    break
    
    def rent_collection(self, rate: float = 0.1):
        """
        Collect rent from all atoms
        
        STI decays over time, simulating forgetting
        """
        for attention in self.atom_attention.values():
            rent = attention.sti * rate
            attention.sti -= rent
            self.attention_bank += rent
    
    def run_attention_cycle(self, iterations: int = 10):
        """
        Run complete attention allocation cycle
        
        Includes diffusion, rent collection, and focus update
        """
        for _ in range(iterations):
            self.diffuse_attention(decay_rate=0.1)
            self.rent_collection(rate=0.05)
            
            # Update LTI for focused atoms
            for atom in self.attentional_focus:
                self.update_lti(atom)
            
            self.update_attentional_focus()
            self.normalize_sti()
    
    def get_statistics(self) -> Dict[str, float]:
        """Get attention allocation statistics"""
        sti_values = [av.sti for av in self.atom_attention.values()]
        lti_values = [av.lti for av in self.atom_attention.values()]
        
        return {
            'total_sti': sum(sti_values),
            'attention_bank': self.attention_bank,
            'mean_sti': sum(sti_values) / len(sti_values) if sti_values else 0,
            'max_sti': max(sti_values) if sti_values else 0,
            'focus_size': len(self.attentional_focus),
            'mean_lti': sum(lti_values) / len(lti_values) if lti_values else 0,
        }
    
    def _atom_key(self, atom: Atom) -> str:
        """Generate unique key for atom"""
        return f"{atom.atom_type.value}:{atom.name}"
    
    def __repr__(self):
        return f"AttentionAllocation(focus={len(self.attentional_focus)}, bank={self.attention_bank:.2f})"
