# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2023-02-10 09:28:07
@LastEditTime: 2023-12-04 11:05:01
@LastEditors: HuangJianYi
@Description: console引用
"""
# 框架引用
from seven_framework.console.base_console import *
from seven_cloudapp_frame.libs.common import *

# 初始化配置,执行顺序需先于调用模块导入
share_config.init_config("share_config.json")  # 全局配置,只需要配置一次


work_process_date_dict = {} # 作业心跳监控时间

def heart_beat_monitor(work_name, interval_time=30, data={}, check_time=60, redis_config_dict=None):
    """
    :description: 作业心跳监控
    :param work_name: 作业名称
    :param interval_time: 上报间隔时间，单位：秒
    :param data: 数据字典
    :param check_time: 预警间隔时间，单位：分钟
    :param redis_config_dict: redis配置
    :return: 
    :last_editors: HuangJianYi
    """
    from seven_cloudapp_frame.libs.customize.redis_helper import RedisExHelper
    is_heart_beat_monitor = share_config.get_value("is_heart_beat_monitor",True)
    if is_heart_beat_monitor == True:
        try:
            is_init = False
            now_date = TimeHelper.get_now_format_time()
            process_date = work_process_date_dict.get(work_name)
            if not process_date:
                work_process_date_dict[work_name] = now_date
                process_date = now_date
                is_init = True
            if abs(TimeHelper.difference_seconds(process_date, now_date)) > interval_time or is_init == True:
                RedisExHelper.init(config_dict=redis_config_dict).set(f"heart_beat_monitor:{work_name}", JsonHelper.json_dumps({"process_date":now_date,"check_time":check_time,"data":data}), 30*24*3600)
                work_process_date_dict[work_name] = now_date
        except Exception as ex:
            logger_error.error(f"{work_name}-作业心跳监控异常,ex:{traceback.format_exc()}")

def heart_beat_check(redis_config_dict=None, wx_send_key=""):
    """
    :description: 作业心跳检测
    :param redis_config_dict: redis配置
    :param wx_send_key: 企业微信群推送密钥
    :return: 
    :last_editors: HuangJianYi
    """
    from seven_cloudapp_frame.libs.customize.redis_helper import RedisExHelper
    try:
        keys = []
        redis_init = RedisExHelper.init(config_dict=redis_config_dict)
        match_result = redis_init.scan_iter(match=f'heart_beat_monitor:*')
        for item in match_result:
            keys.append(item)
        if len(keys) > 0:
            redis_init.delete(*keys)

        while True:
            try:
                time.sleep(60)
                redis_init = RedisExHelper.init(config_dict=redis_config_dict)
                match_result = redis_init.scan_iter(match=f'heart_beat_monitor:*')
                for item in match_result:
                    work_name = item
                    info_json = redis_init.get(work_name)
                    if info_json:
                        info = json.loads(info_json)
                        check_time = int(info.get("check_time", 0))
                        process_date = info.get("process_date","")
                        if process_date and check_time > 0:
                            now_date = TimeHelper.get_now_format_time()
                            if abs(TimeHelper.difference_minutes(process_date, now_date)) > check_time:
                                if not wx_send_key:
                                    logger_error.error(f"{work_name}-作业没有检测到心跳,最后上报时间：{process_date}")
                                else:
                                    webhook = WorkWechatWebhookHelper(wx_send_key)
                                    webhook.send_webhook_message_markdown(f"{work_name}-作业没有检测到心跳,最后上报时间：{process_date}")

            except Exception as ex:
                logger_error.error(f"{work_name}-作业心跳检测异常,ex:{traceback.format_exc()}")
    except Exception as ex:    
        logger_error.error(f"{work_name}-作业心跳检测异常,ex:{traceback.format_exc()}")

