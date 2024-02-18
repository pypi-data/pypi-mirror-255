import json
import click
import re

def get_tests_and_nodes(manifest :dict) -> (dict, dict):
    """
    Get the tests and nodes that the tests depend on.
    """
    tests_with_data = {}
    nodes_with_tests = {}
    for _, node_data in manifest.get('nodes', {}).items():
        if node_data.get('resource_type') == 'test':
            tests_with_data[node_data.get('name')] = node_data
            
            # Get the models that the test depends on
            for node in node_data.get('depends_on', {}).get('nodes', []):
                nodes_with_tests.setdefault(node, []).append(node_data.get('name'))

    return tests_with_data, nodes_with_tests

def get_ascend_node_name(node_name :str) -> str:
    """
    Get the Ascend node name from the dbt node name.
    """
    return node_name.split('.')[-1].lower()

def get_dbt_node_type(node_name :str) -> str:
    """
    Get the dbt node type from the dbt node name.
    """
    return node_name.split('.')[0]

def get_dbt_node_name(nodes :list, node :str) -> str:
    """
    Get the dbt node name from the dbt node name.
    """
    return [node_str for node_str in nodes if node_str.split('.')[-1] == node][0]

def get_nodes_and_dependencies(manifest :dict, default_seed :str = None, node_match_regex :str = "*") -> (list, dict[str, list[str]]):    
    """
    Parse the manifest files and return a list of nodes in topological order and a dict of dependencies of each node.
    """
    # Extract source elements
    sources = []
    for node_name, _ in manifest['sources'].items():
        sources.append(node_name)

    # Extract model and seed dependencies
    dependencies = {}
    for node_name, node_data in manifest['nodes'].items():
        if (node_data['resource_type'] == 'model' and node_matches("model.", node_name, node_match_regex)) or node_data['resource_type'] == 'seed':
            # Check if 'depends_on' and 'nodes' keys exist
            if 'depends_on' in node_data and 'nodes' in node_data['depends_on']:
                dependencies[node_name] = node_data['depends_on']['nodes']
            else:
                dependencies[node_name] = []

    # Perform topological sort
    sorted_nodes = sort_topologically(dependencies)

    # Replace empty dependencies with default seed unless it is a source node
    for node in sorted_nodes:
        # If dependency is a source, add empty list
        if node in sources:
            dependencies[node] = []
        # If dependency is empty and node is a model, add default seed
        elif len(dependencies[node]) == 0 and node.split('.')[0] == 'model':
            dependencies[node] = [default_seed] if default_seed else []

    # return list of sorted nodes and dict of dependencies of each node
    return sorted_nodes, dependencies


def sort_topologically(graph):
    """
    Sort nodes in topological order.
    """
    visited = set()
    post_order = []
    temp_marked = set()

    def visit(node):
        if node in temp_marked:
            raise ValueError("Graph contains a cycle")
        if node not in visited:
            temp_marked.add(node)
            for neighbor in graph.get(node, []):
                visit(neighbor)
            temp_marked.remove(node)
            visited.add(node)
            post_order.append(node)

    for node in graph:
        visit(node)

    return post_order

@click.pass_context
def get_compiled_sql(ctx, node_str):
    """
    Get compiled SQL from manifest.
    """
    return ctx.obj['manifest']['nodes'][node_str]['compiled_code']

@click.pass_context
def get_description(ctx, node_str):
    """
    Get description from manifest.
    """
    return ctx.obj['manifest']['nodes'][node_str].get('description', '')

def node_matches(prefix :str, node_name :str, node_match_regex :str) -> bool:
    """
    Check if the node name matches the node match regex.
    """
    return node_match_regex == '*' or re.match(prefix + node_match_regex, node_name) is not None

@click.pass_context
def get_reduction_from_manifest(ctx, node_str :str) -> str:
    """
    Get reduction from manifest JSON. Values are ['no-reduction', 'full-reduction']. The default is 'no-reduction'
        Will be added to dbt_project.yml as a custom config parameter:
        ```
        models:
            jaffle_shop:
                weather-models-dbt:
                    stg_weather_data:
                        ascend-partition-reduction: full-reduction
        ```
    """
    return ctx.obj['manifest']['nodes'][node_str].get('config', {}).get('ascend-partition-reduction', 'no-reduction')