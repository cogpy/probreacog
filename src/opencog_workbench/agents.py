"""
Multi-Agent System for Model Analysis

Implements autonomous agents that can analyze, simulate, and optimize
PDRH models through coordinated actions.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import json

from .atomspace import ModelAtomSpace, Atom, TruthValue


class AgentRole(Enum):
    """Roles that agents can play in the workbench"""
    SIMULATOR = "simulator"
    VERIFIER = "formal_verifier"
    MC_VERIFIER = "mc_verifier"
    OPTIMIZER = "optimizer"
    ANALYZER = "analyzer"
    COORDINATOR = "coordinator"
    REASONER = "reasoner"


class TaskStatus(Enum):
    """Status of agent tasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task to be executed by an agent"""
    task_id: str
    task_type: str
    agent_role: AgentRole
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    priority: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'agent_role': self.agent_role.value,
            'parameters': self.parameters,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'dependencies': self.dependencies,
            'priority': self.priority
        }


@dataclass
class Message:
    """Message exchanged between agents"""
    sender: str
    receiver: str
    content: Dict[str, Any]
    message_type: str
    timestamp: float = 0.0


class Agent(ABC):
    """
    Base class for autonomous agents
    
    Each agent has a specific role and can process tasks,
    communicate with other agents, and update the atomspace.
    """
    
    def __init__(self, agent_id: str, role: AgentRole, atomspace: ModelAtomSpace):
        self.agent_id = agent_id
        self.role = role
        self.atomspace = atomspace
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        self.task_queue: List[Task] = []
        self.message_queue: List[Message] = []
        self.capabilities: Dict[str, Any] = {}
        
    @abstractmethod
    def process_task(self, task: Task) -> Task:
        """Process a task and return updated task with results"""
        pass
    
    def can_handle(self, task: Task) -> bool:
        """Check if agent can handle this task"""
        return task.agent_role == self.role
    
    def add_task(self, task: Task):
        """Add task to agent's queue"""
        self.task_queue.append(task)
        self.logger.info(f"Task {task.task_id} added to queue")
    
    def get_next_task(self) -> Optional[Task]:
        """Get next task from queue (highest priority first)"""
        if not self.task_queue:
            return None
        
        # Sort by priority (higher priority first)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        return self.task_queue.pop(0)
    
    def send_message(self, receiver: str, content: Dict[str, Any], 
                    message_type: str = "info"):
        """Send message to another agent"""
        message = Message(
            sender=self.agent_id,
            receiver=receiver,
            content=content,
            message_type=message_type
        )
        # In real implementation, this would go through message bus
        self.logger.info(f"Sending {message_type} message to {receiver}")
        return message
    
    def receive_message(self, message: Message):
        """Receive message from another agent"""
        self.message_queue.append(message)
        self.logger.info(f"Received {message.message_type} from {message.sender}")
    
    def update_atomspace(self, atom: Atom):
        """Update the shared atomspace"""
        self.atomspace.add_atom(atom)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.agent_id}, role={self.role.value})"


class SimulatorAgent(Agent):
    """Agent responsible for simulating PDRH models"""
    
    def __init__(self, agent_id: str, atomspace: ModelAtomSpace):
        super().__init__(agent_id, AgentRole.SIMULATOR, atomspace)
        self.capabilities = {
            'simulate': True,
            'trajectory_generation': True,
            'visualization': True
        }
    
    def process_task(self, task: Task) -> Task:
        """Execute simulation task"""
        self.logger.info(f"Processing simulation task {task.task_id}")
        
        try:
            task.status = TaskStatus.RUNNING
            
            # Extract parameters
            model_file = task.parameters.get('model_file')
            num_paths = task.parameters.get('num_paths', 1)
            depth = task.parameters.get('depth', 100)
            
            # In real implementation, this would call ProbReach simulator
            result = {
                'model': model_file,
                'num_paths': num_paths,
                'trajectories': [],  # Would contain actual simulation data
                'success': True
            }
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            self.logger.info(f"Simulation task {task.task_id} completed")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.logger.error(f"Simulation task {task.task_id} failed: {e}")
        
        return task


class VerifierAgent(Agent):
    """Agent responsible for formal verification"""
    
    def __init__(self, agent_id: str, atomspace: ModelAtomSpace):
        super().__init__(agent_id, AgentRole.VERIFIER, atomspace)
        self.capabilities = {
            'formal_verification': True,
            'reachability_analysis': True,
            'probability_bounds': True
        }
    
    def process_task(self, task: Task) -> Task:
        """Execute verification task"""
        self.logger.info(f"Processing verification task {task.task_id}")
        
        try:
            task.status = TaskStatus.RUNNING
            
            model_file = task.parameters.get('model_file')
            goal = task.parameters.get('goal')
            precision = task.parameters.get('precision', 0.01)
            
            # In real implementation, this would call dReal/formal verifier
            result = {
                'model': model_file,
                'goal': goal,
                'reachable': True,
                'probability_bounds': (0.7, 0.9),
                'precision': precision
            }
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        return task


class AnalyzerAgent(Agent):
    """Agent for analyzing model properties and results"""
    
    def __init__(self, agent_id: str, atomspace: ModelAtomSpace):
        super().__init__(agent_id, AgentRole.ANALYZER, atomspace)
        self.capabilities = {
            'sensitivity_analysis': True,
            'parameter_analysis': True,
            'result_interpretation': True
        }
    
    def process_task(self, task: Task) -> Task:
        """Execute analysis task"""
        self.logger.info(f"Processing analysis task {task.task_id}")
        
        try:
            task.status = TaskStatus.RUNNING
            
            analysis_type = task.parameters.get('analysis_type')
            data = task.parameters.get('data')
            
            result = {
                'analysis_type': analysis_type,
                'insights': [],
                'recommendations': []
            }
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        return task


class AgentCoordinator:
    """
    Coordinates multiple agents to accomplish complex workflows
    
    Uses ECAN-inspired attention allocation to prioritize tasks
    and PLN-inspired reasoning to plan agent coordination.
    """
    
    def __init__(self, atomspace: ModelAtomSpace):
        self.atomspace = atomspace
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.workflows: Dict[str, List[Task]] = {}
        self.logger = logging.getLogger("AgentCoordinator")
        
    def register_agent(self, agent: Agent):
        """Register an agent with the coordinator"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent}")
    
    def create_task(self, task_id: str, task_type: str, agent_role: AgentRole,
                   parameters: Dict[str, Any], priority: float = 0.5,
                   dependencies: List[str] = None) -> Task:
        """Create a new task"""
        task = Task(
            task_id=task_id,
            task_type=task_type,
            agent_role=agent_role,
            parameters=parameters,
            priority=priority,
            dependencies=dependencies or []
        )
        self.tasks[task_id] = task
        return task
    
    def submit_task(self, task: Task):
        """Submit task to appropriate agent"""
        for agent in self.agents.values():
            if agent.can_handle(task):
                agent.add_task(task)
                self.logger.info(f"Task {task.task_id} assigned to {agent.agent_id}")
                return
        
        self.logger.warning(f"No agent available for task {task.task_id}")
    
    def create_workflow(self, workflow_id: str, tasks: List[Task]):
        """Create a workflow consisting of multiple tasks"""
        self.workflows[workflow_id] = tasks
        self.logger.info(f"Created workflow {workflow_id} with {len(tasks)} tasks")
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute all tasks in a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        tasks = self.workflows[workflow_id]
        results = {}
        
        # Execute tasks respecting dependencies
        completed = set()
        
        for task in tasks:
            # Wait for dependencies
            deps_met = all(dep in completed for dep in task.dependencies)
            if not deps_met:
                self.logger.warning(f"Dependencies not met for {task.task_id}")
                continue
            
            # Find agent and execute
            for agent in self.agents.values():
                if agent.can_handle(task):
                    result_task = agent.process_task(task)
                    results[task.task_id] = result_task.to_dict()
                    if result_task.status == TaskStatus.COMPLETED:
                        completed.add(task.task_id)
                    break
        
        return {
            'workflow_id': workflow_id,
            'tasks': results,
            'completed': len(completed),
            'total': len(tasks)
        }
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a task"""
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    def allocate_attention(self):
        """
        Allocate attention to tasks based on importance
        
        Uses ECAN-inspired attention allocation mechanism
        """
        all_tasks = []
        for agent in self.agents.values():
            all_tasks.extend(agent.task_queue)
        
        if not all_tasks:
            return
        
        # Update priorities based on various factors
        for task in all_tasks:
            # Increase priority for tasks with dependencies completed
            deps_completed = sum(1 for dep in task.dependencies 
                               if self.tasks.get(dep, Task('', '', AgentRole.SIMULATOR, {})).status == TaskStatus.COMPLETED)
            task.priority += 0.1 * deps_completed
            
            # Increase priority for verification tasks
            if task.agent_role == AgentRole.VERIFIER:
                task.priority += 0.2
        
        self.logger.info(f"Attention allocated to {len(all_tasks)} tasks")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        return {
            'num_agents': len(self.agents),
            'num_tasks': len(self.tasks),
            'num_workflows': len(self.workflows),
            'agents': [
                {
                    'id': agent.agent_id,
                    'role': agent.role.value,
                    'queue_size': len(agent.task_queue)
                }
                for agent in self.agents.values()
            ]
        }
    
    def __repr__(self):
        return f"AgentCoordinator(agents={len(self.agents)}, tasks={len(self.tasks)})"
