#!/usr/bin/env python
# coding=utf-8
import json
import logging

from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest

import Debug
import ResponseUtil


def get_domain_record_id(response):
    """
    :param response:
    :return:
    """
    response = json.loads(response)
    if response:
        domain_records = response["DomainRecords"]
        if domain_records:
            record = domain_records["Record"]
            if record and len(record) > 0:
                return record[0]["RecordId"]
    return None


def response_record_id(response):
    """
    :param response:
    :return:
    """
    response = json.loads(response)
    if response:
        return response["RecordId"]
    return None


class DomainUtil(object):

    def __init__(self, client=None):
        self.client = client

    @ResponseUtil.debug(Debug.debugEnable, None)
    def record_id(self, sub_domain):
        """
        :param sub_domain:
        :return:
        """
        request = DescribeSubDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_SubDomain(sub_domain)
        try:
            logging.info("Start to find domain record id for sub domain %s." % sub_domain)
            response = self.client.do_action_with_exception(request)
            if ResponseUtil.success(response):
                record = get_domain_record_id(str(response, encoding='utf-8'))
                if not record:
                    raise ValueError("Record ID NullPointException")
                logging.info("Found domain record id %s for sub_domain : %s." % (record, sub_domain))
                return True, record
            else:
                return False, str(response, encoding='utf-8')
        except Exception as e:
            logging.error("Failed to get description for domain %s" % sub_domain, e)
            return False, e

    @ResponseUtil.debug(Debug.debugEnable, None)
    def add(self, domain_type, rr, domain_name, value):
        """
        :param domain_type: A
        :param rr: hk
        :param domain_name: ***************
        :param value: ***************
        :return:
        """
        request = AddDomainRecordRequest()
        request.set_accept_format('json')
        request.set_Value(value)
        request.set_Type(domain_type)
        request.set_RR(rr)
        request.set_DomainName(domain_name)
        try:
            response = self.client.do_action_with_exception(request)
            if ResponseUtil.success(response):
                record_id = response_record_id(response)
                if record_id:
                    logging.info("Successfully add domain information for : %s.%s to %s" % (rr, domain, value))
                    return True, None
            else:
                return False, str(response, encoding='utf-8')
        except Exception as e:
            logging.error("Failed to add sub domain parse information for %s.%s to %s" % (rr, domain, value), e)
            return False, e

    @ResponseUtil.debug(Debug.debugEnable, None)
    def update(self, record_id, domain_type, rr, value):
        """
        :param record_id: ***************
        :param domain_type: A
        :param rr: hk
        :param value: ***************
        :return:
        """
        request = UpdateDomainRecordRequest()
        request.set_accept_format('json')
        request.set_Value(value)
        request.set_Type(domain_type)
        request.set_RR(rr)
        request.set_RecordId(record_id)
        try:
            response = self.client.do_action_with_exception(request)
            if ResponseUtil.success(response):
                record_id = response_record_id(response)
                if record_id:
                    logging.info("Successfully update domain parse information for %s to %s" % (record_id, value))
                    return True, None
            else:
                return False, str(response, encoding='utf-8')
        except Exception as e:
            logging.error("Failed to add sub domain parse information for %s to %s" % (record_id, value), e)
            return False, e

    def change(self, domain_type, rr, domain_name, eip):
        is_ok, record_id = self.record_id("%s.%s" % (rr, domain_name))
        if is_ok:
            return self.update(record_id, domain_type, rr, eip)
        else:
            return self.add(domain_type, rr, domain_name, eip)

