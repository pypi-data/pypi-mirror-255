from ascend.sdk import definitions
from ascend.sdk.applier import DataflowApplier
from ascend.sdk.client import Client

from . import manifest_utils as mu
from . import transform_utils as tu

def update_component_sql_cmd(ctx, **kwargs):
    """
    Update the SQL of existing Ascend dataflow transform.
    """
    node = ctx.params['model_name']
    print(f"Updating SQL of the transform {node}")

    # Create Ascend Client
    client = Client(ctx.params['hostname'])

    nodes, dependencies = mu.get_nodes_and_dependencies(manifest=ctx.obj['manifest'], node_match_regex=ctx.params['model_selector'])

    node_str = mu.get_dbt_node_name(nodes, node)

    input_ids = [mu.get_ascend_node_name(node) for node in dependencies[node_str]]

    try:
        transform_body = client.get_transform(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], id=node).data
        transform_body.view.operator.spark_function.executable.code.source.inline = tu.translate_sql(
            language=ctx.params['language'],
            sql=mu.get_compiled_sql(node_str=node_str), 
            inputs=input_ids)
        client.update_transform(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], transform_id=node, body=transform_body)
    except Exception as e:
        print(f"Could not update transform {node}. Error: {e.reason}")     


def create_component_cmd(ctx, **kwargs):
    """
    Create a component from a dbt model.
    """
    # Create Ascend Client
    client = Client(ctx.params['hostname'])

    # Get manifest nodes and their dependencies
    nodes, dependencies = mu.get_nodes_and_dependencies(manifest=ctx.obj['manifest'], node_match_regex=ctx.params['model_selector'])

    # Get the list of existing dataflow components
    existing_nodes = client.list_dataflow_components(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], deep=True).data

    # Check that the component has all its dependencies in the dataflow
    model_name = ctx.params['model_name']

    # Check that the model_name exists
    try:
        mu.get_dbt_node_name(nodes, model_name)
    except:
        print(f"Node {model_name} is not present in the dataflow. Please check it and try again.")
        exit(1)

    node_id = mu.get_dbt_node_name(nodes, model_name)
    for node_str in dependencies[node_id]:
        node = mu.get_ascend_node_name(node_str)
        if  node not in [node.id for node in existing_nodes]:
            print(f"Node {node} is not present in the dataflow. Please add it and try again.")
            exit(1)

    # Create the component
    component = tu.create_transform(
        id=ctx.params['model_name'], 
        sql=mu.get_compiled_sql(node_str=node_id), 
        inputs=[mu.get_ascend_node_name(node) for node in dependencies[node_id]],
        description=mu.get_description(node_str=node_id),
        reduction=ctx.params['reduction'],
        language=ctx.params['language'],
    )
    components = [component]

    # Deploy tests if requested
    groups = []
    if ctx.params['with_tests']:

        # Get test data
        test_data, nodes_with_test_data = mu.get_tests_and_nodes(manifest=ctx.obj['manifest'])

        # Get tests for the created node
        test_id = [test for test in nodes_with_test_data if mu.get_ascend_node_name(test) == ctx.params['model_name']][0]
        tests = nodes_with_test_data[test_id] 

        # Create transforms for the tests
        for test_id in tests:
            test = test_data[test_id]

            # If one of the inputs is not there, don't deploy the test and report it
            test_dependencies = test['depends_on']['nodes']
            existing_components_plus_transform = {node.id for node in existing_nodes}
            existing_components_plus_transform.add(ctx.params['model_name'])
            missing_nodes = {mu.get_ascend_node_name(dep) for dep in test_dependencies} - existing_components_plus_transform
            if len(missing_nodes) > 0:
                print(f"Test {test['name']} is missing the following dependencies: {missing_nodes}. Skipping test.")
                continue

            components.append(
                tu.create_transform(
                    id=test['name'], 
                    sql=test['compiled_code'], 
                    inputs=test['depends_on']['nodes'],
                    description=test.get('description', ''),
                    custom_dq_test_sql='select * from {{target}} WHERE 1=1',
                    reduction='full-reduction',
                    language=ctx.params['language'],
                )
            )

        groups = [definitions.ComponentGroup(
            id=f'{ctx.params["model_name"]}_dbt_tests',
            name=f'{ctx.params["model_name"]}_dbt_tests',
            component_ids = [transform.id for transform in components if transform.id != ctx.params['model_name']],
            description=f'{ctx.params["model_name"]} dbt tests'
            )]

    # Get dataflow definition
    dataflow_def = client.get_dataflow(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow']).data

    # Perform a non-deleting append
    applier = DataflowApplier(client)
    applier.apply(data_service_id=ctx.params['data_service'], dataflow=definitions.Dataflow(id=dataflow_def.id, name=dataflow_def.name, components=components, groups=groups), delete=False, dry_run=False)

def show_component_sql_cmd(ctx, **kwargs):
    """
    Show the SQL of existing Ascend dataflow transform.
    """

    nodes, dependencies = mu.get_nodes_and_dependencies(manifest=ctx.obj['manifest'], node_match_regex=ctx.params['model_selector'])
    node = mu.get_dbt_node_name(nodes, ctx.params['model_name'])
    print(f"Showing SQL of the {node}\n ------------------\n")

    compiled_sql = mu.get_compiled_sql(node_str=node)

    if ctx.params['show_raw']:
        print(compiled_sql)
    else:
        print(tu.translate_sql(
            language=ctx.params['language'],
            sql=compiled_sql, 
            input_ids=[mu.get_ascend_node_name(node) for node in dependencies[node]])
            )