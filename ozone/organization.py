# -*- coding: utf-8 -*-

"""
Class to represent an organization
"""
import re
import boto3
from botocore.exceptions import ValidationError, ClientError
from json import JSONEncoder
import json

ACCOUNTID_IN_ARN = re.compile(r'(\d{12})')

class Account(object):
    """
    Class to represent an account
    """
    def __init__(self, account, ouid, ouname):
        """
        Initialize the Account object
        """
        for key, value in account.items():
            setattr(self, key, value)
        self.JoinedTimestamp = self.JoinedTimestamp.isoformat()
        self.OrganizationUnitId = ouid
        self.OrganizationUnitName = ouname

    def to_dict(self):
        return self.__dict__


class Organization(object):
    """
    Class to represent an organization
    """

    def __init__(self, ouid=None, parent=None, parent_name=None, client=None):
        """
        Initializes the OrganizationUnit node
        """
        if client is None:
            client = boto3.client('organizations')

        self.parent = parent
        if ouid is None:
            self.ouid = client.list_roots()['Roots'][0]['Id']
        else:
            self.ouid = ouid

        if not self.ouid.startswith('r-'):
            data = client.describe_organizational_unit(
                OrganizationalUnitId=self.ouid
            )["OrganizationalUnit"]
            self.name = data['Name']
            self.arn = data['Arn']
        else:
            self.name = 'Root'
            self.arn = client.list_roots()['Roots'][0]['Arn']
        if self.name == 'Root' or parent_name is None:
            self.path = ''
        else:
            self.path = f'{parent_name}/{self.name}'
        self.ous = []

        accounts = client.list_accounts_for_parent(
            ParentId=self.ouid
        )['Accounts']
        self.accounts = []
        for account in accounts:
            self.accounts.append(Account(account, self.ouid, self.name))

        children_ous = client.list_children(
            ParentId=self.ouid,
            ChildType='ORGANIZATIONAL_UNIT'
        )['Children']

        for unit in children_ous:
            self.ous.append(Organization(unit['Id'], self.ouid, self.path, client))

    def __repr__(self):
        return self.to_dict()


    def get_organization_unit(self, ou_path, ou=None):
        """
        Get the details of an organization by name
        """

        if ou is None:
            ou = self

        if ou_path.startswith('/'):
            ou_path = ou_path[1:]
        if ou_path.split('/') and ou_path.endswith('/'):
            ou_path = ou_path[:-1]

        ou_child = ou_path.split('/', 1)[-1]
        if ou_path.find('/') > 0:
            ou_parent = ou_path.split('/', 1)[0]
        else:
            ou_parent = ou_path

        for org in ou.ous:
            if org.name == ou_path:
                return org
            if ou_parent == org.name:
                if ou_child.split('/'):
                    return self.get_organization_unit(ou_child, org)


    def get_all_accounts(self, accounts=None, nextou=None):
        """
        Returns all accounts in the Organization
        """
        if accounts is None:
            accounts = []
        if nextou is None:
            nextou = self
            accounts = [account.to_dict() for account in self.accounts]

        for ounit in nextou.ous:
            if ounit.accounts:
                accounts += [account.to_dict() for account in ounit.accounts]
            if ounit.ous:
                for subou in ounit.ous:
                    return self.get_all_accounts(accounts, subou)
        return accounts

    def to_dict(self):
        rendered_accounts = []
        rendered_ous = []
        for ounit in self.ous:
            rendered_ous.append(ounit.to_dict())
        for ounit in self.accounts:
            rendered_accounts.append(ounit.to_dict())
        self.ous = rendered_ous
        self.accounts = rendered_accounts
        return self.__dict__


if __name__ == '__main__':
    from argparse import ArgumentParser
    PARSER = ArgumentParser()
    PARSER.add_argument('--ou-path', required=True)
    ARGS = PARSER.parse_args()

    Org = Organization()
    ou = Org.get_organization_unit(ARGS.ou_path)
    print(ou.get_all_accounts())
