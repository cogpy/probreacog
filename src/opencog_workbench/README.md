# OpenCog Multi-Agent Orchestration Workbench

An autonomous multi-agent orchestration system for mathematical biology models of hybrid systems with parametric uncertainty, integrating OpenCog's cognitive architecture with ProbReach's formal verification tools.

## Overview

This workbench provides a unified framework that combines:

- **AtomSpace**: OpenCog-style knowledge representation for PDRH models
- **PLN (Probabilistic Logic Networks)**: Reasoning about parametric uncertainty and reachability
- **ECAN (Economic Attention Network)**: Intelligent task prioritization and resource allocation
- **Multi-Agent System**: Autonomous agents for simulation, verification, and analysis
- **Orchestrator**: High-level coordination of complex workflows

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Workbench Orchestrator                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  AtomSpace   │  │     PLN      │  │     ECAN     │       │
│  │ Knowledge    │  │  Reasoning   │  │  Attention   │       │
│  │   Graph      │  │   Engine     │  │  Allocation  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │          Agent Coordinator                          │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │     │
│  │  │Simulator │ │ Verifier │ │ Analyzer │  ...       │     │
│  │  │  Agent   │ │  Agent   │ │  Agent   │            │     │
│  │  └──────────┘ └──────────┘ └──────────┘            │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │     ProbReach Tools (C++)              │
        │  ┌──────────┐ ┌───────────┐           │
        │  │Simulator │ │  Verifier │  ...      │
        │  └──────────┘ └───────────┘           │
        └───────────────────────────────────────┘
```

## Key Features

### 1. AtomSpace Knowledge Representation

- **Hypergraph-based**: Represents models, modes, parameters, flows, and goals as atoms
- **Truth Values**: Probabilistic truth values for uncertainty representation
- **Pattern Matching**: Query capabilities for knowledge discovery
- **Metadata**: Extensible metadata for domain-specific information

### 2. PLN Reasoning

- **Inference Rules**: Deduction, induction, abduction, revision
- **Uncertainty Propagation**: Track parameter uncertainty through model
- **Reachability Analysis**: Reason about goal satisfaction probability
- **Backward/Forward Chaining**: Strategic inference planning

### 3. ECAN Attention Allocation

- **Short-Term Importance (STI)**: Dynamic task prioritization
- **Long-Term Importance (LTI)**: Learning from usage patterns
- **Attention Diffusion**: Spread activation through knowledge graph
- **Attentional Focus**: Manage computational resources efficiently

### 4. Multi-Agent System

- **Autonomous Agents**: Self-contained agents with specific roles
- **Agent Roles**:
  - **Simulator**: Execute simulations, generate trajectories
  - **Verifier**: Perform formal verification, compute probability bounds
  - **Analyzer**: Analyze results, sensitivity analysis
  - **Optimizer**: Parameter optimization, therapy design
- **Coordination**: Workflow management with dependency resolution
- **Communication**: Inter-agent message passing

## Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# ProbReach dependencies (for integration)
sudo apt-get install cmake build-essential bison flex libgsl-dev
```

### Setup

```bash
# Clone repository
git clone https://github.com/cogpy/probreacog.git
cd probreacog

# Python path setup (for development)
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## Quick Start

### Basic Usage

```python
from opencog_workbench import WorkbenchOrchestrator

# Initialize workbench
workbench = WorkbenchOrchestrator()

# Load PDRH model
model = workbench.load_pdrh_model(
    "model/psoriasis/psoriasis.pdrh",
    "psoriasis"
)

# Create analysis workflow
workflow_id = workbench.create_analysis_workflow("psoriasis")

# Execute workflow
results = workbench.execute_workflow(workflow_id)

# Reason about goals
reasoning = workbench.reason_about_goal("remission_365")
print(f"Reachability: {reasoning['reachability']['probability']:.3f}")

# Optimize attention
workbench.optimize_attention(focus_atoms=['remission_365', 'InA'])

# Get important atoms
top_atoms = workbench.get_top_important_atoms(10)
```

### Example Script

```bash
cd src/opencog_workbench
python example_usage.py
```

## API Reference

### WorkbenchOrchestrator

Main interface for the workbench.

```python
class WorkbenchOrchestrator:
    def __init__(self, log_level=logging.INFO)
    def load_pdrh_model(self, model_file: str, model_name: str) -> PDRHAtom
    def create_analysis_workflow(self, model_name: str, workflow_name: str = "default") -> str
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]
    def reason_about_goal(self, goal_name: str) -> Dict[str, Any]
    def optimize_attention(self, focus_atoms: Optional[List[str]] = None)
    def get_top_important_atoms(self, n: int = 10) -> List[Dict[str, Any]]
    def export_state(self, filepath: str)
    def get_status(self) -> Dict[str, Any]
```

### ModelAtomSpace

Knowledge graph for PDRH models.

```python
class ModelAtomSpace:
    def add_atom(self, atom: Atom) -> Atom
    def add_model(self, model_name: str, model_file: str) -> PDRHAtom
    def add_mode(self, model_name: str, mode_id: int, mode_name: str) -> PDRHAtom
    def add_parameter(self, name: str, value: float, bounds: tuple, uncertainty: float) -> PDRHAtom
    def add_goal(self, goal_name: str, condition: str, probability: float) -> PDRHAtom
    def get_atom(self, atom_type: AtomType, name: str) -> Optional[Atom]
    def query(self, pattern: Dict[str, Any]) -> List[Atom]
```

### PLNReasoner

Probabilistic reasoning engine.

```python
class PLNReasoner:
    def deduction(self, tv_ab: TruthValue, tv_bc: TruthValue) -> TruthValue
    def revision(self, tv1: TruthValue, tv2: TruthValue) -> TruthValue
    def conjunction(self, tv_list: List[TruthValue]) -> TruthValue
    def disjunction(self, tv_list: List[TruthValue]) -> TruthValue
    def propagate_uncertainty(self, parameter_name: str, operation: str) -> TruthValue
    def reason_about_reachability(self, goal_name: str, evidence: List[Tuple[str, TruthValue]]) -> TruthValue
    def backward_chain(self, goal: Atom, max_depth: int) -> List[Atom]
    def forward_chain(self, premises: List[Atom], max_steps: int) -> List[Atom]
```

### AttentionAllocation

ECAN-based resource management.

```python
class AttentionAllocation:
    def initialize_attention(self)
    def stimulate_atom(self, atom: Atom, amount: float)
    def diffuse_attention(self, decay_rate: float)
    def update_attentional_focus(self)
    def focus_on_goal(self, goal_atom: Atom, intensity: float)
    def get_top_atoms(self, n: int, atom_type: Optional[AtomType]) -> List[Atom]
    def run_attention_cycle(self, iterations: int)
```

### AgentCoordinator

Multi-agent coordination.

```python
class AgentCoordinator:
    def register_agent(self, agent: Agent)
    def create_task(self, task_id: str, task_type: str, agent_role: AgentRole, parameters: Dict) -> Task
    def submit_task(self, task: Task)
    def create_workflow(self, workflow_id: str, tasks: List[Task])
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]
    def allocate_attention(self)
```

## Testing

```bash
# Run unit tests
cd src/opencog_workbench
python test_workbench.py

# Expected output:
# test_add_atom ... ok
# test_deduction ... ok
# test_stimulate_atom ... ok
# test_agent_creation ... ok
# test_initialization ... ok
# ...
# Ran 20 tests in 0.XXXs
# OK
```

## Use Cases

### 1. Psoriasis Therapy Optimization

```python
# Load psoriasis model
model = workbench.load_pdrh_model("model/psoriasis/psoriasis.pdrh", "psoriasis")

# Analyze treatment efficacy
workflow_id = workbench.create_analysis_workflow("psoriasis", "therapy_optimization")
results = workbench.execute_workflow(workflow_id)

# Reason about remission
reasoning = workbench.reason_about_goal("remission_365")
```

### 2. Parameter Sensitivity Analysis

```python
# Focus attention on key parameters
workbench.optimize_attention(focus_atoms=['gamma1d', 'k1asd', 'beta1d', 'InA'])

# Analyze parameter impact
analyzer_task = workbench.coordinator.create_task(
    task_id="sensitivity",
    task_type="analyze",
    agent_role=AgentRole.ANALYZER,
    parameters={'analysis_type': 'sensitivity', 'parameters': ['InA', 'gamma1d']}
)
```

### 3. Multi-Model Comparison

```python
# Load multiple models
models = ['psoriasis', 'insulin-infusion', 'prostate-cancer']
for model_name in models:
    workbench.load_pdrh_model(f"model/{model_name}/{model_name}.pdrh", model_name)

# Compare reachability across models
for model_name in models:
    workflow = workbench.create_analysis_workflow(model_name)
    results = workbench.execute_workflow(workflow)
```

## Integration with ProbReach

The workbench integrates with existing ProbReach tools:

```python
# Agents wrap ProbReach executables
class SimulatorAgent:
    def process_task(self, task):
        # Calls: simulator <options> model.pdrh
        # Parses JSON output
        pass

class VerifierAgent:
    def process_task(self, task):
        # Calls: formal_verifier <options> model.pdrh
        # Extracts probability bounds
        pass
```

## Extending the Workbench

### Adding Custom Agents

```python
from opencog_workbench.agents import Agent, AgentRole

class CustomAgent(Agent):
    def __init__(self, agent_id: str, atomspace: ModelAtomSpace):
        super().__init__(agent_id, AgentRole.ANALYZER, atomspace)
        
    def process_task(self, task: Task) -> Task:
        # Custom task processing logic
        task.status = TaskStatus.COMPLETED
        task.result = {...}
        return task

# Register with coordinator
custom_agent = CustomAgent("custom_1", workbench.atomspace)
workbench.coordinator.register_agent(custom_agent)
```

### Adding Custom Inference Rules

```python
from opencog_workbench.pln import PLNReasoner

class ExtendedReasoner(PLNReasoner):
    def custom_inference(self, premises):
        # Custom inference logic
        pass
```

## Performance Considerations

- **AtomSpace**: O(1) atom lookup, O(n) pattern matching
- **Attention**: Configurable STI budget, adjustable diffusion rates
- **Agents**: Parallel task execution (future enhancement)
- **Workflows**: Dependency-based scheduling

## Roadmap

- [ ] Parallel agent execution
- [ ] Distributed atomspace (across machines)
- [ ] Integration with OpenCog Hyperon
- [ ] Real-time model learning from data
- [ ] Interactive visualization dashboard
- [ ] GPU acceleration for attention computation
- [ ] Integration with additional solvers (Z3, MathSAT)

## References

### OpenCog Framework
- [OpenCog AtomSpace](https://wiki.opencog.org/w/AtomSpace)
- [PLN Book](https://github.com/opencog/pln)
- [ECAN](https://wiki.opencog.org/w/ECAN)

### ProbReach
- [ProbReach Documentation](../../doc/)
- [Formal Verifier](../../doc/formal_verifier/README.md)
- [Simulator](../../doc/simulator/README.md)

### Mathematical Biology
- Zhang et al. (2012) - Psoriasis therapy model
- Hybrid Systems in Systems Biology

## Contributing

Contributions welcome! Areas of interest:
- Additional agent types
- New PLN inference rules
- Performance optimizations
- Documentation improvements
- Test coverage

## License

Same as parent ProbReach project (see [LICENSE](../../LICENSE))

## Contact

- Repository: https://github.com/cogpy/probreacog
- Issues: https://github.com/cogpy/probreacog/issues

---

*Part of the CogPy/ProbReaCog project - Integrating cognitive architectures with formal verification for mathematical biology*
