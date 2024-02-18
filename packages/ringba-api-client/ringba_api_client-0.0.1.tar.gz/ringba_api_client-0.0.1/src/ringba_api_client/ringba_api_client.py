"""Main module."""
import os
import csv
import time
import logging
import requests
from io import BytesIO
from typing import List
from zipfile import ZipFile

from rest_wrapper import RestClient
from rest_wrapper.utilities import BearerTokenMixin


logger = logging.getLogger('ringba-api-client')


class RingbaApiClient(BearerTokenMixin, RestClient):
    base_url = 'https://api.ringba.com/v2'
    
    def __init__(self, api_key: str = None, account_id: str = None, *args, **kwargs):
        """ Initialize the Ringba API client. Optionally provide an `api_key` ad-hoc, or set your `RINGBA_API_TOKEN` 
        environment variable.

        :param api_key: a valid Ringba API key. defaults to None, can be overridden at the request level.
        :type api_key: str, optional
        :param account_id: a valid Ringba account ID. defaults to None, can be overridden at the request level.
        :type account_id: str, optional
        :raises KeyError: raised when both `api_key` is not provided and no `RINGBA_API_TOKEN` env variable is set.
        """
        
        try:
            self.api_key = api_key if api_key else os.environ['RINGBA_API_TOKEN']
        except KeyError:
            raise KeyError('Environment variable `RINGBA_API_TOKEN` not found and no `api_key` specified.')

        self._account_id = account_id if account_id else os.environ.get('RINGBA_ACCOUNT_ID')

        super(RingbaApiClient, self).__init__(*args, **kwargs)

    @property
    def account_id(self) -> str:
        return self._account_id

    @account_id.setter
    def account_id(self, account_id: str):
        self._account_id = account_id
    
    def get_accounts(self) -> requests.Response:
        """ GET v2/ringbaacounts """
        return self.get('ringbaaccounts')
    
    def get_buyers(self, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/Buyers

        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/Buyers'.format(account_id or self.account_id))
    
    def get_publishers(self, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/publishers

        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/publishers'.format(account_id or self.account_id))
    
    def get_publisher_invitations(self, publisher_id: int, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/affiliates/{publisher_id}/invitations

        :param publisher_id: ringba publisher id
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/affiliates/{}/invitations'.format(account_id or self.account_id, publisher_id))

    def get_publisher_references(self, publisher_id: str, account_id: str = None) -> requests.Response:
        """ GET v2/{}/Publishers/{account_id}/InboundReferences

        :param publisher_id: publisher ID
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/Publishers/{}/InboundReferences'.format(account_id or self.account_id, publisher_id))
    
    def get_campaigns(self, campaign_id: str = None, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/campaigns/{campaign_id}

        :param campaign_id: campaign ID to fetch. if omitted, returns all campaigns.
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        endpoint = '{}/campaigns/{}'.format(account_id or self.account_id, campaign_id if campaign_id else '')
        return self.get(endpoint)
    
    def get_call_log_columns(self, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/calllogs/columns

        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/calllogs/columns'.format(account_id or self.account_id))
    
    def get_report_status(self, report_id: str, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/calllogs/export/{report_id}

        :param report_id: generated report ID
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/calllogs/export/{}'.format(account_id or self.account_id, report_id))
    
    def get_csv_report(self, payload: dict, account_id: str = None) -> requests.Response:
        """ POST v2/{account_id}/calllogs/export/csv

        Waits for the job to finish, then fetches and returns the report.

        :param payload: csv report payload
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :raises KeyError: something was wrong with the Ringba status response
        :return: report response
        """
        resp = self.post('{}/calllogs/export/csv'.format(account_id or self.account_id), json=payload)
        report_id = resp.json().get('id')

        report_status = self.get_report_status(report_id)

        try:
            while report_status.json()['status'] != 'Ready':
                time.sleep(1)
                report_status = self.get_report_status(report_id)
            report_content = requests.get(report_status.json()['url'], stream=True)
            return report_content
        except KeyError as exc:
            logger.error('Error in Ringba Report Status call. Response: {}'.format(report_status.json()))
            raise exc
        except Exception as exc:
            raise exc
    
    def get_tags_for_filtering_call_log(self, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/calllogs/tags

        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/calllogs/tags'.format(account_id or self.account_id))
    
    def get_call_log(self, report_body: dict, account_id: str = None) -> requests.Response:
        """ POST v2/{account_id}/calllogs/tags
        
        :param report_body: a valid Ringba report body
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.post('{}/calllogs'.format(account_id or self.account_id), json=report_body)
    
    def get_call_details(self, inbound_call_id: str, account_id: str = None) -> requests.Response:
        """ POST v2/{account_id}/calllogs/detail

        :param inbound_call_id: ringba inbound call ID
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.post('{}/calllogs/detail'.format(account_id or self.account_id), json={'InboundCallIds': [inbound_call_id]})

    def get_bid_details_response(self, bid_id: str, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/rtb/bid/{bid_id}

        :param bid_id: RTB bid ID
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/rtb/bid/{}'.format(account_id or self.account_id, bid_id))
    
    def get_targets(self, target_id: str = None, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/targets/{target_id}

        :param target_id: Ringba target ID to fetch. if none provided, returns all
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/targets/{}'.format(account_id or self.account_id, target_id if target_id else ''))

    def create_targets(self, target_data: dict, account_id: str = None) -> requests.Response:
        """ POST v2/{account_id}/targets

        :param target_data: valid Ringba target configuration data
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.post('{}/targets'.format(account_id if account_id else self.account_id), json=target_data)
    
    def update_target(self, target_id: str, target_data: dict, account_id: str = None) -> requests.Response:
        """ PATCH v2/{account_id}/targets/{target_id}

        :param target_id: Ringba target ID
        :param target_data: valid Ringba target configuration
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.patch('{}/targets/{}'.format(account_id or self.account_id, target_id), json=target_data)
    
    def get_ring_trees(self, ring_tree_id: str = None, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/pingtrees/{ring_tree_id}

        :param ring_tree_id: Ringba ring tree ID. if none provided, returns all
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/pingtrees/{}'.format(account_id or self.account_id, ring_tree_id if ring_tree_id else ''))

    def get_ring_tree_targets(self, ring_tree_target_id: str = None, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/pingtreetargets/{ring_tree_target_id}

        :param ring_tree_target_id: Ringba ring tree target ID. if none provided, returns all
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/pingtreetargets/{}'.format(account_id or self.account_id, ring_tree_target_id if ring_tree_target_id else ''))
    
    def get_rtb_settings_for_publisher(self, campaign_id: str, publisher_id: int, account_id: str = None) -> requests.Response:
        """ GET v2/{account_id}/campaigns/{campaign_id}/rtb/publishers/{publisher_id}

        :param campaign_id: Ringba campaign ID
        :param publisher_id: Ringba publisher ID
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        return self.get('{}/campaigns/{}/rtb/publishers/{}'.format(account_id or self.account_id, campaign_id, publisher_id))
    
    def adjust_call_payout(self, inbound_call_id: str, payout_amount: float, account_id: str = None) -> requests.Response:
        """ POST v2/{account_id}/calls/payments

        :param inbound_call_id: inbound call ID to make adjustment for
        :param payout_amount: conversion payout amount
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        body = {
            'inboundCallId': inbound_call_id,
            'reason': 'Call payout adjusted by admin [LNXOpsBot]',
            'adjustPayout': True,
            'adjustPayoutByAmount': payout_amount

        }
        return self.post('{}/calls/payments'.format(account_id or self.account_id), json=body)

    def get_inbound_call_id_from_bid_id(self, ringba_bid_id: str, account_id: str = None) -> str:
        """ Provide a Ringba bid ID and return its corresponding inboundCallId

        :param ringba_bid_id: a Ringba bid ID
        :param account_id: ringba account ID, defaults to object property `account_id`, if set
        :return: requests.Response
        """
        resp = self.get_bid_details_response(bid_id=ringba_bid_id, account_id=account_id)
        winning_bid = [x for x in resp.json()['report']['records'][0]['events'] if x['name'] == 'RTBWinningBid'][0]
        bid_map = {x['name']: x['value'] for x in winning_bid['eventStrVals']}
        return bid_map['inboundCallId']

    @staticmethod
    def convert_report_content(content: bytes) -> List[dict]:
        """ Convert zipped csv content to a list of dictionaries. Provide the `content` of a given response.

        :param content: CSV-encoded bytes
        :type content: bytes
        :return: data as a list of dictionaries
        :rtype: List[dict]
        """
        zip_file = ZipFile(BytesIO(content))
        csv_text = zip_file.read(zip_file.namelist()[0]).decode('utf-8-sig')
        call_data = [{k: v for k, v in row.items()} for row in csv.DictReader(csv_text.splitlines(), skipinitialspace=True)]

        return call_data
