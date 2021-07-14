import os

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elasticloadbalancingv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs
from aws_cdk import aws_ssm as ssm
from aws_cdk import core


class EcsClusterMnist(core.Stack):
    def __init__(self, scope: core.App, name: str, **kwargs) -> None:
        super().__init__(scope, name, **kwargs)

        # if the docker image is from public repo
        vpc = ec2.Vpc(
            self,
            "EcsClusterMnist-Vpc",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            nat_gateways=0,
        )

        sg = ec2.SecurityGroup(
            self,
            "EcsClusterMnist-SG",
            vpc=vpc,
            allow_all_outbound=True,
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic(),
        )

        # TODO setup alb in cdk
        # alb = elasticloadbalancingv2.ApplicationLoadBalancer(
        #     self,
        #     "EcsClusterMnist-Alb",
        #     security_group=sg,
        #     vpc=vpc,
        #     internet_facing=True,
        # )
        # alb.add_listener(
        #     "EcsClusterMnist-Listener",
        #     default_action=elasticloadbalancingv2.ListenerAction(
        #         elasticloadbalancingv2.CfnListener.ActionProperty(type="forward")
        #     ),
        #     port=80,
        #     protocol=elasticloadbalancingv2.ApplicationProtocol.HTTP,
        # )

        cluster = ecs.Cluster(self, "EcsClusterMnist-Cluster", vpc=vpc)

        taskdef = ecs.FargateTaskDefinition(
            self,
            "EcsClusterMnist-TaskDef",
            cpu=1024,  # 1 CPU
            memory_limit_mib=4096,  # 4GB RAM
        )

        taskdef.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW, resources=["*"], actions=["ssm:GetParameter"]
            )
        )

        # REST API port
        port_mapping = ecs.PortMapping(container_port=8501, host_port=8501)

        container = taskdef.add_container(
            id="EcsClusterMnist-Container",
            image=ecs.ContainerImage.from_registry(
                "public.ecr.aws/e2j4c7c9/test-mnist-serving:latest"
            ),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="EcsClusterMnist",
                log_retention=aws_logs.RetentionDays.ONE_DAY,
            ),
            port_mappings=[port_mapping],
        )

        # if alb setup is succeeded
        # service = ecs.FargateService(
        #     self,
        #     id="EcsClusterMnist-Service",
        #     task_definition=taskdef,
        #     cluster=cluster,
        #     assign_public_ip=True,
        # )

        # # Store parameters in SSM
        ssm.StringParameter(
            self,
            "ECS_CLUSTER_NAME",
            parameter_name="ECS_CLUSTER_NAME",
            string_value=cluster.cluster_name,
        )
        ssm.StringParameter(
            self,
            "ECS_TASK_DEFINITION_ARN",
            parameter_name="ECS_TASK_DEFINITION_ARN",
            string_value=taskdef.task_definition_arn,
        )
        ssm.StringParameter(
            self,
            "ECS_TASK_VPC_SUBNET_1",
            parameter_name="ECS_TASK_VPC_SUBNET_1",
            string_value=vpc.public_subnets[0].subnet_id,
        )
        ssm.StringParameter(
            self,
            "CONTAINER_NAME",
            parameter_name="CONTAINER_NAME",
            string_value=container.container_name,
        )

        core.CfnOutput(self, "ClusterName", value=cluster.cluster_name)
        core.CfnOutput(self, "TaskDefinitionArn", value=taskdef.task_definition_arn)


app = core.App()
EcsClusterMnist(
    app,
    "EcsClusterMnist",
    env={
        "region": os.environ["CDK_DEFAULT_REGION"],
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    },
)

app.synth()
