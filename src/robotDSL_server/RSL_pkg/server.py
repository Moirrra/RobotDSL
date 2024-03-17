import socket
import sys
import time
import pickle
import tkinter as tk
from socket import *
import RSL_pkg.myparser
import RSL_pkg.interpreter
from multiprocessing.pool import ThreadPool


class Server(object):
    """
    服务器，包括界面、socket通信、解释程序
    """
    def __init__(self, ip, port):
        """
        s = Server('127.0.0.1', 8888)
        :param ip: ip地址
        :param port: 端口号
        """
        self.ip = ip
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setblocking(False)  # 服务端套接字设置为非阻塞
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 设置端口复用
        self.socket.bind((self.ip, self.port))
        self.thread_pool = ThreadPool(10)
        # 客户端信息
        self.user_list = []  # 在线用户列表
        self.user_dict = {}  # 记录在线的用户信息
        self.parser_dict = {}  # 分析器字典 <script_name,parser>
        self.it_dict = {}  # 解释器字典 <user_id,interpreter>
        self.msg_dict = {}  # 用户的最新消息字典 <user_id,msg>
        # UI
        self.window = tk.Tk()
        self.window.title('客服机器人服务器')
        self.window.geometry('600x400')
        self.window.resizable(0, 0)
        # 容器
        self.frame_left = tk.Frame(self.window, width=140, height=380)
        self.frame_right = tk.Frame(self.window, width=440, height=380)
        self.frame_left.rowconfigure(0, weight=1)
        self.frame_left.rowconfigure(1, weight=10)
        self.frame_right.rowconfigure(0, weight=1)
        self.frame_right.rowconfigure(1, weight=10)
        # 固定容器大小
        self.frame_left.grid_propagate(0)
        self.frame_right.grid_propagate(0)
        # 放置容器
        self.frame_left.grid(row=0, column=0, padx=5, pady=2)
        self.frame_right.grid(row=0, column=1, padx=5, pady=2)
        # 标签
        self.lb_list = tk.Label(self.frame_left, text="在线用户：").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.lb_log = tk.Label(self.frame_right, text="日志").grid(row=0,column=0, sticky=tk.NSEW)
        # 列表
        self.list_var = tk.StringVar(value=self.user_list)
        self.list_var.set(self.user_list)
        self.listbox = tk.Listbox(self.frame_left, listvariable=self.list_var, selectmode=tk.BROWSE, width=18)
        self.listbox.grid(row=1, column=0, padx=(5,5), pady=10, sticky=tk.NSEW)
        # 文本框
        self.logbox = tk.Text(self.frame_right, state='normal', width=58, height=20, spacing3=5)
        # 滚动条
        self.scrollbar = tk.Scrollbar(self.frame_right)
        self.scrollbar.config(command=self.logbox.yview)
        self.logbox.config(yscrollcommand=self.scrollbar.set)
        self.logbox.grid(row=1, column=0, sticky=tk.NSEW)
        self.scrollbar.grid(row=1, column=2, sticky=tk.NSEW)
        # 关闭窗口时结束程序
        self.window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        # 分配线程运行run
        self.thread_pool.apply_async(func=self.run)
        # 显示窗口
        self.window.mainloop()

    def __del__(self):
        """
        析构函数
        :return:
        """
        self.socket.close()  # 套接字释放
        self.window.destroy()  # 销毁窗口

    def run(self):
        """
        主线程执行函数
        :return: None
        """
        self.write_log("self.run()\n")
        self.socket.listen(10)
        while True:
            try:
                client, client_addr = self.socket.accept()
                # 处理来自客户端的通话请求
                self.thread_pool.apply_async(func=self.recv_first_come, args=(client,))
            except BlockingIOError:
                pass
    def write_log(self, msg, tag=""):
        """
        服务端界面日志输出
        :param msg: 日志内容
        :param tag: 日志类型标签
        :return: None
        """
        time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        log = time_stamp + msg + '\n\n'
        self.logbox.configure(state=tk.NORMAL)
        self.logbox.insert(tk.END, log, tag)
        self.logbox.see(tk.END)  # 自动滚屏至最底
        self.logbox.configure(state=tk.DISABLED)

    """
    socket通信模块
    """
    def recv_first_come(self, client):
        """
        处理客户端的第一条信息，根据脚本创建语法树
        :param client: 客户端套接字
        :return: None
        first_msg = {
            'flag': 'basic',
            'data': {
                'user_id': user_id,
                'script_name': self.mode.get()
            }
        }
        """
        self.write_log("self.recv_first_come()\n")
        recv_msg = client.recv(1024)
        first_msg = pickle.loads(recv_msg)
        self.write_log("recv from client:\n{}\n".format(first_msg))
        if first_msg and first_msg.get('flag') == 'first':
            user_id = first_msg['data']['user_id']
            if user_id in self.user_list:  # 用户id重复，报错
                send_error_msg = {
                    'flag': 'repeat',
                    'data': {}
                }
                self.write_log("send to client:\n{}\n".format(send_error_msg))
                client.send(pickle.dumps(send_error_msg))
            else: # 处理通话请求
                script_name = first_msg['data']['script_name']
                client.setblocking(False)  # 真正存储在在线字典里的用户套接字是个非阻塞的
                self.user_dict[user_id] = {
                    'name': None,
                    'socket': client
                }
                self.user_list.append(user_id)
                self.list_var.set(self.user_list)
                send_first_msg = {
                    'flag': 'start',
                    'data': {}
                }
                client.send(pickle.dumps(send_first_msg))
                self.write_log("send to client:\n{}".format(send_first_msg))

                # 创建分析器并构造语法树
                filepath = '.\\script\\' + script_name + '.txt'
                self.write_log(filepath)
                if self.parser_dict.get(script_name) is None:
                    self.parser_dict[script_name] = RSL_pkg.myparser.Parser(filepath)  # 保存分析器
                    self.write_log("Parser()")
                    self.parser_dict[script_name].run()  # 构造语法树
                    self.write_log("Parser.run()")
                self.thread_pool.apply_async(func=self.interpret, args=(user_id, script_name))
                self.write_log("self.thread_pool.apply_async(func=self.interpret, args=(user_id, script_name))")
        else:
            client.close() #数据无效
            self.write_log("client.close()")

    def recv_send_msg(self, user_id, time_limit):
        """
        接收客户端消息
        :param user_id: 客户端用户ID
        :param time_limit: 接收消息时间限制
        :return: 客户端的用户输入
        """
        cnt = 0  # 计时
        client = self.user_dict[user_id]['socket']  # 获得客户端套接字
        while cnt < time_limit:
            try:
                recv_msg = client.recv(1024)
                clear_msg = pickle.loads(recv_msg)
                self.msg_dict[user_id] = clear_msg['data']['message']
                self.write_log("当前用户：{}\n输入：{}\n用时：{}\n".format(user_id,clear_msg,cnt))
                return self.msg_dict[user_id]
            except BlockingIOError:  # 未发送信息
                time.sleep(1)
                cnt += 1
            except ConnectionResetError:  # 客户端断开连接
                self.write_log("用户{}断开连接".format(user_id))
                client.close()
                self.write_log("client.close()\n")
                # 更新数据
                del self.user_dict[user_id]  # 删去用户字典信息
                self.user_list.remove(user_id)  # 删去用户列表信息
                self.list_var.set(self.user_list)  # 更新在线用户显示
                return
        # 超时未收到用户信息
        self.msg_dict[user_id] = "#silence"
        self.write_log("当前用户：{}\n输入超时\n用时：{}\n".format(user_id, cnt))
        return self.msg_dict[user_id]

    def send_client_msg(self, user_id, msg):
        """
        发送消息至客户端
        :param user_id: 客户端的用户ID
        :param msg: 发送的消息
        :return: None
        """
        client = self.user_dict[user_id]['socket']  # 获得客户端套接字
        send_msg = {
            'flag': 'send',
            'data': {
                'message': msg
            }
        }
        time.sleep(1)
        client.send(pickle.dumps(send_msg))
        self.write_log("send to client:\n{}".format(send_msg))

    """
    解释器
    """
    def interpret(self, user_id, script_name):
        """
        解释程序
        :param user_id: 客户端的用户ID
        :param script_name: 脚本名称
        :return: None
        """
        self.write_log("self.interpret({},{})".format(user_id,script_name))
        # 创建解释器
        it = RSL_pkg.interpreter.Interpreter(self.parser_dict[script_name], user_id, script_name)
        self.it_dict[user_id] = it  # 保存解释器
        self.visit_state_node(it.entry_node, user_id)  # 开始解释

    def visit_state_node(self, node, user_id):
        """
        访问state节点
        :param node: 节点
        :param user_id: 客户端的用户ID
        :return: None
        """
        self.write_log("self.visit_state_node()")
        # 遍历子节点
        for child in node.children:
            if child.type == 'speak':
                self.visit_speak_node(child, user_id)
            elif child.type == 'listen':
                self.visit_listen_node(child, user_id)
            elif child.type == 'branch':
                self.visit_branch_node(child, user_id)
            elif child.type == 'goto':
                self.visit_goto_node(child, user_id)
            elif child.type == 'exit':
                self.visit_exit_node(child, user_id)

    def visit_speak_node(self, node, user_id):
        """
        访问speak节点
        :param node: 节点
        :param user_id: 客户端的用户ID
        :return: None
        """
        self.write_log("self.visit_speak_node()")
        output = ""
        it = self.it_dict[user_id]
        for child in node.children:
            if child.type == 'string':
                output += child.value[1:-1]
            elif child.type == 'var':
                if "answer" in child.value:
                    val = it.helper.get_value(child.value, it.answer)
                else:
                    val = it.helper.get_value(child.value)
                if val is not None:
                    output += str(val)
                else:
                    output = "您的输入有误，无法查询到数据！"
                    break
        self.send_client_msg(user_id, output)

    def visit_listen_node(self, node, user_id):
        """
        访问listen节点
        :param node: 节点
        :param user_id: 客户端的用户ID
        :return: None
        """
        self.write_log("self.visit_listen_node()")
        it = self.it_dict[user_id]
        time_limit = node.children[0].value
        # 处理客户端消息
        it.answer = self.recv_send_msg(user_id, time_limit)
        self.msg_dict[user_id] = ""  # 获取后刷新

    def visit_branch_node(self, node, user_id):
        """
        访问branch节点
        :param node: 节点
        :param user_id: 客户端的用户ID
        :return: None
        """
        it = self.it_dict[user_id]
        keyword = node.children[0].value
        self.write_log("self.visit_branch_node()\nkeyword={}".format(keyword))
        # 比较当前输入和分支选项keyword
        if keyword == it.answer or keyword == "#other":
            self.visit_goto_node(node.children[1], user_id)

    def visit_goto_node(self, node, user_id):
        """
        访问goto节点
        :param node: 节点
        :param user_id: 客户端的用户ID
        :return: None
        """
        self.write_log("self.visit_goto_node()")
        it = self.it_dict[user_id]
        # 寻找下一个状态节点
        next_state_node = it.ASTtree.get_node(it.ASTtree, node.value, 'state')
        self.visit_state_node(next_state_node, user_id)

    def visit_exit_node(self, node, user_id):
        """
        访问exit节点
        :param node: 节点
        :return: None
        """
        self.write_log("self.visit_exit_node()")
        del self.it_dict[user_id]  # 删除解释器
        client = self.user_dict[user_id]["socket"]
        self.write_log("用户{}断开连接".format(user_id))
        client.close()
        self.write_log("client.close()\n")
        # 更新数据
        del self.user_dict[user_id]  # 删去用户字典信息
        self.user_list.remove(user_id)  # 删去用户列表信息
        self.list_var.set(self.user_list)  # 更新在线用户显示