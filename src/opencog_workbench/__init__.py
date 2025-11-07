"""
OpenCog Multi-Agent Orchestration Workbench for ProbReach

This module provides an autonomous multi-agent orchestration system for
mathematical biology models of hybrid systems with parametric uncertainty.

The workbench integrates OpenCog's cognitive architecture (AtomSpace, PLN, ECAN)
with ProbReach's formal verification and simulation tools.
"""

__version__ = "0.1.0"
__author__ = "ProbReaCog Team"

from .atomspace import ModelAtomSpace, PDRHAtom, Atom, AtomType, TruthValue
from .agents import Agent, AgentCoordinator, AgentRole, Task, TaskStatus
from .pln import PLNReasoner
from .ecan import AttentionAllocation
from .orchestrator import WorkbenchOrchestrator

__all__ = [
    'ModelAtomSpace',
    'PDRHAtom',
    'Atom',
    'AtomType',
    'TruthValue',
    'Agent',
    'AgentCoordinator',
    'AgentRole',
    'Task',
    'TaskStatus',
    'PLNReasoner',
    'AttentionAllocation',
    'WorkbenchOrchestrator',
]
