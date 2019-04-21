#!/usr/bin/env python
# coding=utf-8
import functools
import json
import logging
import time
import argparse
from aliyunsdkcore.client import AcsClient
import requests
from datetime import datetime, timedelta
from domain.Domain import DomainUtil
from ecs.Ecs import EcsUtil

# aliyun sdk auth
access_id = '***********'
access_secret = '***********'
region_id = '***************'

# ecs template
template_id = "***************"
template_name = "***************"

# domain
domain_type = "A"
prefix = 'hk'
domain_name = '***************'

# notify
token = '***************'
mobiles = [
    "***************"
]

ding_ding = "https://oapi.dingtalk.com/robot/send?access_token="

# logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def ding(token):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            markdown = func(*args, **kw)
            if token:
                url = "%s%s" % (ding_ding, token)
                message = {
                    "msgtype": "markdown",
                    "markdown": markdown,
                    "at": {
                        "atMobiles": mobiles,
                        "isAtAll": False
                    }
                }
                # send notify msg
                if notify(message, url):
                    logging.info("Successfully send ding msg : %s" % message)
                else:
                    logging.error("Failed to Send ding message.")
            return markdown
        return wrapper
    return decorator


def notify(msg, url):
    headers = {'content-type': 'application/json',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    response = requests.post(url, data=json.dumps(msg), headers=headers)
    obj = response.json()
    logging.info("Get Response : %s" % obj)
    if obj["errmsg"] == "ok":
        return True
    return False


@ding(token)
def create_instance(client):
    """
    :param client: AcsClient
    :return:
    """
    ecs_util = EcsUtil(client)
    domain_util = DomainUtil(client)
    # create ecs
    is_ok, instance_id = ecs_util.create(template_id, template_name)

    text = ""
    result = "#### ECS @Proxy 创建消息通知\n\n"
    if is_ok:
        result = result + "> 结果： 创建成功"
        text = text + "> 实例ID： %s\n\n" % instance_id

        time.sleep(10)

        is_ok, eip = ecs_util.eip(instance_id)

        if is_ok:
            text += "> 公网IP： %s\n\n" % eip

            # change sub domain parse record
            is_ok, err_msg = domain_util.change(domain_type, prefix, domain_name, eip)
            if is_ok:
                result = result + "，域名解析成功"
                text = text + "> 域名：%s.%s\n\n" % (prefix, domain_name)
            else:
                result = result + "， 域名解析失败"
                text = text + "> 原因： %s\n\n" % err_msg
        else:
            result = result + "， 获取EIP失败"
            text = text + "> 原因： %s\n\n" % eip
    else:
        result = result + "> 结果： 创建失败"
        text = text + "> 原因： %s\n\n" % instance_id

    text = "%s \n\n %s" % (result, text)

    markdown = {
        "title": "ECS创建通知",
        "text": text
    }

    return markdown


def utc():
    # release time must after 30 minutes
    utc_tm = datetime.utcnow() + timedelta(minutes=35)
    return utc_tm.strftime("%Y-%m-%dT%H:%M:%SZ")


@ding(token)
def release_instance(client):
    """
    :param client: AcsClient
    :return:
    """
    ecs_util = EcsUtil(client)
    is_ok, instances = ecs_util.search()

    success = []
    failed = []
    msgs = []
    for instance in instances:
        is_ok, err = ecs_util.stop_and_delete(instance)
        if is_ok:
            success.append(instance)
        else:
            failed.append(instance)
            msgs.append(err)

    text = "#### ECS @Proxy 释放消息通知\n\n"

    if success and len(success):
        text = text + "> 结果： 释放成功\n\n > 成功列表："
        text += "%s\n\n" % success
    elif failed and len(failed):
        text += "> 失败列表："
        text += "%s\n\n" % failed
        text += "\n\n > 失败原因：%s\n\n" % msgs
    else:
        text += "> 结果： 待释放为空\n\n"

    markdown = {
        "title": "ECS释放通知",
        "text": text
    }

    return markdown


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--create', action="store_true", dest="mode",
                        help='flag : means to create ecs instance')
    group.add_argument('-r', '--release', action="store_false", dest="mode",
                        help='flag : means to release ecs instance')
    args = parser.parse_args()
    client = AcsClient(access_id, access_secret, region_id)
    if args.mode:
        create_instance(client)
    else:
        release_instance(client)





