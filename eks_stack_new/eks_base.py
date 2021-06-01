from aws_cdk import (core, aws_eks as _eks, aws_ec2 as _ec2)

class EKSBase(core.Construct):
    
    def __init__(self, scope: core.Construct, id: str, cluster_configuration, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        self.cluster_configuration = cluster_configuration
        
        def determine_cluster_size(self):
            """
            return instance_size, node_count
            """
            if self.cluster_configuration['capacity_details'] == 'small':
                # default to fargate only
                instance_details = _ec2.InstanceType.of(_ec2.InstanceClass.BURSTABLE3, _ec2.InstanceSize.SMALL)
                instance_count = 1
            elif self.cluster_configuration['capacity_details'] == 'medium':
                instance_details = _ec2.InstanceType.of(_ec2.InstanceClass.BURSTABLE3, _ec2.InstanceSize.SMALL)
                instance_count = 2
            elif self.cluster_configuration['capacity_details'] == 'large':
                instance_details = _ec2.InstanceType.of(_ec2.InstanceClass.BURSTABLE3, _ec2.InstanceSize.SMALL)
                instance_count = 3
            else:
                # For a non specified capacity cluster, we will default to zero nodes and fargate only
                instance_count = 1
                instance_details = _ec2.InstanceType.of(_ec2.InstanceClass.BURSTABLE3, _ec2.InstanceSize.SMALL)
                self.cluster_configuration['fargate_enabled'] == True
            
            return { 'default_capacity': instance_count, 'default_capacity_instance': instance_details }
        
        capacity_details = determine_cluster_size(self)
        
        # Create an EKS cluster with default nodegroup configuration        
        self.cluster = _eks.Cluster(
            self, "EKSCluster",
            version = self.cluster_configuration['eks_version'],
            cluster_name = self.cluster_configuration['cluster_name'],
            **capacity_details
        )
        
        # If fargate is enabled, create a fargate profile
        if self.cluster_configuration['fargate_enabled'] is True:
            self.cluster.add_fargate_profile(
                "FargateEnabled",
                selectors = [
                    _eks.Selector(
                        namespace = 'default',
                        labels = { 'fargate': 'enabled' }
                    )
                ]
            )
            
        # If bottle rocket is enabled, build a self managed nodegroup
        if self.cluster_configuration.get('bottlerocket_asg') is True:
            self.cluster.add_auto_scaling_group_capacity(
                "BottleRocketASG",
                instance_type=_ec2.InstanceType.of(_ec2.InstanceClass.BURSTABLE3, _ec2.InstanceSize.SMALL),
                machine_image_type=_eks.MachineImageType.BOTTLEROCKET,
                desired_capacity=1,
            )
        
        