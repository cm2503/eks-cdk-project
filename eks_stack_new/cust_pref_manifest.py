from aws_cdk import (core, aws_eks as _eks)


class CustPrefManifest(core.Construct):
    
    def __init__(self, scope: core.Construct, id: str, cluster, manifest, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        self.cluster = cluster
        self.manifest = manifest
        
        def custPref_service(self, manifest):
            labels = manifest['labels']
            
            pref_deployment = {
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
                                "ports": [{"containerPort": manifest['port'], "protocol": "TCP"}],
                                "env": [
                                    {
                                      "name":  "PREF_SERVICE_HOST",
                                      "value": "custprefsvc",
                                    }]
                                }
                            ]
                        }
                    }
                }
            }
            
            pref_service = {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {"name": manifest['service_name'], "namespace": "default"},
                    "spec": {
                        "type": "ClusterIP",
                        "ports": [{"port": 8096, "targetPort": manifest['port']}],
                        "selector": manifest['labels']
                    }
                }
            
            pref_auto_scaler = {
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
        
            return pref_deployment, pref_service, pref_auto_scaler
    
        if self.manifest['service_type'] == 'custPref_backend':
                pref_deployment_manifest, pref_service_manifest, pref_auto_scaler  = custPref_service(self, self.manifest)
                
        _eks.KubernetesManifest(self, "CustPrefManifest", cluster=self.cluster, manifest=[pref_deployment_manifest, pref_service_manifest, pref_auto_scaler])