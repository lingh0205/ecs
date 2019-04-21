# !/usr/bin/env python
# coding=utf-8
import json
import logging
import time

from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.ModifyInstanceAutoReleaseTimeRequest import ModifyInstanceAutoReleaseTimeRequest
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest

import Debug
import ResponseUtil


def get_instance_eip(response):
    """
    :param response:
    :return:
    """
    ecs_info = json.loads(response)
    if ecs_info:
        ecs_list = ecs_info["Instances"]["Instance"]
        if ecs_list and len(ecs_list) > 0:
            eip_list = ecs_list[0]["PublicIpAddress"]["IpAddress"]
            if ecs_list and len(ecs_list) > 0:
                return eip_list[0]


def get_instance_id(response):
    """
    :param response:
    :return:
    """
    response = json.loads(response)
    if response:
        instance_id_sets = response["InstanceIdSets"]
        if instance_id_sets:
            instance_id_set = instance_id_sets["InstanceIdSet"]
            if instance_id_set and len(instance_id_set) > 0:
                return instance_id_set[0]
    return None


def get_instance_list(response):
    """
    :param response:
    :return:
    """
    ecs_info = json.loads(response)
    if ecs_info:
        ecs_list = ecs_info["Instances"]["Instance"]
        if ecs_list and len(ecs_list) > 0:
            return [ecs["InstanceId"] for ecs in ecs_list if ecs["InternetChargeType"] == "PayByTraffic" ]
    return []


class EcsUtil(object):

    def __init__(self, client=None):
        self.client = client

    @ResponseUtil.debug(Debug.debugEnable, [])
    def search(self):
        """
        :return:
        """
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        try:
            response = self.client.do_action_with_exception(request)
            if ResponseUtil.success(response):
                instances = get_instance_list(str(response, encoding='utf-8'))
                if not instances or len(instances) <= 0:
                    raise ValueError("Instances NullPointException")
                logging.info("Get instances : %s." % instances)
                return True, instances
            else:
                return False, str(response, encoding='utf-8')
        except Exception as e:
            logging.error("Failed to get instances, cause by exception : ", e)
            return False, e

    @ResponseUtil.debug(Debug.debugEnable, None)
    def stop_and_delete(self, instance_id):
        """
        :argument instance_id
        :return:
        """
        request = StopInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(instance_id)
        try:
            response = self.client.do_action_with_exception(request)
            logging.info("Start to stop Ecs : %s" % instance_id)
            if ResponseUtil.success(response):
                logging.info("Start to delete Ecs : %s" % instance_id)

                time.sleep(60)

                request = DeleteInstanceRequest()
                request.set_accept_format('json')
                request.set_InstanceId(instance_id)
                response = self.client.do_action_with_exception(request)
                if ResponseUtil.success(response):
                    return True, None
                return False, str(response, encoding='utf-8')
            return False, str(response, encoding='utf-8')
        except Exception as e:
            logging.error("Failed to delete ecs, cause by exception : ", e)
            return False, e

    @ResponseUtil.debug(Debug.debugEnable, None)
    def release(self, instance_id, release_time):
        """
        :param instance_id:  ***************
        :param release_time:  2019-04-20T08:50:00Z  -> UTC date format
        :return:
        """
        request = ModifyInstanceAutoReleaseTimeRequest()
        request.set_accept_format('json')
        request.set_AutoReleaseTime(release_time)
        request.set_InstanceId(instance_id)
        try:
            logging.info("Start to release Ecs : %s at UTC time : %s" % (instance_id, release_time))
            response = self.client.do_action_with_exception(request)
            if ResponseUtil.success(response):
                return True, None
            else:
                return False, str(response, encoding='utf-8')
        except Exception as e:
            logging.error("Failed to release ecs, cause by exception : ", e)
            return False, e

    @ResponseUtil.debug(Debug.debugEnable, None)
    def create(self, template_id, template_name):
        """
        :argument template_id ***************
        :argument template_name ***************
        :return:
        """
        request = RunInstancesRequest()
        request.set_accept_format('json')
        request.set_LaunchTemplateName(template_name)
        request.set_LaunchTemplateId(template_id)
        try:
            logging.info("Start to create ecs instance for template %s." % template_name)
            response = self.client.do_action_with_exception(request)
            if ResponseUtil.success(response):
                instance_id = get_instance_id(str(response, encoding='utf-8'))
                if not instance_id:
                    raise ValueError("Instance ID NullPointException")
                logging.info("Successfully create instance %s with template %s." % (instance_id, template_name))
                return True, instance_id
            else:
                return False, str(response, encoding='utf-8')
        except Exception as e:
            logging.error("Failed to create ecs, cause by exception : ", e)
            return False, e

    @ResponseUtil.debug(Debug.debugEnable, None)
    def eip(self, instance_id):
        """
        :argument instance_id - ecs instance id ***************
        :return: ecs
        """
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_InstanceIds("['%s']" % instance_id)
        try:
            logging.info("Start to get eip for instance %s." % instance_id)
            response = self.client.do_action_with_exception(request)
            if ResponseUtil.success(response):
                eip = get_instance_eip(str(response, encoding='utf-8'))
                if not instance_id:
                    raise ValueError("Eip NullPointException")
                logging.info("Get eip : %s for instance : %s." % (eip, instance_id))
                return True, eip
            else:
                return False, str(response, encoding='utf-8')
        except Exception as e:
            logging.error("Failed to get eip for instance %s, cause by exception : " % instance_id, e)
            return False, e

