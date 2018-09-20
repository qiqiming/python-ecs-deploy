import argparse
import logging
import os

from deploy import ECSDeploy

LOG = logging.getLogger(__name__)


def check_positive(value):
    if not str(value).isdigit() or int(value) <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return int(value)


def check_params(params: dict):
    if not params.get('cluster') or not params.get('cluster'):
        raise ParamIllgal("Lack of '-c/--cluster' or '-n/--service-name' parameters")
    scale = params.get('scale')
    if scale:
        if params.get('desired_count'):
            print("Warning: You specified the 'desired-count' parameter, but it will not take effect")
    else:
        if not params.get('images'):
            raise ParamIllgal("Lack of '-i/--images' parameters")


class ParamIllgal(Exception):
    pass


def parse():
    parser = argparse.ArgumentParser(
        description='ecs-deploy',
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=300),
    )
    parser.add_argument(
        '-k', '--aws-access-key',
        dest='aws_access_key_id',
        help='AWS Access Key ID. May also be set as environment variable AWS_ACCESS_KEY_ID',
    )
    parser.add_argument(
        '-s', '--aws-secret-key',
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
        metavar='images', nargs='+',
        help='''Name of Docker image to run(support multiple images) \nex: --images repo/image:1.0 repo2/image2:8.0'''
    )
    parser.add_argument(
        '--min',
        metavar='minumumHealthyPercent', dest='minumum_healthy', type=check_positive,
        help='minumumHealthyPercent: The lower limit on the number of running tasks during a deployment.'
    )
    parser.add_argument(
        '--max',
        metavar='maximumPercent', dest='maximum_percent', type=check_positive,
        help='maximumPercent: The upper limit on the number of running tasks during a deployment.'
    )
    parser.add_argument(
        '--max-definitions',
        metavar='max-definitions', dest='max_definitions', type=check_positive, default=1,
        help='Number of Task Definition Revisions to persist before deregistering oldest revisions. (default: 1)'
    )
    parser.add_argument(
        '-D', '--desired-count',
        metavar='desired-count', dest='desired_count', type=check_positive,
        help='The number(positive) of instantiations of the task to place and keep running in your service.'
    )
    parser.add_argument(
        '--scale',
        metavar='nums', dest='scale', type=check_positive,
        help='Modifies the number(positive) of container instances of the current Task Definition'
    )
    kwargs = vars(parser.parse_args())
    check_params(kwargs)
    LOG.debug("arg params: %s" % kwargs)
    return kwargs


def main():
    kwargs = parse()
    # get value from environment variable
    kwargs.setdefault('aws_access_key_id', os.environ.get('AWS_ACCESS_KEY_ID', None))
    kwargs.setdefault('aws_secret_access_key', os.environ.get('AWS_SECRET_ACCESS_KEY', None))
    kwargs.setdefault('region_name', os.environ.get('AWS_DEFAULT_REGION', None))

    minumum_healthy = kwargs.pop('minumum_healthy', None)
    maximum_percent = kwargs.pop('maximum_percent', None)
    max_definitions = kwargs.pop('max_definitions', 1)
    desired_count = kwargs.pop('desired_count', None)
    scale = kwargs.pop('scale', None)

    ecs = ECSDeploy(**kwargs)
    current_task_def = ecs.get_current_task_definition()
    if scale:
        ecs.update_service(
            task_definition_arn=current_task_def['taskDefinitionArn'],
            desired_count=scale,
            scale_mode=True,
        )
    else:
        new_task_def = ecs.create_new_task_definition(current_task_def)
        task_def_arn = ecs.register_task_definition(new_task_def)
        ecs.update_service(
            task_definition_arn=task_def_arn,
            minimum_healthy_percent=minumum_healthy,
            maximum_percent=maximum_percent,
            max_definitions=max_definitions,
            desired_count=desired_count
        )


if __name__ == '__main__':
    main()
