import logging
import argparse
import os

from deploy import ECSDeploy

LOG = logging.getLogger(__name__)


def parse():
    parser = argparse.ArgumentParser(
        description='ecs-deploy',
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        usage='%(prog)s [options]'
    )
    parser.add_argument(
        '-k', '--aws-access-key',
        dest='aws_access_key_id',
        help='AWS Access Key ID. May also be set as environment variable AWS_ACCESS_KEY_ID',
    )
    parser.add_argument(
        dest='aws_secret_access_key',
        help='AWS Secret Access Key. May also be set as environment variable AWS_SECRET_ACCESS_KEY'
    )
    parser.add_argument(
        '-r', '--region',
        metavar='region_name', dest='region_name',
        help='AWS Region Name. May also be set as environment variable AWS_DEFAULT_REGION'
    )
    parser.add_argument(
        '-c', '--cluster',
        metavar='cluster_name', required=True,
        help='Name of ECS cluster'
    )
    parser.add_argument(
        '-n', '--service-name',
        metavar='service_name', dest='service',
        help='''Name of service to deploy'''
    )
    parser.add_argument(
        '-i', '--images',
        metavar='images', nargs='+', required=True,
        help='''Name of Docker image to run(support multiple images) \nex: --images repo/image:1.0 repo2/image2:8.0'''
    )
    parser.print_help()
    kwargs = vars(parser.parse_args())
    LOG.debug("arg params: %s" % kwargs)
    return kwargs


def main():
    kwargs = parse()
    # get value from environment variable
    kwargs.setdefault('aws_access_key_id', os.environ.get('AWS_ACCESS_KEY_ID', None))
    kwargs.setdefault('aws_secret_access_key', os.environ.get('AWS_SECRET_ACCESS_KEY', None))
    kwargs.setdefault('region_name', os.environ.get('AWS_DEFAULT_REGION', None))

    ecs = ECSDeploy(**kwargs)
    current_task_def = ecs.get_current_task_definition()
    new_task_def = ecs.create_new_task_definition(current_task_def)
    task_def_arn = ecs.register_task_definition(new_task_def)
    ecs.update_service(task_definition_arn=task_def_arn)


if __name__ == '__main__':
    main()