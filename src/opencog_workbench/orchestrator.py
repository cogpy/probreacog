"""
Main Orchestrator for OpenCog Multi-Agent Workbench

Integrates AtomSpace, PLN, ECAN, and multi-agent coordination
to provide a unified interface for model analysis.
"""

from typing import Dict, List, Optional, Any
import logging
import json
from pathlib import Path

from .atomspace import ModelAtomSpace, PDRHAtom, AtomType, TruthValue
from .agents import (Agent, AgentCoordinator, Task, AgentRole,
                     SimulatorAgent, VerifierAgent, AnalyzerAgent)
from .pln import PLNReasoner
from .ecan import AttentionAllocation


class WorkbenchOrchestrator:
    """
    Main orchestrator for the OpenCog workbench
    
    Provides high-level interface for:
    - Loading and representing PDRH models
    - Coordinating agent activities
    - Reasoning about model properties
    - Managing attention and priorities
    """
    
    def __init__(self, log_level: int = logging.INFO):
        # Core components
        self.atomspace = ModelAtomSpace()
        self.reasoner = PLNReasoner(self.atomspace)
        self.attention = AttentionAllocation(self.atomspace)
        self.coordinator = AgentCoordinator(self.atomspace)
        
        # Setup logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("WorkbenchOrchestrator")
        
        # Initialize default agents
        self._initialize_agents()
        
        self.logger.info("OpenCog Workbench initialized")
    
    def _initialize_agents(self):
        """Initialize default set of agents"""
        # Create agents for each role
        simulator = SimulatorAgent("simulator_1", self.atomspace)
        verifier = VerifierAgent("verifier_1", self.atomspace)
        analyzer = AnalyzerAgent("analyzer_1", self.atomspace)
        
        # Register with coordinator
        self.coordinator.register_agent(simulator)
        self.coordinator.register_agent(verifier)
        self.coordinator.register_agent(analyzer)
        
        self.logger.info(f"Initialized {len(self.coordinator.agents)} agents")
    
    def load_pdrh_model(self, model_file: str, model_name: Optional[str] = None) -> PDRHAtom:
        """
        Load a PDRH model into the atomspace
        
        Args:
            model_file: Path to .pdrh file
            model_name: Optional name for the model
        
        Returns:
            Model atom representing the loaded model
        """
        if model_name is None:
            model_name = Path(model_file).stem
        
        self.logger.info(f"Loading model {model_name} from {model_file}")
        
        # Create model atom
        model_atom = self.atomspace.add_model(model_name, model_file)
        
        # In real implementation, would parse PDRH file and extract:
        # - Modes
        # - Parameters
        # - Variables
        # - Flow equations
        # - Jump conditions
        # - Goals
        
        # For now, create example structure for psoriasis model
        if 'psoriasis' in model_name.lower():
            self._load_psoriasis_model(model_name)
        
        # Initialize attention for model
        self.attention.initialize_attention()
        
        self.logger.info(f"Model {model_name} loaded with {len(self.atomspace)} atoms")
        return model_atom
    
    def _load_psoriasis_model(self, model_name: str):
        """Load psoriasis therapy model structure"""
        # Add modes
        self.atomspace.add_mode(model_name, 1, "treatment")
        self.atomspace.add_mode(model_name, 2, "recovery")
        
        # Add parameters with uncertainty
        params = [
            ('gamma1', 0.0033, (0.002, 0.005), 0.1),
            ('gamma1d', 0.0132, (0.008, 0.016), 0.1),
            ('k1as', 0.0131, (0.01, 0.02), 0.1),
            ('beta1', 1.97e-06, (1e-06, 3e-06), 0.15),
            ('InA', 60000, (50000, 70000), 0.2),
        ]
        
        for name, value, bounds, uncertainty in params:
            self.atomspace.add_parameter(name, value, bounds, uncertainty)
        
        # Add goal
        self.atomspace.add_goal(
            "remission_365",
            "tau = 365 and SC_d < 100",
            probability=0.0
        )
    
    def create_analysis_workflow(self, model_name: str, 
                                 workflow_name: str = "default") -> str:
        """
        Create a comprehensive analysis workflow
        
        Args:
            model_name: Name of model to analyze
            workflow_name: Name for the workflow
        
        Returns:
            Workflow ID
        """
        workflow_id = f"{workflow_name}_{model_name}"
        
        # Create task sequence
        tasks = []
        
        # Task 1: Simulation
        sim_task = self.coordinator.create_task(
            task_id=f"{workflow_id}_simulate",
            task_type="simulate",
            agent_role=AgentRole.SIMULATOR,
            parameters={
                'model_file': f"model/{model_name}/{model_name}.pdrh",
                'num_paths': 100,
                'depth': 365
            },
            priority=0.8
        )
        tasks.append(sim_task)
        
        # Task 2: Formal verification
        verify_task = self.coordinator.create_task(
            task_id=f"{workflow_id}_verify",
            task_type="verify",
            agent_role=AgentRole.VERIFIER,
            parameters={
                'model_file': f"model/{model_name}/{model_name}.pdrh",
                'goal': 'remission_365',
                'precision': 0.01
            },
            priority=0.9,
            dependencies=[sim_task.task_id]
        )
        tasks.append(verify_task)
        
        # Task 3: Analysis
        analyze_task = self.coordinator.create_task(
            task_id=f"{workflow_id}_analyze",
            task_type="analyze",
            agent_role=AgentRole.ANALYZER,
            parameters={
                'analysis_type': 'sensitivity',
                'data': None  # Will be populated from verification
            },
            priority=0.7,
            dependencies=[verify_task.task_id]
        )
        tasks.append(analyze_task)
        
        # Create workflow
        self.coordinator.create_workflow(workflow_id, tasks)
        
        self.logger.info(f"Created workflow {workflow_id} with {len(tasks)} tasks")
        return workflow_id
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow and return results
        
        Args:
            workflow_id: ID of workflow to execute
        
        Returns:
            Workflow execution results
        """
        self.logger.info(f"Executing workflow {workflow_id}")
        
        # Focus attention on workflow goal
        workflow = self.coordinator.workflows.get(workflow_id)
        if workflow:
            for task in workflow:
                # Focus on high-priority tasks
                if task.priority > 0.7:
                    # Would focus on task-related atoms
                    pass
        
        # Execute workflow
        results = self.coordinator.execute_workflow(workflow_id)
        
        # Update atomspace with results
        self._update_atomspace_with_results(results)
        
        # Run attention cycle
        self.attention.run_attention_cycle(iterations=5)
        
        self.logger.info(f"Workflow {workflow_id} completed")
        return results
    
    def _update_atomspace_with_results(self, results: Dict[str, Any]):
        """Update atomspace with workflow results"""
        for task_id, task_result in results.get('tasks', {}).items():
            if task_result.get('status') == 'completed':
                result_data = task_result.get('result', {})
                
                # Update goal probabilities from verification
                if 'probability_bounds' in result_data:
                    bounds = result_data['probability_bounds']
                    goal_name = result_data.get('goal', 'unknown')
                    goal_atom = self.atomspace.get_atom(AtomType.GOAL, goal_name)
                    
                    if goal_atom:
                        # Update truth value with probability bounds
                        mean_prob = (bounds[0] + bounds[1]) / 2.0
                        confidence = 1.0 - (bounds[1] - bounds[0])  # Tighter bounds = higher confidence
                        goal_atom.truth_value = TruthValue(mean_prob, confidence)
    
    def reason_about_goal(self, goal_name: str) -> Dict[str, Any]:
        """
        Use PLN to reason about goal reachability
        
        Args:
            goal_name: Name of goal to reason about
        
        Returns:
            Reasoning results and explanation
        """
        self.logger.info(f"Reasoning about goal: {goal_name}")
        
        goal_atom = self.atomspace.get_atom(AtomType.GOAL, goal_name)
        if not goal_atom:
            return {'error': f'Goal {goal_name} not found'}
        
        # Gather evidence
        evidence = []
        
        # Get parameter uncertainties
        params = self.atomspace.get_atoms_by_type(AtomType.PARAMETER)
        for param in params:
            # Propagate uncertainty
            propagated = self.reasoner.propagate_uncertainty(param.name)
            evidence.append((param.name, propagated))
        
        # Reason about reachability
        reachability_tv = self.reasoner.reason_about_reachability(goal_name, evidence)
        
        # Get explanation
        explanation = self.reasoner.explain_inference(goal_atom)
        
        return {
            'goal': goal_name,
            'reachability': {
                'probability': reachability_tv.strength,
                'confidence': reachability_tv.confidence
            },
            'evidence': [
                {'name': name, 'strength': tv.strength, 'confidence': tv.confidence}
                for name, tv in evidence
            ],
            'explanation': explanation
        }
    
    def optimize_attention(self, focus_atoms: Optional[List[str]] = None):
        """
        Optimize attention allocation
        
        Args:
            focus_atoms: Optional list of atom names to focus on
        """
        if focus_atoms:
            for atom_name in focus_atoms:
                # Find atom and stimulate
                for atom in self.atomspace.atoms.values():
                    if atom.name == atom_name:
                        self.attention.stimulate_atom(atom, 50.0)
        
        # Run attention cycle
        self.attention.run_attention_cycle(iterations=10)
        
        # Update task priorities based on attention
        self.coordinator.allocate_attention()
        
        stats = self.attention.get_statistics()
        self.logger.info(f"Attention optimized: {stats}")
    
    def get_top_important_atoms(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get most important atoms by attention"""
        top_atoms = self.attention.get_top_atoms(n)
        
        return [
            {
                'type': atom.atom_type.value,
                'name': atom.name,
                'attention': atom.attention_value,
                'truth_value': {
                    'strength': atom.truth_value.strength,
                    'confidence': atom.truth_value.confidence
                }
            }
            for atom in top_atoms
        ]
    
    def export_state(self, filepath: str):
        """Export workbench state to file"""
        state = {
            'atomspace': json.loads(self.atomspace.export_to_json()),
            'attention': self.attention.get_statistics(),
            'coordinator': self.coordinator.get_statistics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        self.logger.info(f"State exported to {filepath}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall workbench status"""
        return {
            'atomspace': {
                'num_atoms': len(self.atomspace),
                'num_models': len(self.atomspace.models)
            },
            'agents': self.coordinator.get_statistics(),
            'attention': self.attention.get_statistics(),
            'top_focus': [atom.name for atom in list(self.attention.attentional_focus)[:5]]
        }
    
    def __repr__(self):
        return f"WorkbenchOrchestrator(atoms={len(self.atomspace)}, agents={len(self.coordinator.agents)})"
