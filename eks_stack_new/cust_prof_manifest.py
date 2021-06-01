from aws_cdk import (core, aws_eks as _eks)


class CustProfManifest(core.Construct):
    
    def __init__(self, scope: core.Construct, id: str, cluster, manifest, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        self.cluster = cluster
        self.manifest = manifest
        
        def custProf_service(self, manifest):
            labels = manifest['labels']
            prof_deployment = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": manifest['service_name'], "namespace": "default"},
                "spec": {
                    "replicas": manifest['replicas'],
                    "selector": {"matchLabels": labels},
                    "strategy": {
                    "rollingUpdate": {
                        "maxSurge": "25%",
                        "maxUnavailable": "25%"
                    }
                    },
                    "template": {
                        "metadata": {"labels": labels},
                        "spec": {
                            "containers": [{
                                "name":  manifest['service_name'],
                                "image": manifest['image'],
                                "ports": [{"containerPort": manifest['port'], "protocol": "TCP"}]
                            }
                            ]
                        }
                    }
                }
            }
            
            prof_service = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {"name": manifest['service_name'], "namespace": "default"},
                "spec": {
                    "type": "LoadBalancer",
                    "ports": [{"port": 80, "targetPort": manifest['port']}],
                    "selector": manifest['labels']
                }
            }
            
            prof_auto_scaler = {
                "apiVersion": "autoscaling/v1",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {"name": manifest['service_name'], "namespace": "default"},
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": manifest['service_name']
                        },
                    "minReplicas": 1,
                    "maxReplicas": 10,
                    "targetCPUUtilizationPercentage": 50
                }
            }

            return prof_deployment, prof_service, prof_auto_scaler
    
        if self.manifest['service_type'] == 'custProf_backend':
                prof_deployment_manifest, prof_service_manifest, prof_auto_scaler = custProf_service(self, self.manifest)
                
        _eks.KubernetesManifest(self, "CustProfManifest", cluster=self.cluster, manifest=[prof_deployment_manifest, prof_service_manifest, prof_auto_scaler])