from ascend.sdk import definitions
from ascend.sdk.applier import DataflowApplier
from ascend.sdk.client import Client

from . import manifest_utils as mu
from . import transform_utils as tu


# This is currently only handling models, sources and seeds
def show_cmd(ctx, **kwargs):
    """
    Load and parse manifest JSON file and print the dependencies of dbt models.
    """

    nodes, dependencies = mu.get_nodes_and_dependencies(manifest=ctx.obj['manifest'], node_match_regex=ctx.params['model_selector'])

    # Print nodes in topological order
    for node in nodes:
        print(f"\nNode: {node}. Depends on:")
        for dependency in dependencies[node]:
            print(f"  -> {dependency}")

def merge_cmd(ctx, **kwargs):
    """
    Merge dbt models into an Ascend dataflow.
    """
    # Create Ascend Client
    client = Client(ctx.params['hostname'])

    # Get existing nodes in dataflow
    existing_nodes = client.list_dataflow_components(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], deep=True).data
    existing_node_ids = [node.id for node in existing_nodes]

    nodes, dependencies = mu.get_nodes_and_dependencies(manifest=ctx.obj['manifest'], default_seed=existing_node_ids[0] if ctx.params['default_seed'] is None else ctx.params['default_seed'], node_match_regex=ctx.params['model_selector'])

    # Ensure seed nodes present in the manifest are present in the dataflow. Exit if not.
    for node_str in nodes:
        if mu.get_dbt_node_type(node_str) in ['seed', 'source']:
            node = mu.get_ascend_node_name(node_str)
            if node not in existing_node_ids:
                print(f"Seed node {node} is not present in the dataflow. Please add it manually and try again.")
                exit(1)

    # For every "model" node create a component
    components = []
    for node_str in nodes:

        # Skip if node is not a model
        if mu.get_dbt_node_type(node_str) != 'model':
            continue

        node = mu.get_ascend_node_name(node_str)
        # Create component
        component = tu.create_transform(
            id=node, 
            sql=mu.get_compiled_sql(node_str=node_str), 
            inputs=dependencies[node_str],
            description=mu.get_description(node_str=node_str),
            language=ctx.params['language'],
            reduction=mu.get_reduction_from_manifest(node_str=node_str),
        )
        # Add component to list of existing nodes
        components.append(component)

    # Get dataflow definition
    dataflow_def = client.get_dataflow(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow']).data

    # Perform a non-deleting append
    applier = DataflowApplier(client)
    applier.apply(data_service_id=ctx.params['data_service'], dataflow=definitions.Dataflow(id=dataflow_def.id, name=dataflow_def.name, components=components), delete=False, dry_run=False)

def delete_cmd(ctx, **kwargs):
    """
    Delete dbt models from Ascend dataflow.
    """
    # Create Ascend Client
    client = Client(ctx.params['hostname'])

    nodes, _ = mu.get_nodes_and_dependencies(manifest=ctx.obj['manifest'], node_match_regex=ctx.params['model_selector'])

    # Remove all nodes from the list of existing nodes in reverse order
    node_ids = [mu.get_ascend_node_name(node) for node in reversed(nodes) if mu.get_dbt_node_type(node) == 'model']
    for node in node_ids:
        print(f"Deleting transform {node}")
        try:
            client.delete_transform(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], id=node)
        except Exception as e:
            print(f"Could not delete transform {node}. Error: {e.reason}")

def validate_cmd(ctx, **kwargs):
    """
    Validate the seeds are present in the dataflow.
    """
    # Create Ascend Client
    client = Client(ctx.params['hostname'])

    nodes, _ = mu.get_nodes_and_dependencies(manifest=ctx.obj['manifest'], node_match_regex=ctx.params['model_selector'])

    # Validate the seeds are present in the dataflow
    node_ids = [mu.get_ascend_node_name(node) for node in nodes if mu.get_dbt_node_type(node) in ['seed', 'source']]

    # Get existing nodes in dataflow
    existing_nodes = client.list_dataflow_components(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], deep=True).data
    existing_node_ids = [node.id for node in existing_nodes]

    # Print the list of nodes present and absent in the dataflow
    print("Nodes present in the dataflow:")
    for node in node_ids:
        if node in existing_node_ids:
            print(f"  {node}")
    print("Nodes absent in the dataflow:")
    for node in node_ids:
        if node not in existing_node_ids:
            print(f"  {node}")


def update_sql_cmd(ctx, **kwargs):
    """
    Update the SQL of existing Ascend dataflow transforms.
    """

    # Create Ascend Client
    client = Client(ctx.params['hostname'])

    nodes, dependencies = mu.get_nodes_and_dependencies(manifest=ctx.obj['manifest'], node_match_regex=ctx.params['model_selector'])

    # For every node, if there is a transform with the same name, update the SQL. Otherwise, display a message.
    for node_str in nodes:
        node_type = mu.get_dbt_node_type(node_str)

        if node_type != 'model':
            continue

        node = mu.get_ascend_node_name(node_str)
        input_ids = [mu.get_ascend_node_name(node) for node in dependencies[node_str]]
        print(f"Updating SQL of the transform {node}")
        try:
            transform_body = client.get_transform(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], id=node).data
            transform_body.view.operator.spark_function.executable.code.source.inline = tu.translate_sql(
                language=ctx.params['language'],
                sql=mu.get_compiled_sql(node_str=node_str), 
                input_ids=input_ids)
            client.update_transform(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], transform_id=node, body=transform_body)
        except Exception as e:
            print(f"Could not update transform {node}. Error: {e.reason}") 


