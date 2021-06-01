from aws_cdk import (core, aws_eks as _eks, aws_iam as _iam, aws_ec2 as _ec2)

import json

class EKSStack(core.Stack):
    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        
        super().__init__(scope, id, **kwargs)
        
        # create new vpc
        vpc = _ec2.Vpc(self, "VPC")
        
        # create eks
        self.eks = self.create_eks(vpc)
        
    def create_eks(self, vpc):
        # create eks cluster with amd nodegroup
        cluster = _eks.Cluster(self, "EKS", vpc=vpc, version=_eks.KubernetesVersion.V1_18,
                                default_capacity_instance=_ec2.InstanceType("m5.large"),
                                default_capacity=1)
        # add arm/graviton nodegroup
        cluster.add_nodegroup_capacity("graviton", desired_size=1, 
                                instance_type=_ec2.InstanceType("m6g.large"), 
                                nodegroup_name="graviton", node_role=cluster.default_nodegroup.role)
                                
        # create service account
        sa = self.add_service_account(cluster=cluster, name="aws-load-balancer-controller", 
                                      namespace="kube-system")
        
        # add helm charts
        ingress = cluster.add_helm_chart("LBIngress", chart="aws-load-balancer-controller",
                                release="aws-load-balancer-controller",
                                repository="https://aws.github.io/eks-charts",
                                namespace="kube-system", values={
                                    "clusterName": cluster.cluster_name,
                                    "serviceAccount.name": "aws-load-balancer-controller",
                                    "serviceAccount.create": "false"
                                })

        return cluster
    
    def add_service_account(self, cluster, name, namespace):
        """
        workaround to add helm role to service account
        
        """
        # create role 
        conditions = core.CfnJson(self, 'ConditionJson',
          value = {
            "%s:aud" % cluster.cluster_open_id_connect_issuer : "sts.amazonaws.com",
            "%s:sub" % cluster.cluster_open_id_connect_issuer : "system:serviceaccount:%s:%s" % (namespace, name),
          },
        )
        principal = _iam.OpenIdConnectPrincipal(cluster.open_id_connect_provider).with_conditions({
          "StringEquals": conditions,
        })
        role = _iam.Role(self, 'ServiceAccountRole', assumed_by=principal)
        
        # create policy for the service account
        statements = []
        with open('eks_stack/iam_policy.json') as f:
            data = json.load(f)
            for s in data["Statement"]:
                statements.append(_iam.PolicyStatement.from_json(s))
        policy = _iam.Policy(self, "LBControllerPolicy", statements=statements)
        policy.attach_to_role(role)
    
        return _eks.KubernetesManifest(self, "ServiceAccount", cluster=cluster,
          manifest=[{
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
              "name": name, 
              "namespace": namespace ,
              "labels": {
                "app.kubernetes.io/name": name, 
                "app.kubernetes.io/managed-by": "Helm",
              },
              "annotations": {
                "eks.amazonaws.com/role-arn": role.role_arn,
                "meta.helm.sh/release-name": name, 
                "meta.helm.sh/release-namespace": namespace, 
              },
            },
          }],
        );