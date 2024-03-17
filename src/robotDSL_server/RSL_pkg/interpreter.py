from RSL_pkg.helper import *
class Interpreter(object):
    """
    解释器
    """
    def __init__(self, parser, user_id, script_name):
        """
        构造函数
        :param parser: 语法分析器
        :param user_id: 用户ID
        :param script_name: 脚本名称
        """
        self.user_id = user_id  # 用户ID
        self.parser = parser  # 语法分析器
        self.ASTtree = parser.tree  # 语法树
        self.helper = Helper(user_id, script_name)  # 数据查询
        self.entry_state = parser.symbol_table.entry_state  # 入口状态
        self.entry_node = self.ASTtree.get_node(self.ASTtree, self.entry_state, 'state')  # 入口状态节点
        self.answer = ""  # 最近用户输入






