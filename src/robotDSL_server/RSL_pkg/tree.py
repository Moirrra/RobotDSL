class Node(object):
    """
    树节点
    """
    def __init__(self, value="", type=""):
        """
        构造函数
        :param value: 节点值
        :param type: 节点类型
        """
        self.value = value  # 节点值
        self.type = type  # 节点类型
        self.children = []  # 孩子节点列表

    def add(self, child):
        """
        添加子节点
        :param child: 子节点
        :return: None
        """
        self.children.append(child)

    def get_node(self, root, value, type):
        """
        查找节点
        :param root: 根节点，从这里开始查找
        :param value: 待查找节点的值
        :param type: 待查找节点的类型
        :return: 待查找节点
        """
        if root is None:
            return None
        elif root.value == value and root.type == type:
            return root
        else:
            for child in root.children:
                result = self.get_node(child,value,type)
                if result is not None:
                    return result
            return None


class StateNode(Node):
    def __init__(self, name):
        super(StateNode,self).__init__(name,'state')


class SpeakNode(Node):
    def __init__(self, expr_list):
        super(SpeakNode, self).__init__('speak', 'speak')
        for expr in expr_list:
            if expr[0] == '$':
                expr_node = VarNode(expr[1:])
            else:
                expr_node = StringNode(expr)
            self.add(expr_node)


class ListenNode(Node):
    def __init__(self, time):
        super(ListenNode, self).__init__('listen', 'listen')
        time_node = NumNode(time)
        self.add(time_node)


class BranchNode(Node):
    def __init__(self, answer, name):
        super(BranchNode, self).__init__('branch', 'branch')
        answer_node = StringNode(answer)
        goto_node = GotoNode(name)
        self.add(answer_node)
        self.add(goto_node)


class GotoNode(Node):
    def __init__(self, name):
        super(GotoNode, self).__init__(name, 'goto')


class ExitNode(Node):
    def __init__(self, name):
        super(ExitNode, self).__init__(name, 'exit')


class StringNode(Node):
    def __init__(self, value):
        super(StringNode, self).__init__(value, 'string')


class VarNode(Node):
    def __init__(self, value):
        super(VarNode, self).__init__(value, 'var')


class NumNode(Node):
    def __init__(self, value):
        super(NumNode, self).__init__(value, 'num')

