from aws_cdk import (core, aws_eks as _eks)

class EKSManifest(core.Construct):
    
    def __init__(self, scope: core.Construct, id: str, cluster, manifest, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        self.cluster = cluster
        self.manifest = manifest
        
        def backend_service(self, manifest):
            labels = manifest['labels']
            deployment = {
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
            
            service = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {"name": manifest['service_name'], "namespace": "default"},
                "spec": {
                    "type": "LoadBalancer",
                    "ports": [{"port": 80, "targetPort": manifest['port']}],
                    "selector": manifest['labels']
                }
            }
            
            return deployment, service
        
        if self.manifest['service_type'] == 'backend':
            deployment_manifest, service_manifest = backend_service(self, self.manifest)
            
        _eks.KubernetesManifest(self, "NodeJSManifest", cluster=self.cluster, manifest=[deployment_manifest, service_manifest])