import logging
import pprint
import re
import time

import boto3

logging.basicConfig(format='%(message)s', level=logging.INFO)
LOG = logging.getLogger(__name__)


def parse_image(image_name):
    pattern = re.compile(r'^([a-zA-Z0-9\.\-]+:?[0-9]+?/[a-zA-Z0-9\._\-]+/[\/a-zA-Z0-9\._\-]+?):?([a-zA-Z0-9\._\-]+)?$')
    m = re.match(pattern, image_name)
    if m is None:
        pattern = re.compile(r'^([\/a-zA-Z0-9\._\-]+?):?([a-zA-Z0-9\._\-]+)?$')
        m = re.match(pattern, image_name)
    if m is None:
        exit('Error image name, Please check it')
    return m.group(1), m.group(2) if m.group(2) else 'lasted'


def clean_params(params_dict: dict):
    ret = {}
    for k, v in params_dict.items():
        if isinstance(v, dict):
            v = clean_params(v)
        if v is not None and v != {}:
            ret[k] = v
    return ret


class ECSDeploy(object):

    def __init__(self, cluster=None, service=None, images=None, **kwargs):
        self.cluster = cluster
        self.service = service
        # [(image_name, image_tag), (image_name, image_tag) ...]
        self.images = [parse_image(image) for image in images] if images else []
        self.client = boto3.client(service_name='ecs', **kwargs)
        self.current_task_definition = self.get_current_task_definition()

    def get_current_task_definition(self):
        services_info = self.client.describe_services(cluster=self.cluster, services=[self.service, ])
        task_definition_arn = services_info['services'][0]['taskDefinition']
        return self.client.describe_task_definition(taskDefinition=task_definition_arn)['taskDefinition']

    def create_new_task_definition(self, task_definition):
        new_task_definition = task_definition
        if not new_task_definition.get('containerDefinitions') or len(new_task_definition['containerDefinitions']) < 1:
            exit('Can not container definitions')

        images_dict = dict(self.images)

        for container_definition in new_task_definition['containerDefinitions']:
            image, _ = parse_image(container_definition.get('image'))
            if image in images_dict:
                container_definition['image'] = '{}:{}'.format(image, images_dict[image])

        for key in ('compatibilities', 'requiresAttributes', 'revision', 'status', 'taskDefinitionArn'):
            new_task_definition.pop(key, None)

        return new_task_definition

    def register_task_definition(self, task_definition):
        resp = self.client.register_task_definition(**task_definition)
        pprint.pprint(resp)
        LOG.info("New task definition: %s" % resp['taskDefinition']['taskDefinitionArn'])
        return resp['taskDefinition']['taskDefinitionArn']

    def get_revison_tasks(self, task_definition_arn):
        tasks = []
        while not tasks:
            time.sleep(1)
            tasks = self.client.list_tasks(
                cluster=self.cluster,
                serviceName=self.service,
                desiredStatus='RUNNING'
            ).get('taskArns')
            LOG.debug("tasks: %s" % tasks)
            for task_info in self.client.describe_tasks(cluster=self.cluster, tasks=tasks).get('tasks', []):
                if task_info['taskDefinitionArn'] != task_definition_arn:
                    tasks.remove(task_info['taskArn'])

        return tasks

    def update_service(self, task_definition_arn, maximum_percent=None, minimum_healthy_percent=None,
                       desired_count=None, max_definitions=1, scale_mode=False):
        params = dict(
            taskDefinition=task_definition_arn,
            deploymentConfiguration=dict(
                maximumPercent=maximum_percent,
                minimumHealthyPercent=minimum_healthy_percent
            ),
            desiredCount=desired_count
        )
        params = clean_params(params)

        LOG.info('Start updating the service.')
        resp = self.client.update_service(cluster=self.cluster, service=self.service, **params)
        print("Update: ")
        pprint.pprint(resp, indent=4)
        tasks = self.get_revison_tasks(task_definition_arn)
        waiter = self.client.get_waiter('tasks_running')
        waiter.wait(cluster=self.cluster, tasks=tasks)
        LOG.info('New task definition running.')

        all_task_definition_revisions = self.client.list_task_definitions(
            familyPrefix=self.current_task_definition['family'],
            status='ACTIVE',
            sort='ASC'
        ).get('taskDefinitionArns')

        if scale_mode is False:
            for task_definition in all_task_definition_revisions[:-max_definitions]:
                LOG.info("Deregistering task: %s" % task_definition)
                self.client.deregister_task_definition(taskDefinition=task_definition)

        LOG.info("Waiting service stable")
        waiter = self.client.get_waiter('services_stable')
        waiter.wait(cluster=self.cluster, services=[self.service])

        LOG.info("Service deployment successful.")
