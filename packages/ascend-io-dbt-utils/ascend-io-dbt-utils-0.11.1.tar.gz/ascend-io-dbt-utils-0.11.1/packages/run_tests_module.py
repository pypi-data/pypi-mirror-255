from ascend.sdk import definitions
from ascend.sdk.applier import DataflowApplier
from ascend.sdk.client import Client

from . import manifest_utils as mu
from . import transform_utils as tu


def deploy_tests_cmd(ctx, **kwargs):

    # Get nodes and dependencies
    test_data, nodes_with_test_data = mu.get_tests_and_nodes(manifest=ctx.obj['manifest'])

    # Create Ascend Client
    client = Client(ctx.params['hostname'])

    # Get the list of components in the dataflow
    components = client.list_dataflow_components(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], deep=True).data

    # For every node with test data, check the node exists in the dataflow
    nodes_to_be_tested = []
    for node_to_be_tested in [node for node in nodes_with_test_data]:
        node_id = mu.get_ascend_node_name(node_to_be_tested)
        if node_id not in [component.id for component in components]:
            print(f"Node {node_id} is not present in the dataflow.")
        else:
            print(f"Node {node_id} is present in the dataflow.")
            nodes_to_be_tested.append(node_to_be_tested)

    # For every existing node from the list, add transforms for every test linked to that node
    transforms = []
    present_component_names = [component.id for component in components]
    for test, test_details in test_data.items():

        # If one of the inputs is not there, don't deploy the test and report it
        test_dependencies = [mu.get_ascend_node_name(test) for test in test_details['depends_on']['nodes']]
        missing_nodes = set(test_dependencies) - set(present_component_names)
        if len(missing_nodes) > 0:
            print(f"Test {test} is missing the following dependencies: {missing_nodes}. Skipping test.")
            continue

        # If the test has no compiled code, skip the test and report an error
        if not 'compiled_code' in test_details.keys():
            print(f"Test {test} has no compiled code. Skipping test.")
            continue

        print(f"Adding test {test_details['name']} to the dataflow.")

        transforms.append(
            tu.create_transform(
                id=test_details['name'], 
                sql=test_details['compiled_code'], 
                inputs=test_details['depends_on']['nodes'],
                description=test_details.get('description', ''),
                custom_dq_test_sql='select * from {{target}} WHERE 1=1',
                reduction='full-reduction',
                language=ctx.params['language'],
            )
        )

    # Check if there are any transforms to deploy
    if len(transforms) == 0:
        print("No tests to deploy.")
        return

    # Create a group and add all the transforms to the group
    group=definitions.ComponentGroup(
        id="dbt_tests",
        name="dbt tests",
        component_ids = [transform.id for transform in transforms],
        description="dbt tests"
        )

    # Deploy the test transforms using the dataflow applier
    # Get dataflow definition
    dataflow_def = client.get_dataflow(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow']).data

    # Create dataflow definition
    dataflow_def = definitions.Dataflow(
        id=dataflow_def.id, 
        name=dataflow_def.name, 
        components=transforms,
        groups=[group]
        )

    # Perform a non-deleting append
    applier = DataflowApplier(client)
    applier.apply(data_service_id=ctx.params['data_service'], dataflow=dataflow_def, delete=False, dry_run=False)


def delete_tests_cmd(ctx, **kwargs):
    # Create Ascend Client
    client = Client(ctx.params['hostname'])
    
    # Get test nodes
    test_data, _ = mu.get_tests_and_nodes(manifest=ctx.obj['manifest'])

    # Remove all nodes from the list of existing nodes in reverse order
    node_ids = [node for node in test_data.keys()]
    for node in node_ids:
        print(f"Deleting test {node}")
        try:
            client.delete_transform(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], id=node)
        except Exception as e:
            print(f"An error occurred while deleting transform {node}: {e.reason}")

    # Delete component group
    print(f"Deleting component group dbt_tests")
    try:
        client.delete_component_group(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], id="dbt_tests")
    except Exception as e:
        print(f"An error occurred while deleting dbt_tests group: {e.reason}")

def check_test_results_cmd(ctx, **kwargs):
    """
    Check the results of all dbt tests against the deployed models in Ascend.
    """
    # Create Ascend Client
    client = Client(ctx.params['hostname'])

    # Get test nodes
    test_data, _ = mu.get_tests_and_nodes(manifest=ctx.obj['manifest'])

    # Get the list of components in the dataflow
    components = client.list_dataflow_components(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], deep=True).data

    # For every node with test data, check the node exists in the dataflow
    nodes_to_be_tested = []
    for node_to_be_tested in [node for node in test_data.keys()]:
        node_id = mu.get_ascend_node_name(node_to_be_tested)
        if node_id not in [component.id for component in components]:
            print(f"Node {node_id} is not present in the dataflow.")
        else:
            nodes_to_be_tested.append(node_id)

    # For every existing test node from the list, retrieve and print the number of records
    print("Checking test results based on the number of records returned by tests...")
    for test_node in nodes_to_be_tested:
        try:
            test_results = client.get_transform_records(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], id=test_node, limit=1).data
            num_of_records = len(test_results.data.records_response.records.value)
            message = f"{Colours.GREEN}Ok.{Colours.RESET}" if num_of_records == 0 else f"{Colours.RED}Failed.{Colours.RESET}"
            print(f"Test {test_node} produced {num_of_records} records. Test result is {message}")
        except Exception as e:
            print(f"An error occurred while retrieving test {test_node} results: {e.reason}")

    # For every existing test node from the list, check custom SQL test results
    print()
    print("Checking test results based on data quality check results...")
    for test_node in nodes_to_be_tested:
        try:
            test_results = client.get_transform_quality_test_results(data_service_id=ctx.params['data_service'], dataflow_id=ctx.params['dataflow'], id=test_node).data
            result = test_results.test_summaries[0].result
            if result == "passed":
                result_str = f"{Colours.GREEN}{result}{Colours.RESET}"
            else:
                result_str = f"{Colours.RED}{result}{Colours.RESET}"
            print(f"Test {test_node} produced {result_str}")
        except Exception as e:
            print(f"An error occurred while retrieving test {test_node} results: {e.reason}")

class Colours:
    RED = '\033[31m'
    GREEN = '\033[32m'
    RESET = '\033[0m'