from setuptools import setup, find_packages

VERSION = '0.0.3'

setup(
    name='python-ecs-deploy',
    version=VERSION,
    description="This script use ecs client of boto3 to instigate an automatic blue/green deployment.",
    classifiers=[],
    keywords='python aws-ecs ecs',
    author='qiqiming',
    author_email='tiedanqi@gmail.com',
    url='https://github.com/qiqiming/python-ecs-deploy',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'boto3',
    ],
    entry_points={
        'console_scripts': [
            'ecs-deploy=ecs_deploy.cli:main',
        ]
    },
)
