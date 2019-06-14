#!/usr/bin/env python

import yaml
from ozone.templates.awslambda import template
from ozone.resources.iam.policies import AWS_LAMBDA_BASIC_EXEC
from troposphere.iam import Role

ROLE = Role(
    'IamRole',
    Path='/lambda/demo',
    ManagedPoliciesArns=[AWS_LAMBDA_BASIC_EXEC]
)

with open('function_config.yml', 'r') as fd:
    CONFIG = yaml.safe_load(fd.read())

assert CONFIG
TEMPLATE_ARGS = {}

if 'layers' in CONFIG.keys():
    TEMPLATE_ARGS['Layers'] = CONFIG['layers']

TEMPLATE_ARGS['Role'] = 'dummyrole'
TEMPLATE_ARGS['Runtime'] = CONFIG['runtime']
TEMPLATE = template(**TEMPLATE_ARGS)

print(TEMPLATE.to_json())
