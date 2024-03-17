import json


class Helper(object):
    """
    数据查询类
    """
    def __init__(self, user_id, script_name):
        """
        h = Helper("2","online_shop_robot")
        :param user_id: 用户ID
        :param script_name: 脚本名称
        """
        self.user_id = user_id  # 用户ID
        self.script_name = script_name  # 脚本名称
        filepath = "./data/" + script_name + ".json"  # 数据文件路径
        with open(filepath, 'r', encoding='utf8') as fp:
            self.data = json.load(fp)
        fp.close()

    def get_value(self, var, answer=""):
        """
        查找变量对应数据
        :param var: 变量名
        :param answer: 用户输入
        :return: 变量对应数据
        """
        # 提取查找路径
        str_list = var.split('.')
        alist = []
        for item in str_list:
            if item == "answer":
                alist.append(answer)
            else:
                alist.append(item)
        result = self.data[self.user_id]
        for attr in alist:
            try:
                result = result[attr]
            except:
                result = None
                break
        return result