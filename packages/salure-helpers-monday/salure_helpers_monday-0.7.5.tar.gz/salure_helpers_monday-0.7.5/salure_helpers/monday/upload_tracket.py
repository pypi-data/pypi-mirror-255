import os
import sys
import pandas as pd
from typing import Union, List
import requests
import json
from salure_helpers.salureconnect import SalureConnect

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class UploadTracket(SalureConnect):

    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        For the full documentation, see: https://avisi-apps.gitbook.io/tracket/api/
        """
        super().__init__()
        self.headers = self.__get_headers(label=label)
        self.base_url = "https://v1-gateway-9e6mvodx.uk.gateway.dev/api/1.0/"
        self.debug = debug

    def __get_headers(self, label):
        """
        Get the credentials for the Traket API from SalureConnect, with those credentials, get the access_token for Tracket.
        Return the headers with the access_token.
        """
        # Get credentials from SalureConnect
        credentials = self.get_system_credential(system='tracket', label=label)

        # With those credentials, get the access_token from Tracket
        endpoint = 'https://v1-gateway-9e6mvodx.uk.gateway.dev/api/1.0/oauth2/token'
        payload = json.dumps({
            "grant-type": "client-credentials",
            "monday/account-id": credentials['account_id'],
            "client-id": credentials['client_id'],
            "client-secret": credentials['client_secret']
        })
        headers = {'Content-Type': 'application/json'}
        tracket_response = requests.request("POST", endpoint, headers=headers, data=payload)

        # Return the headers with the access_token
        access_token = tracket_response.json()['access_token']
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }

        return headers

    @staticmethod
    def __check_fields(data: Union[dict, List], required_fields: List, allowed_fields: List):
        if isinstance(data, dict):
            data = data.keys()

        for field in data:
            if field not in allowed_fields and field not in required_fields:
                warnings.warn('Field {field} is not implemented. Optional fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields)))

        for field in required_fields:
            if field not in data:
                raise ValueError('Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

    def create_worklog(self, data: dict) -> requests.Response:
        """
        Create a new worklog in Tracket.
        :param data: A dictionary with all the required fields to create a worklog.
        """
        required_fields = ['worklogMinutes', 'worklogDate', 'itemId', 'userId']
        allowed_fields = ['worklogCategory', 'description', 'worklogBillableMinutes']
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'{self.base_url}worklogs'

        base_body = {
            "worklogMinutes": data['worklogMinutes'],
            "worklogDate": data['worklogDate'],
            "itemId": data['itemId'],
            "userId": data['userId']
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"worklogCategory": data['worklogCategory']}) if 'worklogCategory' in data else fields_to_update
        fields_to_update.update({"description": data['description']}) if 'description' in data else fields_to_update
        fields_to_update.update({"worklogBillableMinutes": data['worklogBillableMinutes']}) if 'worklogBillableMinutes' in data else fields_to_update
        base_body.update(fields_to_update)

        if self.debug:
            print(json.dumps(base_body))

        response = requests.request("POST", url, data=json.dumps(base_body), headers=self.headers)
        return response

    def update_worklog(self, worklog_id: str, data: dict) -> requests.Response:
        """
        Get all the worklogs from Tracket.
        :param worklog_id: The ID of the worklog that you want to update.
        :param data: A dictionary with all the required fields to update a worklog.
        """
        required_fields = ['worklogMinutes', 'worklogDate', 'itemId', 'userId']
        allowed_fields = ['worklogCategory', 'description', 'worklogBillableMinutes']
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'{self.base_url}worklogs/{worklog_id}'

        base_body = {
            "worklogMinutes": data['worklogMinutes'],
            "worklogDate": data['worklogDate'],
            "itemId": data['itemId'],
            "userId": data['userId']
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"worklogCategory": data['worklogCategory']}) if 'worklogCategory' in data else fields_to_update
        fields_to_update.update({"description": data['description']}) if 'description' in data else fields_to_update
        fields_to_update.update({"worklogBillableMinutes": data['worklogBillableMinutes']}) if 'worklogBillableMinutes' in data else fields_to_update
        base_body.update(fields_to_update)

        if self.debug:
            print(json.dumps(base_body))

        response = requests.request("PUT", url, data=json.dumps(base_body), headers=self.headers)
        return response

    def delete_worklog(self, worklog_id: str) -> requests.Response:
        """
        Get all the worklogs from Tracket.
        :param worklog_id: The ID of the worklog that you want to delete.
        """
        url = (f'{self.base_url}worklogs/{worklog_id}')
        response = requests.request("DELETE", url, headers=self.headers)
        return response