#!/usr/bin/env python3
# from aws_cdk import core
# from eks_stack.eks_stack import EKSStack
# env = core.Environment(account="960046141612", region="us-east-1")
# app = core.App()
# core.Tag.add(app, key="email", value=app.node.try_get_context('envs')['prod']['email'])
# core.Tag.add(app, key="stack-level-tagging", value=app.node.try_get_context('envs')['prod']['tagValue'])
# core.Tag.add(app, key="Owner", value=app.node.try_get_context('envs')['prod']['owner'])
# # EKS Stack
# backend = EKSStack(app, "backend", env=env)
# app.synth()

from aws_cdk import core

from eks_stack_new.eks_stack import EKSWorkshop

cust_pref_service_details = {
    "service_name": "custprefsvc",
    "replicas": 1,
    "labels": {
        "app": "custprefsvc"
    },
    "image": "960046141612.dkr.ecr.us-east-1.amazonaws.com/custprefsvc:1.0.0",
    "port": 8096,
    "service_type": "custPref_backend"
}

cust_prof_service_details = {
    "service_name": "custprofsvc",
    "replicas": 1,
    "labels": {
        "app": "custprofsvc"
    },
    "image": "960046141612.dkr.ecr.us-east-1.amazonaws.com/custprofsvc:1.0.0",
    "port": 8095,
    "service_type": "custProf_backend"
}

# Cluster name: If none, will autogenerate
cluster_name = "cftc-demo" 
# Capacity details: Cluster size of small/med/large
capacity_details = "small"
# Fargate enabled: Create a fargate profile on the cluster
fargate_enabled = False
# Bottlerocket ASG: Create a self managed node group of Bottlerocket nodes
bottlerocket_asg = False

app = core.App()

core.Tag.add(app, key="email", value=app.node.try_get_context('envs')['prod']['email'])
core.Tag.add(app, key="stack-level-tagging", value=app.node.try_get_context('envs')['prod']['tagValue'])
core.Tag.add(app, key="Owner", value=app.node.try_get_context('envs')['prod']['owner'])

# EKSWorkshop(app, "cftc-demo", fargate_enabled=fargate_enabled, capacity_details=capacity_details, 
#              bottlerocket_asg=bottlerocket_asg, cust_pref_service=cust_pref_service_details, 
#              cust_prof_service=cust_prof_service_details)

EKSWorkshop(app, "cftc-demo", fargate_enabled=fargate_enabled, capacity_details=capacity_details, 
             bottlerocket_asg=bottlerocket_asg, cust_prof_service=cust_prof_service_details, cust_pref_service=cust_pref_service_details)

app.synth()