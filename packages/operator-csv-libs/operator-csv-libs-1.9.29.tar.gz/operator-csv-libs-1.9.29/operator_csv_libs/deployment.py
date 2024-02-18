import copy
from functools import reduce

class Deployment:
    """
    Class containing functions to work with Deployment yaml files
    """

    LABEL_LOCATIONS= [
        ('metadata', 'labels'),
        ('spec', 'template', 'metadata', 'labels')
    ]

    def __init__(self, deployment):
        self.original_deployment = deployment
        self.deployment = copy.deepcopy(self.original_deployment)

        self.name = ''
        self.containers = []

        if 'metadata' in self.deployment and 'name' in self.deployment['metadata']:
            self.name = self.deployment['metadata']['name']

        if 'containers' in self.deployment['spec']['template']['spec']:
            self.containers = self.deployment['spec']['template']['spec']['containers']

    def set_image(self, new_image, container_name=None):
        for c in self.containers:
            if container_name:
                if c['name'] == container_name:
                    c['image'] = new_image
            else:
                c['image'] = new_image

    def get_updated(self):
        self.deployment['spec']['template']['spec']['containers'] = self.containers
        return self.deployment

    def get_containers(self):
        return self.containers

    def set_label(self, attribute, value):
        for loc in self.LABEL_LOCATIONS:
            labels = reduce(lambda d, key: d[key], loc, self.deployment)
            if attribute in labels:
                if len(loc) == 2:
                    self.deployment[loc[0]][loc[1]][attribute] = value
                elif len(loc) == 4:
                    self.deployment[loc[0]][loc[1]][loc[2]][loc[3]][attribute] = value
