# OpenCog Integration Documentation

This document describes the OpenCog multi-agent orchestration workbench integrated into ProbReach.

## Overview

The OpenCog workbench provides an autonomous multi-agent system for analyzing mathematical biology models of hybrid systems with parametric uncertainty. It integrates three core OpenCog technologies:

1. **AtomSpace** - Knowledge representation using hypergraphs
2. **PLN** - Probabilistic Logic Networks for reasoning
3. **ECAN** - Economic Attention Network for resource allocation

## Directory Structure

```
src/opencog_workbench/
├── __init__.py           # Module exports
├── atomspace.py          # AtomSpace knowledge representation
├── agents.py             # Multi-agent system
├── pln.py                # Probabilistic reasoning engine
├── ecan.py               # Attention allocation mechanism
├── orchestrator.py       # Main workbench orchestrator
├── example_usage.py      # Example usage script
├── test_workbench.py     # Unit tests
└── README.md             # Full documentation
```

## Quick Start

### 1. Run Example

```bash
cd src/opencog_workbench
python example_usage.py
```

### 2. Run Tests

```bash
cd src/opencog_workbench
python test_workbench.py
```

### 3. Use in Your Code

```python
from opencog_workbench import WorkbenchOrchestrator

# Initialize
workbench = WorkbenchOrchestrator()

# Load model
model = workbench.load_pdrh_model("model/psoriasis/psoriasis.pdrh", "psoriasis")

# Create and execute workflow
workflow_id = workbench.create_analysis_workflow("psoriasis")
results = workbench.execute_workflow(workflow_id)

# Reason about goals
reasoning = workbench.reason_about_goal("remission_365")
print(f"Reachability: {reasoning['reachability']['probability']:.3f}")
```

## Architecture

The workbench implements a multi-layered cognitive architecture:

### Layer 1: Knowledge Representation (AtomSpace)

- **Atoms**: Nodes representing concepts, parameters, models, goals
- **Links**: Relationships between atoms (inheritance, evaluation, etc.)
- **Truth Values**: Probabilistic values (strength, confidence)
- **Attention Values**: Resource allocation priorities

### Layer 2: Reasoning (PLN)

- **Deduction**: A→B, B→C ⇒ A→C
- **Induction**: A→B ⇒ B→A (with reduced confidence)
- **Abduction**: A→C, B→C ⇒ A→B (hypothesis generation)
- **Revision**: Combine multiple evidence sources
- **Uncertainty Propagation**: Track parameter uncertainty through model

### Layer 3: Attention (ECAN)

- **STI (Short-Term Importance)**: Current task priority
- **LTI (Long-Term Importance)**: Historical importance
- **Attention Diffusion**: Spread activation through network
- **Attentional Focus**: Set of high-priority atoms
- **Rent Collection**: Decay mechanism for forgetting

### Layer 4: Agents

- **SimulatorAgent**: Execute simulations
- **VerifierAgent**: Perform formal verification
- **AnalyzerAgent**: Analyze results
- **Coordinator**: Manage workflows and task dependencies

## Use Cases

### 1. Psoriasis Therapy Optimization

```python
# Load psoriasis model
model = workbench.load_pdrh_model("model/psoriasis/psoriasis.pdrh", "psoriasis")

# Create comprehensive analysis
workflow_id = workbench.create_analysis_workflow("psoriasis", "therapy_opt")
results = workbench.execute_workflow(workflow_id)

# Focus on treatment parameter
workbench.optimize_attention(focus_atoms=['InA', 'remission_365'])

# Reason about reachability
reasoning = workbench.reason_about_goal("remission_365")
```

### 2. Parameter Sensitivity Analysis

```python
# Load model
model = workbench.load_pdrh_model("model/psoriasis/psoriasis.pdrh", "psoriasis")

# Create custom sensitivity analysis task
from opencog_workbench import AgentRole

task = workbench.coordinator.create_task(
    task_id="sensitivity",
    task_type="analyze",
    agent_role=AgentRole.ANALYZER,
    parameters={
        'analysis_type': 'sensitivity',
        'parameters': ['gamma1d', 'k1asd', 'beta1d', 'InA']
    },
    priority=0.9
)

workbench.coordinator.submit_task(task)
```

### 3. Multi-Model Comparison

```python
# Load multiple models
models = {
    'psoriasis': 'model/psoriasis/psoriasis.pdrh',
    'insulin': 'model/insulin-infusion/insulin.pdrh',
    'cancer': 'model/prostate-cancer/cancer.pdrh'
}

for name, path in models.items():
    workbench.load_pdrh_model(path, name)

# Compare reachability across models
results = {}
for model_name in models.keys():
    workflow_id = workbench.create_analysis_workflow(model_name)
    results[model_name] = workbench.execute_workflow(workflow_id)
```

## Integration with ProbReach

The workbench acts as a high-level orchestration layer on top of ProbReach tools:

```
┌─────────────────────────────────────────┐
│   OpenCog Workbench (Python)            │
│   - AtomSpace knowledge graph           │
│   - PLN reasoning                       │
│   - ECAN attention                      │
│   - Multi-agent coordination            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│   ProbReach Tools (C++)                 │
│   - simulator                           │
│   - formal_verifier                     │
│   - mc_verifier                         │
│   - qmc_verifier                        │
│   - gp                                  │
│   - pid_optimiser                       │
└─────────────────────────────────────────┘
```

Agents in the workbench wrap ProbReach executables and parse their output.

## Extending the Workbench

### Add Custom Agent

```python
from opencog_workbench.agents import Agent, AgentRole, Task, TaskStatus

class CustomAgent(Agent):
    def __init__(self, agent_id: str, atomspace):
        super().__init__(agent_id, AgentRole.ANALYZER, atomspace)
        self.capabilities = {'custom_analysis': True}
    
    def process_task(self, task: Task) -> Task:
        # Custom logic
        task.status = TaskStatus.COMPLETED
        task.result = {'custom': 'result'}
        return task

# Register
workbench.coordinator.register_agent(CustomAgent("custom_1", workbench.atomspace))
```

### Add Custom PLN Rule

```python
from opencog_workbench.pln import PLNReasoner, TruthValue

class ExtendedReasoner(PLNReasoner):
    def custom_inference(self, tv1: TruthValue, tv2: TruthValue) -> TruthValue:
        # Custom inference logic
        strength = (tv1.strength + tv2.strength) / 2.0
        confidence = min(tv1.confidence, tv2.confidence)
        return TruthValue(strength, confidence)

# Use custom reasoner
workbench.reasoner = ExtendedReasoner(workbench.atomspace)
```

## API Documentation

See [README.md](README.md) for complete API documentation.

## Testing

The workbench includes comprehensive unit tests:

```bash
python test_workbench.py
```

Tests cover:
- AtomSpace operations (5 tests)
- PLN reasoning (4 tests)
- ECAN attention (3 tests)
- Agent system (5 tests)
- Orchestrator (4 tests)

## Performance

- **AtomSpace**: O(1) atom lookup, O(n) pattern matching
- **PLN**: O(1) per inference rule
- **ECAN**: O(n) attention diffusion per cycle
- **Agents**: Sequential execution (parallel in future)

## Future Enhancements

- [ ] Parallel agent execution using multiprocessing
- [ ] Distributed atomspace across machines
- [ ] Real-time model learning from data
- [ ] Interactive visualization dashboard
- [ ] GPU-accelerated attention computation
- [ ] Integration with OpenCog Hyperon
- [ ] Support for additional solvers (Z3, MathSAT)

## References

- [OpenCog Framework](https://opencog.org/)
- [AtomSpace Documentation](https://wiki.opencog.org/w/AtomSpace)
- [PLN Book](https://github.com/opencog/pln)
- [ECAN](https://wiki.opencog.org/w/ECAN)
- [ProbReach](../../README.md)

## Support

For issues and questions:
- Repository: https://github.com/cogpy/probreacog
- Issues: https://github.com/cogpy/probreacog/issues

---

*Integrating cognitive architectures with formal verification for mathematical biology*
