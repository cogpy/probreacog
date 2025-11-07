#!/usr/bin/env python3
"""
Example usage of OpenCog Multi-Agent Workbench

Demonstrates how to use the workbench for analyzing
psoriasis therapy models with autonomous agents.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from opencog_workbench import (
    WorkbenchOrchestrator,
    ModelAtomSpace,
    AgentRole
)


def main():
    print("=" * 70)
    print("OpenCog Multi-Agent Workbench for Mathematical Biology")
    print("=" * 70)
    print()
    
    # Initialize workbench
    print("Initializing workbench...")
    workbench = WorkbenchOrchestrator()
    print(f"✓ Workbench initialized: {workbench}")
    print()
    
    # Load psoriasis model
    print("Loading psoriasis therapy model...")
    model_file = "model/psoriasis/psoriasis.pdrh"
    model = workbench.load_pdrh_model(model_file, "psoriasis")
    print(f"✓ Model loaded: {model.name}")
    print(f"  Atoms in atomspace: {len(workbench.atomspace)}")
    print()
    
    # Show atomspace structure
    print("Atomspace structure:")
    print(f"  Models: {len(workbench.atomspace.models)}")
    print(f"  Parameters: {len(workbench.atomspace.get_atoms_by_type(workbench.atomspace.atoms[list(workbench.atomspace.atoms.keys())[0]].atom_type.__class__.PARAMETER))}")
    print()
    
    # Create analysis workflow
    print("Creating analysis workflow...")
    workflow_id = workbench.create_analysis_workflow("psoriasis", "comprehensive")
    print(f"✓ Workflow created: {workflow_id}")
    print()
    
    # Show workflow tasks
    workflow = workbench.coordinator.workflows.get(workflow_id)
    if workflow:
        print("Workflow tasks:")
        for i, task in enumerate(workflow, 1):
            print(f"  {i}. {task.task_type} (priority: {task.priority})")
            if task.dependencies:
                print(f"     Dependencies: {', '.join(task.dependencies)}")
        print()
    
    # Execute workflow
    print("Executing workflow...")
    results = workbench.execute_workflow(workflow_id)
    print(f"✓ Workflow executed")
    print(f"  Completed tasks: {results['completed']}/{results['total']}")
    print()
    
    # Show task results
    print("Task results:")
    for task_id, task_result in results['tasks'].items():
        status = task_result['status']
        print(f"  {task_id}: {status}")
    print()
    
    # Reason about goal
    print("Reasoning about remission goal...")
    reasoning = workbench.reason_about_goal("remission_365")
    if 'error' not in reasoning:
        prob = reasoning['reachability']['probability']
        conf = reasoning['reachability']['confidence']
        print(f"✓ Goal reachability:")
        print(f"  Probability: {prob:.3f}")
        print(f"  Confidence: {conf:.3f}")
        print()
        
        print(f"  Evidence considered ({len(reasoning['evidence'])} parameters):")
        for ev in reasoning['evidence'][:3]:  # Show first 3
            print(f"    - {ev['name']}: strength={ev['strength']:.3f}, conf={ev['confidence']:.3f}")
        print()
    
    # Optimize attention
    print("Optimizing attention allocation...")
    workbench.optimize_attention(focus_atoms=['remission_365', 'InA'])
    attention_stats = workbench.attention.get_statistics()
    print(f"✓ Attention optimized:")
    print(f"  Focus size: {attention_stats['focus_size']} atoms")
    print(f"  Mean STI: {attention_stats['mean_sti']:.2f}")
    print()
    
    # Show most important atoms
    print("Top important atoms by attention:")
    top_atoms = workbench.get_top_important_atoms(5)
    for i, atom in enumerate(top_atoms, 1):
        print(f"  {i}. {atom['type']}: {atom['name']}")
        print(f"     Attention: {atom['attention']:.2f}")
    print()
    
    # Show overall status
    print("Workbench status:")
    status = workbench.get_status()
    print(f"  Atomspace: {status['atomspace']['num_atoms']} atoms, {status['atomspace']['num_models']} models")
    print(f"  Agents: {status['agents']['num_agents']} registered")
    print(f"  Tasks: {status['agents']['num_tasks']} total")
    print(f"  Current focus: {', '.join(status['top_focus'][:3])}")
    print()
    
    # Export state
    output_file = "/tmp/workbench_state.json"
    print(f"Exporting state to {output_file}...")
    workbench.export_state(output_file)
    print(f"✓ State exported")
    print()
    
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
