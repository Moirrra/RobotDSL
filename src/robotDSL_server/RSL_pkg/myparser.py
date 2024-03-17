import os
from RSL_pkg.tree import *

class SymbolTable(object):
    """
    符号表
    """
    def __init__(self):
        self.state_list = []    # 状态列表
        self.var_list = []      # 变量列表
        self.entry_state = ""   # 入口状态

    def register_state(self, state):
        """
        将状态名添加到符号表中
        :param state: 状态名
        :return: None
        """
        self.state_list.append(state)

    def register_var(self, var):
        """
        将变量名添加到符号表中
        :param var: 变量名
        :return: None
        """
        self.var_list.append(var)


class Parser(object):
    """
    语法分析器
    """
    def __init__(self, filepath):
        """
        构造函数
        :param filepath: 脚本路径
        """
        self.current_state = "" # 当前状态名
        self.current_state_node = None  # 当前状态节点
        self.symbol_table = SymbolTable()   # 符号表
        self.declaration = []   # 脚本的过程声明
        self.definition = []    # 脚本的过程定义
        self.filepath = filepath    # 脚本文件路径
        filename = os.path.basename(filepath).split('.')[0]  # 脚本名
        self.tree = Node(filename,'root')  # 语法树

    def get_tree(self):
        return self.tree

    def get_symbol_table(self):
        return self.symbol_table

    def run(self):
        """
        开始分析脚本
        :return: None
        """
        # 打开文件
        with open(self.filepath, mode='r', encoding='utf-8') as file:
            # print("open file")
            begin_dec = False
            read_dec = False
            # 读取文件，处理空行和注释,分成声明和定义
            for line in file:
                line = line.rstrip()
                newline = line.split()
                if newline and not newline[0][0] == '#':
                    if newline[0] == 'states':
                        begin_dec = True
                        continue
                    if begin_dec and newline[0] == 'end':
                        read_dec = True
                        continue
                    if read_dec:
                        self.definition.append(newline)
                    else:
                        self.declaration.append(newline)
        # 关闭文件
        file.close()
        self.parse_dec()
        self.parse_def()

    def parse_dec(self):
        """
        处理states声明
        :return: None
        """
        self.symbol_table.entry_state = self.declaration[0][0]
        for line in self.declaration:
            if line[0] == 'end':
                break
            # 语法树
            state = StateNode(line[0])
            self.tree.add(state)

    def parse_def(self):
        """
        处理state定义
        :return: None
        """
        for line in self.definition:
            self.parse_line(line)

    def parse_line(self, line):
        """
        处理每一行定义
        :param line: 待分析的一行脚本
        :return: None
        """
        if line[0] == 'state':
            self.parse_state(line)
        elif line[0] == 'speak':
            self.parse_speak(line)
        elif line[0] == 'listen':
            self.parse_listen(line)
        elif line[0] == 'branch':
            self.parse_branch(line)
        elif line[0] == 'goto':
            self.parse_goto(line)
        elif line[0] == 'exit':
            self.parse_exit(line)
        elif line[0] == 'end':
            pass
        else:
            print("error key")

    def parse_state(self, line):
        """
        分析 state token
        :param line: 待分析的一行脚本
        :return: None
        """
        if line[1] is not None:
            # 符号表
            self.symbol_table.register_state(line[1])
            self.current_state = line[1]
            # 语法树
            target_node = self.tree.get_node(self.tree, line[1], 'state')
            if target_node is not None:
                self.current_state_node = target_node

    def parse_speak(self, line):
        """
        分析 speak token
        :param line: 待分析的一行脚本
        :return: None
        """
        if len(line) > 1:
            expr_list = []
            for token in line[1:]:
                if token != '+':
                    expr_list.append(token)
                if token[0] == '$': #变量
                    self.symbol_table.register_var(token[1:])
            speak_node = SpeakNode(expr_list)
            self.current_state_node.add(speak_node)

    def parse_listen(self, line):
        """
        分析 listen token
        :param line: 待分析的一行脚本
        :return: None
        """
        time_limit = 30
        if len(line) == 2:
            time_limit = int(line[1])
        listen_node = ListenNode(time_limit)
        self.current_state_node.add(listen_node)

    def parse_branch(self, line):
        """
        分析 branch token
        :param line: 待分析的一行脚本
        :return: None
        """
        if len(line) == 3:
            branch_node = BranchNode(line[1], line[2])
            self.current_state_node.add(branch_node)

    def parse_goto(self, line):
        """
        分析 goto token
        :param line: 待分析的一行脚本
        :return: None
        """
        if len(line) == 2:
            # 语法树
            goto_node = GotoNode(line[1])
            self.current_state_node.add(goto_node)

    def parse_exit(self, line):
        """
        分析 exit token
        :param line: 待分析的一行脚本
        :return: None
        """
        exit_node = ExitNode(line[0])
        self.current_state_node.add(exit_node)