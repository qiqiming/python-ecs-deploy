import os

from setuptools import find_packages, setup

from ecs_deploy import VERSION

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    readme = f.read()

setup(
    name='python-ecs-deploy',
    version=VERSION,
    description="This script use ecs client of boto3 to instigate an automatic blue/green deployment.",
    long_description=readme,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
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
