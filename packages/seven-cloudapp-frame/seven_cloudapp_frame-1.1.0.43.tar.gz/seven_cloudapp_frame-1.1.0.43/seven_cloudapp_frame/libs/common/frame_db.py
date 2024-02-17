# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2024-01-18 18:19:58
@LastEditTime: 2024-01-18 18:19:58
@LastEditors: HuangJianYi
:Description: 框架DB操作类
"""
from seven_framework.base_model import *
from seven_framework import *
from seven_cloudapp_frame.libs.common import *
from seven_cloudapp_frame.libs.customize.seven_helper import *

class FrameDbModel(BaseModel):

    def __init__(self, model_class, sub_table):
        """
        :Description: 框架DB操作类
        :param model_class: 实体对象类
        :param sub_table: 分表标识
        :last_editors: HuangJianYi
        """
        super(FrameDbModel,self).__init__(model_class, sub_table)

    def set_sub_table(self, object_id=''):
        """
        :description: 设置分表
        :param object_id:object_id
        :return:
        :last_editors: HuangJianYi
        """
        table_name = str(self.model_obj).lower()
        sub_table_config = share_config.get_value("sub_table_config",{})
        table_config = sub_table_config.get(table_name, None)
        if table_config and object_id:
            sub_table = SevenHelper.get_sub_table(object_id, table_config.get("sub_count", 10))
            if sub_table:
                # 数据库表名
                self.table_name = table_name.replace("_tb", f"_{sub_table}_tb")
        return self
    

