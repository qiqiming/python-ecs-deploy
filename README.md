# python-ecs-deploy

[![GitHub](https://img.shields.io/github/license/qiqiming/python-ecs-deploy.svg)](https://github.com/qiqiming/python-ecs-deploy/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/python-ecs-deploy.svg?style=popout)](https://pypi.org/project/python-ecs-deploy/)

inspired by <https://github.com/silinternational/ecs-deploy>, rewrite use python3

This script use ecs client of boto3 to instigate an automatic blue/green deployment.
It only updates the tag of the images in the task definition with the same image name you provided
This allows you to easily implement CI/CD

## usage
```
ecs-deploy

optional arguments:
  -h, --help                                                        show this help message and exit
  -k AWS_ACCESS_KEY, --aws-access-key AWS_ACCESS_KEY                AWS Access Key ID. May also be set as environment variable AWS_ACCESS_KEY_ID
  -s AWS_SECRET_ACCESS_KEY, --aws-secret-key AWS_SECRET_ACCESS_KEY  AWS Secret Access Key. May also be set as environment variable AWS_SECRET_ACCESS_KEY
  -r region_name, --region region_name                              AWS Region Name. May also be set as environment variable AWS_DEFAULT_REGION
  -c cluster_name, --cluster cluster_name                           Name of ECS cluster
  -n service_name, --service-name service_name                      Name of service to deploy
  -i images [images ...], --images images [images ...]              Name of Docker image to run(support multiple images)
                                                                    ex: --images repo/image:1.0 repo2/image2:8.0
  --scale nums                                                      Modifies the number(positive) of container instances of the current Task Definition
```

## example

You have a task definition that contains two docker images(aaa/foo:1.0, bbb/bar:2.0)

Update the service with the new image:

```
ecs-deploy -c test_cluster -n test_service -i aaa/foo:1.1 bbb/bar:3.0
```

Scale current service number of tasks

```
ecs-deploy -c test_cluster -n test_service --scale 5
```

## Installation

```
pip install python-ecs-depl
```


