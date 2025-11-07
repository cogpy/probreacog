"""
Unit tests for OpenCog Workbench

Tests the core components: AtomSpace, PLN, ECAN, Agents, Orchestrator
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from opencog_workbench.atomspace import (
    ModelAtomSpace, Atom, PDRHAtom, AtomType, TruthValue
)
from opencog_workbench.pln import PLNReasoner
from opencog_workbench.ecan import AttentionAllocation
from opencog_workbench.agents import (
    Agent, AgentCoordinator, SimulatorAgent, VerifierAgent,
    Task, AgentRole, TaskStatus
)
from opencog_workbench.orchestrator import WorkbenchOrchestrator


class TestAtomSpace(unittest.TestCase):
    """Test AtomSpace functionality"""
    
    def setUp(self):
        self.atomspace = ModelAtomSpace()
    
    def test_add_atom(self):
        """Test adding atoms to atomspace"""
        atom = Atom(
            atom_type=AtomType.CONCEPT,
            name="test_concept",
            truth_value=TruthValue(0.8, 0.9)
        )
        result = self.atomspace.add_atom(atom)
        self.assertEqual(result.name, "test_concept")
        self.assertEqual(len(self.atomspace), 1)
    
    def test_add_model(self):
        """Test adding PDRH model"""
        model = self.atomspace.add_model("test_model", "test.pdrh")
        self.assertEqual(model.name, "test_model")
        self.assertEqual(model.model_file, "test.pdrh")
        self.assertIn("test_model", self.atomspace.models)
    
    def test_add_parameter(self):
        """Test adding parameter with uncertainty"""
        param = self.atomspace.add_parameter(
            "test_param", 0.5, bounds=(0.0, 1.0), uncertainty=0.1
        )
        self.assertEqual(param.name, "test_param")
        self.assertEqual(param.metadata['value'], 0.5)
        self.assertAlmostEqual(param.truth_value.confidence, 0.9)
    
    def test_query(self):
        """Test pattern matching query"""
        self.atomspace.add_parameter("param1", 1.0)
        self.atomspace.add_parameter("param2", 2.0)
        
        results = self.atomspace.query({'type': AtomType.PARAMETER})
        self.assertEqual(len(results), 2)
    
    def test_truth_value_merge(self):
        """Test truth value merging"""
        tv1 = TruthValue(0.7, 0.8)
        tv2 = TruthValue(0.9, 0.6)
        
        merged = self.atomspace._merge_truth_values(tv1, tv2)
        self.assertGreater(merged.strength, 0.0)
        self.assertLess(merged.strength, 1.0)


class TestPLN(unittest.TestCase):
    """Test PLN reasoning"""
    
    def setUp(self):
        self.atomspace = ModelAtomSpace()
        self.reasoner = PLNReasoner(self.atomspace)
    
    def test_deduction(self):
        """Test deduction rule"""
        tv_ab = TruthValue(0.8, 0.9)
        tv_bc = TruthValue(0.7, 0.8)
        
        tv_ac = self.reasoner.deduction(tv_ab, tv_bc)
        self.assertAlmostEqual(tv_ac.strength, 0.8 * 0.7, places=2)
    
    def test_revision(self):
        """Test revision rule"""
        tv1 = TruthValue(0.6, 0.7)
        tv2 = TruthValue(0.8, 0.6)
        
        revised = self.reasoner.revision(tv1, tv2)
        # Should be between the two original strengths
        self.assertGreater(revised.strength, 0.6)
        self.assertLess(revised.strength, 0.8)
    
    def test_conjunction(self):
        """Test conjunction of truth values"""
        tvs = [TruthValue(0.9, 0.8), TruthValue(0.8, 0.9)]
        result = self.reasoner.conjunction(tvs)
        
        # Conjunction strength should be product
        self.assertAlmostEqual(result.strength, 0.9 * 0.8, places=2)
    
    def test_disjunction(self):
        """Test disjunction of truth values"""
        tvs = [TruthValue(0.5, 0.8), TruthValue(0.6, 0.9)]
        result = self.reasoner.disjunction(tvs)
        
        # Disjunction strength should be higher than either
        self.assertGreater(result.strength, 0.6)


class TestECAN(unittest.TestCase):
    """Test ECAN attention allocation"""
    
    def setUp(self):
        self.atomspace = ModelAtomSpace()
        self.attention = AttentionAllocation(self.atomspace, total_sti=1000.0)
    
    def test_initialize_attention(self):
        """Test attention initialization"""
        # Add some atoms
        for i in range(5):
            self.atomspace.add_atom(Atom(
                atom_type=AtomType.CONCEPT,
                name=f"concept_{i}"
            ))
        
        self.attention.initialize_attention()
        self.assertEqual(len(self.attention.atom_attention), 5)
    
    def test_stimulate_atom(self):
        """Test stimulating an atom"""
        atom = Atom(atom_type=AtomType.CONCEPT, name="test")
        self.atomspace.add_atom(atom)
        self.attention.initialize_attention()
        
        initial_sti = self.attention.atom_attention[
            self.attention._atom_key(atom)
        ].sti
        
        self.attention.stimulate_atom(atom, 100.0)
        
        new_sti = self.attention.atom_attention[
            self.attention._atom_key(atom)
        ].sti
        
        self.assertGreater(new_sti, initial_sti)
    
    def test_attention_diffusion(self):
        """Test attention diffusion"""
        atom1 = Atom(atom_type=AtomType.CONCEPT, name="atom1")
        atom2 = Atom(atom_type=AtomType.CONCEPT, name="atom2")
        
        # Create link
        link = Atom(
            atom_type=AtomType.LINK,
            name="link",
            outgoing=[atom1, atom2]
        )
        
        self.atomspace.add_atom(atom1)
        self.atomspace.add_atom(atom2)
        self.atomspace.add_atom(link)
        
        self.attention.initialize_attention()
        self.attention.stimulate_atom(atom1, 500.0)
        
        # Diffuse attention
        self.attention.diffuse_attention(decay_rate=0.2)
        
        # atom2 should have gained some attention
        atom2_sti = self.attention.atom_attention[
            self.attention._atom_key(atom2)
        ].sti
        self.assertGreater(atom2_sti, 0)


class TestAgents(unittest.TestCase):
    """Test multi-agent system"""
    
    def setUp(self):
        self.atomspace = ModelAtomSpace()
        self.coordinator = AgentCoordinator(self.atomspace)
    
    def test_agent_creation(self):
        """Test creating agents"""
        agent = SimulatorAgent("sim1", self.atomspace)
        self.assertEqual(agent.role, AgentRole.SIMULATOR)
        self.assertEqual(agent.agent_id, "sim1")
    
    def test_agent_registration(self):
        """Test registering agents with coordinator"""
        agent = SimulatorAgent("sim1", self.atomspace)
        self.coordinator.register_agent(agent)
        
        self.assertIn("sim1", self.coordinator.agents)
    
    def test_task_creation(self):
        """Test creating tasks"""
        task = self.coordinator.create_task(
            task_id="test_task",
            task_type="simulate",
            agent_role=AgentRole.SIMULATOR,
            parameters={'model': 'test.pdrh'},
            priority=0.8
        )
        
        self.assertEqual(task.task_id, "test_task")
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_task_submission(self):
        """Test submitting tasks to agents"""
        agent = SimulatorAgent("sim1", self.atomspace)
        self.coordinator.register_agent(agent)
        
        task = self.coordinator.create_task(
            task_id="test_task",
            task_type="simulate",
            agent_role=AgentRole.SIMULATOR,
            parameters={'model': 'test.pdrh'}
        )
        
        self.coordinator.submit_task(task)
        self.assertEqual(len(agent.task_queue), 1)
    
    def test_task_execution(self):
        """Test executing a task"""
        agent = SimulatorAgent("sim1", self.atomspace)
        
        task = Task(
            task_id="test_task",
            task_type="simulate",
            agent_role=AgentRole.SIMULATOR,
            parameters={
                'model_file': 'test.pdrh',
                'num_paths': 10
            }
        )
        
        result = agent.process_task(task)
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(result.result)


class TestOrchestrator(unittest.TestCase):
    """Test workbench orchestrator"""
    
    def setUp(self):
        self.workbench = WorkbenchOrchestrator()
    
    def test_initialization(self):
        """Test orchestrator initialization"""
        self.assertIsNotNone(self.workbench.atomspace)
        self.assertIsNotNone(self.workbench.reasoner)
        self.assertIsNotNone(self.workbench.attention)
        self.assertIsNotNone(self.workbench.coordinator)
    
    def test_load_model(self):
        """Test loading a model"""
        model = self.workbench.load_pdrh_model(
            "test.pdrh", "test_model"
        )
        self.assertEqual(model.name, "test_model")
        self.assertGreater(len(self.workbench.atomspace), 0)
    
    def test_workflow_creation(self):
        """Test creating analysis workflow"""
        self.workbench.load_pdrh_model("test.pdrh", "test_model")
        
        workflow_id = self.workbench.create_analysis_workflow("test_model")
        self.assertIn(workflow_id, self.workbench.coordinator.workflows)
    
    def test_get_status(self):
        """Test getting workbench status"""
        status = self.workbench.get_status()
        
        self.assertIn('atomspace', status)
        self.assertIn('agents', status)
        self.assertIn('attention', status)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAtomSpace))
    suite.addTests(loader.loadTestsFromTestCase(TestPLN))
    suite.addTests(loader.loadTestsFromTestCase(TestECAN))
    suite.addTests(loader.loadTestsFromTestCase(TestAgents))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
