import os
import sys
import pandas as pd
from typing import Union, List
import requests
import json
from salure_helpers.salureconnect import SalureConnect

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class ExtractMonday(SalureConnect):

    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        For the full documentation, see: https://developer.monday.com/api-reference/docs/basics
        """
        super().__init__()
        self.headers = self.__get_headers(label=label)
        self.endpoint = "https://api.monday.com/v2/"
        self.debug = debug

    def __get_headers(self, label):
        credentials = self.get_system_credential(system='monday', label=label)
        api_key = credentials['api_key']
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json',
            'API-Version': '2023-10'
        }

        return headers

    def get_activity_logs(self, board_id: int, start_date: str, end_date: str, column_ids: str = '', limit: int = 25):
        """
        See for the docs: https://developer.monday.com/api-reference/docs/activity-logs
        :param board_id: the ID of the board you want to get the activity logs from
        :param start_date: start date in YYYY-MM-DD format
        :param end_date: end date in YYYY-MM-DD format
        :param column_ids: optional list of column ID's where you want to get the status updates for. If empty, updates for all columns will be returned
        :param limit: amount of items to be returned. Default is 25
        """
        continue_loop = True
        page = 0
        df = pd.DataFrame()
        while continue_loop:
            page += 1
            payload = json.dumps({
                "query": f"query {{boards (ids: {board_id}) {{ activity_logs (from: \"{start_date}\", to: \"{end_date}\", limit: {limit}, page: {page}, column_ids: [\"{column_ids}\"]) {{ id event entity data user_id created_at }} }} }}"
            })
            if self.debug:
                print(payload)
            response = requests.request("POST", self.endpoint, headers=self.headers, data=payload)
            if self.debug:
                print(response.json())
            response.raise_for_status()
            response_length = len(response.json()['data']['boards'][0]['activity_logs'])
            if response_length > 0:
                df_temp = pd.json_normalize(response.json()['data']['boards'][0]['activity_logs'])
                df = pd.concat([df, df_temp], axis=0)
            if response_length < limit:
                continue_loop = False
        return df

    def get_users(self, limit: int = 50, fields: str = 'id name created_at email is_admin is_guest is_view_only is_pending enabled join_date title last_activity account {id}'):
        continue_loop = True
        page = 0
        df = pd.DataFrame()
        while continue_loop:
            page += 1
            payload = json.dumps({
                "query": f"query {{users (limit:{limit} page:{page}) {{ {fields} }} }}"
            })
            if self.debug:
                print(payload)
            response = requests.request("POST", self.endpoint, headers=self.headers, data=payload)
            if self.debug:
                print(response.json())
            response.raise_for_status()
            response_length = len(response.json()['data']['users'])
            if response_length > 0:
                df_temp = pd.json_normalize(response.json()['data']['users'])
                df = pd.concat([df, df_temp], axis=0)
            if response_length < limit:
                continue_loop = False
        return df

    def get_boards(self, limit: int = 50, fields: str = 'id name description board_kind board_folder_id state items_count'):
        continue_loop = True
        page = 0
        df = pd.DataFrame()
        while continue_loop:
            page += 1
            payload = json.dumps({
                "query": f"query {{boards (limit:{limit} page:{page}) {{ {fields} }} }}"
            })
            if self.debug:
                print(payload)
            response = requests.request("POST", self.endpoint, headers=self.headers, data=payload)
            if self.debug:
                print(response.json())
            response.raise_for_status()
            response_length = len(response.json()['data']['boards'])
            if response_length > 0:
                df_temp = pd.json_normalize(response.json()['data']['boards'])
                df = pd.concat([df, df_temp], axis=0)
            if response_length < limit:
                continue_loop = False
        return df

    def get_groups(self, board_id, fields: str = 'id title position archived deleted color'):
        """
        Get the groups from a board. Groups are groupings of tickets.
        :param board_id: mandatory field from monday.com
        :param fields: optional fields to be returned. Enter as one string without comma's. Default is id, title, position, archived, deleted and color
        """
        payload = json.dumps({
            "query": f"query {{boards (ids:{board_id}) {{groups {{ {fields} }} }} }}"
        })
        if self.debug:
            print(payload)
        response = requests.request("POST", self.endpoint, headers=self.headers, data=payload)
        if self.debug:
            print(response.json())
        response.raise_for_status()
        response_data = response.json()
        if isinstance(response_data.get('data'), dict):
            df = pd.json_normalize(response_data['data']['boards'][0]['groups'])
            return df
        else:
            return response

    def get_column_values(self, item_ids: list):
        """
        :param item_ids: all the items where you want to get the column values from
        """
        # Chunk in lists of 50 items since monday.com doesn't accept requests longer than 50 items
        items_list = (item_ids[pos:pos + 49] for pos in range(0, len(item_ids), 49))
        all_data = []

        for chunk in items_list:
            payload = {
                "query": f"query {{items (ids: {chunk} exclude_nonactive: false) {{id name updated_at column_values {{ column {{ title }} id text }} }} }}"
            }
            payload = json.dumps(payload)
            if self.debug:
                print(payload)
            response = requests.request("POST", self.endpoint, headers=self.headers, data=payload)
            if self.debug:
                print(response.json())
            response.raise_for_status()
            data = response.json()['data']

            # flatten the data
            flat_data = []
            for item in data['items']:
                row = {}
                row['item_id'] = item['id']
                row['item'] = item['name']
                row['updated_at'] = item['updated_at']
                for col in item['column_values']:
                    title = col['column']['title']
                    text = col['text']
                    row[title] = text
                flat_data.append(row)
            all_data.extend(flat_data)
        df = pd.DataFrame(all_data)
        return df

    def get_items(self,
                  board_id: int, limit: int = 50,
                  linked_board_id: int = None,
                  source_column_id: str = None,
                  target_column_id: str = None,
                  item_filter: list = None,
                  fields: str = 'id name created_at email group {id} parent_item {id} state subitems {id} updated_at creator_id'
                  ):
        """
        Get the items from a group. Be aware, we only got the item ID's in this request. Values should be received from a different url.
        :param board_id: mandatory field from monday.com
        :param linked_board_id: If you want to get fields from a linked board, enter that board ID here
        :param source_column_id: The column ID of the column on the CURRENT (board_id) board that links to the linked board. This is the column that contains the linked items.
        :param target_column_id: The column ID of the column on the LINKED (linked_board_id) board that contains the value you want to get.
        :param limit: amount of items to be returned. Default is 50
        :param item_filter: Optional filter to filter on specific items based on their ID. Give a list with ID's
        :param fields: optional fields to be returned. Enter as one string without comma's. Default is id, name, created_at, email, group {id}, parent_item {id}, state, subitems {id}, updated_at and creator_id
        """
        # Since monday.com doesn't accept requests, longer than 100 items, split up the request in multiple requests
        df = pd.DataFrame()
        # Create chunks of item_filter if it has more than 100 IDs
        if item_filter:
            item_filter_chunks = [item_filter[i:i + 100] for i in range(0, len(item_filter), 100)]
        else:
            item_filter_chunks = [None]

        for item_filter_chunk in item_filter_chunks:

            if item_filter_chunk and linked_board_id:
                if not source_column_id or not target_column_id:
                    raise ValueError('If you have filled the linked_board_id, you need to specify the source_column_id and target_column_id')
                payload = {"query":
                               f"query {{boards (ids:{board_id}) {{id items_page (limit: {limit}, query_params: {{ids: {item_filter_chunk} }}) "
                                    f"{{cursor items {{ {fields} linked_items (linked_board_id: {linked_board_id}, link_to_item_column_id: \"{source_column_id}\") {{ id column_values(ids: [\"{target_column_id}\"]) {{ id text value }} }} }} }} }} }}"}
            elif linked_board_id:
                if not source_column_id or not target_column_id:
                    raise ValueError('If you have filled the linked_board_id, you need to specify the source_column_id and target_column_id')
                payload = {"query":
                               f"query {{boards (ids:{board_id}) {{id items_page (limit: {limit}) {{cursor items {{ {fields} linked_items "
                               f"(linked_board_id: {linked_board_id}, link_to_item_column_id: \"{source_column_id}\") {{ id column_values(ids: [\"{target_column_id}\"]) {{ id text value }} }} }} }} }} }}"}
            elif item_filter_chunk:
                payload = {"query": f"query {{boards (ids:{board_id}) {{id items_page (limit: {limit}, query_params: {{ids: {item_filter_chunk} }}) {{cursor items {{ {fields} }} }} }} }}"}
            else:
                payload = {"query": f"query {{boards (ids:{board_id}) {{id items_page (limit: {limit}) {{cursor items {{ {fields} }} }} }} }}"}

            payload = json.dumps(payload)
            if self.debug:
                print(payload)
            continue_loop = True
            while continue_loop:
                response = requests.request("POST", self.endpoint, headers=self.headers, data=payload)
                if self.debug:
                    print(response.json())
                response.raise_for_status()
                data = response.json()['data']['boards'][0]['items_page']
                df_temp = pd.json_normalize(data['items'])
                df = pd.concat([df, df_temp])

                # Check if there is a next page
                cursor = data['cursor']
                if cursor:
                    if linked_board_id:
                        payload = json.dumps({
                            "query": f"query {{boards (ids:{board_id}) {{id items_page (limit: {limit}, cursor: \"{cursor}\") {{cursor items {{ {fields} linked_items (linked_board_id: {linked_board_id}, link_to_item_column_id: \"{source_column_id}\") {{ id column_values(ids: [\"{target_column_id}\"]) {{ id text value }} }} }} }} }} }}"
                        })
                    else:
                        payload = json.dumps({
                            "query": f"query {{boards (ids:{board_id}) {{id items_page (limit: {limit}, cursor: \"{cursor}\") {{cursor items {{ {fields} }} }} }} }}"
                        })
                else:
                    continue_loop = False

        return df

