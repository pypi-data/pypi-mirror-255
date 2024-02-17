import json


class Deployment(object):

    @staticmethod
    def as_deployment(json_data):
        required_deployments = None
        deployment_group_index = None
        if 'requiredDeployments' in json_data:
            required_deployments = json_data['requiredDeployments']
        if 'deploymentGroupIndex' in json_data:
            deployment_group_index = json_data['deploymentGroupIndex']
        deployment = Deployment(json_data['id'], json_data['application'], json_data['deployeds'], json_data['deployables'],
                                json_data['containers'], required_deployments, deployment_group_index,
                                json_data['type'])
        return deployment

    def __init__(self, id, application, deployeds, deployables, containers, requiredDeployments,
                 deploymentGroupIndex, type):
        self.id = id
        self.application = application
        self.deployeds = deployeds
        self.deployables = deployables
        self.containers = containers
        self.requiredDeployments = requiredDeployments
        self.deploymentGroupIndex = deploymentGroupIndex
        self.type = type

    def to_dict(self):
        return dict(id=self.id, application=self.application, deployeds=self.deployeds, deployables=self.deployables,
                    containers=self.containers, requiredDeployments=self.requiredDeployments,
                    deploymentGroupIndex=self.deploymentGroupIndex, type=self.type)

