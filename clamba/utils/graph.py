"""
Graph utilities for dependency analysis
"""

from typing import Dict, List, Set


def has_cycles(graph: Dict[str, List[str]]) -> bool:
    """
    Check if a directed graph has cycles using DFS
    
    Args:
        graph: Dictionary mapping nodes to their dependencies
        
    Returns:
        True if cycles are detected
    """
    def dfs(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    visited = set()
    for node in graph:
        if node not in visited:
            if dfs(node, visited, set()):
                return True
    return False


def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """
    Perform topological sort on a directed acyclic graph
    
    Args:
        graph: Dictionary mapping nodes to their dependencies
        
    Returns:
        List of nodes in topological order
        
    Raises:
        ValueError: If graph has cycles
    """
    if has_cycles(graph):
        raise ValueError("Cannot perform topological sort on graph with cycles")
    
    # Calculate in-degrees
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for dep in graph[node]:
            if dep in in_degree:
                in_degree[dep] += 1
    
    # Initialize queue with nodes having no dependencies
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        # Update in-degrees of dependent nodes
        for other_node, deps in graph.items():
            if node in deps:
                in_degree[other_node] -= 1
                if in_degree[other_node] == 0:
                    queue.append(other_node)
    
    return result


def find_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    Find all cycles in a directed graph
    
    Args:
        graph: Dictionary mapping nodes to their dependencies
        
    Returns:
        List of cycles (each cycle is a list of nodes)
    """
    cycles = []
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node: str) -> None:
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return
        
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            dfs(neighbor)
        
        rec_stack.remove(node)
        path.pop()
    
    for node in graph:
        if node not in visited:
            dfs(node)
    
    return cycles


def remove_cycles(graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Remove cycles from a graph by removing minimal edges
    
    Args:
        graph: Dictionary mapping nodes to their dependencies
        
    Returns:
        Graph with cycles removed
    """
    clean_graph = {node: [] for node in graph}
    
    # Add edges one by one, checking for cycles
    for node, deps in graph.items():
        for dep in deps:
            # Create temporary graph with this edge
            temp_graph = {k: v.copy() for k, v in clean_graph.items()}
            temp_graph[node].append(dep)
            
            # If no cycle is created, keep the edge
            if not has_cycles(temp_graph):
                clean_graph[node].append(dep)
    
    return clean_graph