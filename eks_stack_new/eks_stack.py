from aws_cdk import (core, aws_eks as _eks)
from .eks_base import EKSBase
from .cust_prof_manifest import CustProfManifest
from .cust_pref_manifest import CustPrefManifest
from .alb_ingress import ALBIngressController

class EKSWorkshop(core.Stack):
    
    # def __init__(self, scope: core.Construct, id: str, 
    # eks_version=_eks.KubernetesVersion.V1_18, cluster_name='cftc-demo', 
    # capacity_details='small', fargate_enabled=False, bottlerocket_asg=False,
    # nodejs_service={}, **kwargs) -> None:
    #     super().__init__(scope, id, **kwargs)
    #     self.eks_version = eks_version
    #     self.cluster_name = cluster_name
    #     self.capacity_details = capacity_details
    #     self.fargate_enabled = fargate_enabled
    #     self.bottlerocket_asg = bottlerocket_asg
    #     self.nodejs_service = nodejs_service
    
    def __init__(self, scope: core.Construct, id: str, 
    eks_version=_eks.KubernetesVersion.V1_18, cluster_name='cftc-demo', 
    capacity_details='small', fargate_enabled=False, bottlerocket_asg=False,
    cust_prof_service={}, cust_pref_service={}, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.eks_version = eks_version
        self.cluster_name = cluster_name
        self.capacity_details = capacity_details
        self.fargate_enabled = fargate_enabled
        self.bottlerocket_asg = bottlerocket_asg
        self.cust_prof_service = cust_prof_service
        self.cust_pref_service = cust_pref_service
        
        
        config_dict = {
            'eks_version': self.eks_version,
            'cluster_name': self.cluster_name,
            'capacity_details': self.capacity_details,
            'fargate_enabled': self.fargate_enabled,
            'bottlerocket_asg': self.bottlerocket_asg
        }
        
        base_cluster = EKSBase(self, "Base", cluster_configuration=config_dict)
        cust_prof_service = CustProfManifest(self, "PrefServ", cluster=base_cluster.cluster, manifest=self.cust_prof_service)
        cust_pref_service = CustPrefManifest(self, "PrefServ1", cluster=base_cluster.cluster, manifest=self.cust_pref_service)
        alb_ingress = ALBIngressController(self, "ALBIngress", cluster=base_cluster.cluster)