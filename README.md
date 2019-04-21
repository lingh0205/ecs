# 创建ECS & 添加域名解析

## Step 1. 配置
### 1. 阿里云SDK鉴权  
```text
位置： Operator.py  
配置项： 
access_id = '***********'  
access_secret = '***********'  
region_id = '***************'  
```  

### 2. 设置ECS创建模板
```text
位置： Operator.py  
配置项： 
template_id = "***************"  
template_name = "***************"   
```  

### 3. 设置域名解析配置
```text
位置： Operator.py  
配置项： 
domain_type = "A"   
prefix = 'hk'  
domain_name = '***************'  
```  

### 4. 配置通知
```text
位置： Operator.py  
配置项： 
token = '***************'  
mobiles = [  
    "***************"  
]
``` 

## Step 2. 关闭调试开关
```text
位置： Debug.py  
配置项： 
debugEnable = True  
```  

## Step 3. 操作  
### 1. 创建ECS  
```text
# 执行命令： 
python Operator.py -c  
# OR  
python Operator.py --create  
```
执行日志如下：
```text
2019-04-21 11:47:22,505 - root - INFO - Start to create ecs instance for template ************.
2019-04-21 11:47:24,212 - root - INFO - Get Response : {"RequestId":"********************","InstanceIdSets":{"InstanceIdSet":["i-************"]}}
2019-04-21 11:47:24,212 - root - INFO - Successfully create instance i-************ with template ************.
2019-04-21 11:47:34,212 - root - INFO - Start to get eip for instance ************.
2019-04-21 11:47:34,379 - root - INFO - Get Response : ......
2019-04-21 11:47:34,379 - root - INFO - Get eip : xxx.xxx.xxx.xxx for instance : i-************.
2019-04-21 11:47:34,379 - root - INFO - Start to find domain record id for sub domain xx.xxxxx.xxx.
2019-04-21 11:47:34,489 - root - INFO - Get Response : .......
2019-04-21 11:47:34,489 - root - INFO - Found domain record id ************ for sub_domain : ************.
2019-04-21 11:47:35,324 - root - INFO - Get Response : .......
2019-04-21 11:47:35,325 - root - INFO - Successfully update domain parse information for ********** to xxx.xxx.xxx.xxx
2019-04-21 11:47:35,631 - root - INFO - Get Response : {'errmsg': 'ok', 'errcode': 0}
2019-04-21 11:47:35,632 - root - INFO - Successfully send ding msg : {'msgtype': 'markdown', 'markdown': {'title': 'ECS创建通知', 'text': '#### ECS @Proxy 创建消息通知\n\n> 结果： 创建成功，域名解析成功 \n\n > 实例ID： i-xxxxxxxxxxxxxxxx\n\n> 公网IP： xxx.xxx.xxx.xxx\n\n> 域名：xx.xxxxx.xxx\n\n'}, 'at': {'atMobiles': ['***********'], 'isAtAll': False}}
```  

### 2. 释放ECS  
```text
# 执行命令： 
python Operator.py -r  
# OR  
python Operator.py --release   
```
执行日志如下：
```text
2019-04-21 11:56:27,283 - root - INFO - Get Response : .......
2019-04-21 11:56:27,284 - root - INFO - Get instances : ['i-************'].
2019-04-21 11:56:27,468 - root - INFO - Start to stop Ecs : i-************
2019-04-21 11:56:27,468 - root - INFO - Get Response : {"RequestId":"**********************"}
2019-04-21 11:56:27,468 - root - INFO - Start to delete Ecs : i-************
2019-04-21 11:57:27,906 - root - INFO - Get Response : {"RequestId":"****************"}
2019-04-21 11:57:28,222 - root - INFO - Get Response : {'errmsg': 'ok', 'errcode': 0}
2019-04-21 11:57:28,222 - root - INFO - Successfully send ding msg : {'msgtype': 'markdown', 'markdown': {'title': 'ECS释放通知', 'text': "#### ECS @Proxy 释放消息通知\n\n> 结果： 释放成功\n\n > 成功列表：['i-xxxxxxxxxxxxxxxxxx']\n\n"}, 'at': {'atMobiles': ['**********'], 'isAtAll': False}}
```