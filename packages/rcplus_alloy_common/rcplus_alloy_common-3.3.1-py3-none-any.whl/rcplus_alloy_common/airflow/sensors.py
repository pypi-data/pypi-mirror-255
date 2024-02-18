import json
from jsonpath_ng.ext.parser import parse

from airflow.exceptions import AirflowException
from airflow.sensors.base import BaseSensorOperator
from airflow.providers.amazon.aws.sensors.sqs import SqsSensor
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook

from rcplus_alloy_common.airflow.decorators import alloyize


@alloyize
class AlloySqsSensor(SqsSensor):
    """
    Alloy SqsSensor class with default arguments injected with on_failure_callback.

    NOTE: we use jsonpath_ng.ext.parser.parse (instead of jsonpath_ng.parse) in order to support xpath filters
    """

    def filter_messages_jsonpath(self, messages):
        # NOTE: we use from jsonpath_ng.ext.parser in order to support the filter
        jsonpath_expr = parse(self.message_filtering_config)
        filtered_messages = []
        for message in messages:
            body = message["Body"]
            # Body is a string, deserialize to an object and then parse
            body = json.loads(body)
            results = jsonpath_expr.find(body)
            if not results:
                continue
            if self.message_filtering_match_values is None:
                filtered_messages.append(message)
                continue
            for result in results:
                if result.value in self.message_filtering_match_values:
                    filtered_messages.append(message)
                    break
        self.log.info(f"Filtered {len(messages)} messages to {len(filtered_messages)} messages: {filtered_messages}")
        return filtered_messages


@alloyize
class AlloyAutoScalingGroupSensor(BaseSensorOperator):
    template_fields = ["autoscaling_group_name"]

    def __init__(self, *args, autoscaling_group_name, **kwargs):
        self.autoscaling_group_name = autoscaling_group_name
        super().__init__(*args, **kwargs)

    def poke(self, context):
        client = AwsBaseHook(client_type="autoscaling").get_client_type()
        response = client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                self.autoscaling_group_name,
            ],
            MaxRecords=1,
        )

        if "AutoScalingGroups" in response and len(response["AutoScalingGroups"]) == 1:
            asg_data = response["AutoScalingGroups"][0]
            if asg_data["DesiredCapacity"] <= 0:
                self.log.error(
                    f"The incorrect capacity value {asg_data['DesiredCapacity']} detected "
                    f"for {self.autoscaling_group_name} autoscaling group. Be sure to set "
                    f"the correct value before using this sensor.")
                raise AirflowException("Incorrect AutoScalingGroup capacity value")

            if len(asg_data["Instances"]) == asg_data["DesiredCapacity"]:
                in_service = [instance["LifecycleState"] == "InService" for instance in asg_data["Instances"]]
                if all(in_service):
                    instance_ids = [instance["InstanceId"] for instance in asg_data["Instances"]]
                    ec2_client = AwsBaseHook(client_type="ec2").get_client_type()
                    statuses = ec2_client.describe_instance_status(InstanceIds=instance_ids)["InstanceStatuses"]
                    are_running = [status["InstanceStatus"]["Status"] == "ok" for status in statuses]
                    return all(are_running)

        return False
