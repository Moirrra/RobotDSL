import sys
import time
import tkinter as tk
import tkinter.messagebox as messagebox
import random
import pickle
import json
from socket import *
from multiprocessing.pool import ThreadPool


class Client(object):
    """
    客户端，包扩通话界面和socket通信
    """
    def __init__(self, ip, port):
        """
        c = Client("127.0.0.1", 8888)
        :param ip: ip地址
        :param port: 端口号
        """
        # socket
        self.ip = ip
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.thread_pool = ThreadPool(5)
        # 用户信息
        self.user_id = str(random.randint(1, 10))
        # 脚本信息
        with open("data/ui_data.json", 'r', encoding='utf8') as fp:
            data = json.load(fp)
        fp.close()
        self.quick_dict = data["quick_btn"]
        self.mode_dict = data["mode"]
        # 界面主要参数
        self.window = tk.Tk()
        self.window.title('与客服机器人聊天中...')
        self.window.geometry('800x600')
        self.window.resizable(0, 0)  # 窗口大小固定
        # 容器
        self.frame_left = tk.Frame(self.window, width=660, height=580)
        self.frame_right = tk.Frame(self.window, width=120, height=580)
        self.frame_top = tk.Frame(self.frame_left, width=650, height=350)
        self.frame_list = tk.Frame(self.frame_left, width=650, height=30)
        self.frame_input = tk.Frame(self.frame_left, width=650, height=150)
        self.frame_bottom = tk.Frame(self.frame_left, width=650, height=30)
        self.frame_top.columnconfigure(0, weight=8)
        self.frame_top.columnconfigure(1, weight=1)
        self.frame_input.columnconfigure(0, weight=8)
        self.frame_input.columnconfigure(1, weight=1)
        self.frame_bottom.columnconfigure(0, weight=7)
        self.frame_bottom.columnconfigure(1, weight=1)
        # 放置容器
        self.frame_left.grid(row=0, column=0, padx=5, pady=2)
        self.frame_right.grid(row=0, column=1, padx=5, pady=2)
        self.frame_top.grid(row=0, column=0, padx=5, pady=2)
        self.frame_list.grid(row=1, column=0, padx=5, pady=2)
        self.frame_input.grid(row=2, column=0, padx=5, pady=2)
        self.frame_bottom.grid(row=3, column=0)
        # 固定容器大小
        self.frame_left.grid_propagate(0)
        self.frame_right.grid_propagate(0)
        self.frame_top.grid_propagate(0)
        self.frame_list.grid_propagate(0)
        self.frame_input.grid_propagate(0)
        self.frame_bottom.grid_propagate(0)
        # 标签
        self.lb_quick = tk.Label(self.frame_list, text='快捷操作:')
        self.lb_mode = tk.Label(self.frame_right, text='可切换的脚本:')
        self.lb_quick.grid(row=0, column=0, padx=2)
        self.lb_mode.grid(row=0, column=0, padx=5, pady=20)
        # 单选框
        self.mode = tk.StringVar()
        self.mode.set(list(self.quick_dict.keys())[0])
        self.display_mode()
        # 开始通话按钮
        rowcnt = len(self.mode_dict) + 1
        self.button_start = tk.Button(self.frame_right, text='开始通话', command=self.connect_server, width=10)
        self.button_start.grid(row=rowcnt, column=0, pady = 5, sticky=tk.W)
        # 服务器连接状态标签
        self.start_connection = False
        self.connect_state = tk.StringVar()
        self.connect_state.set("未连接")
        self.lb_connect = tk.Label(self.frame_right, textvariable=self.connect_state).grid(row=rowcnt+1, column=0, pady=5, sticky=tk.W)
        # 发送按钮
        self.button_send = tk.Button(self.frame_bottom, text='发送', command=self.send_msg, width=15)
        self.button_send.config(state=tk.DISABLED)  # 禁用按钮
        self.button_send.grid(row=0, column=1, padx=25, sticky=tk.E)
        # 对话框
        self.output = tk.Text(self.frame_top, state='disable')
        self.output.tag_config('self_msg', foreground='green', spacing3=5)
        self.output.tag_config('robot_msg', foreground='blue', spacing3=5)
        # 输入框
        self.input = tk.Text(self.frame_input)
        # 滚动条
        self.scrollbar_output = tk.Scrollbar(self.frame_top)
        self.scrollbar_output.config(command=self.output.yview)
        self.output.config(yscrollcommand=self.scrollbar_output.set)
        self.output.grid(row=0, column=0, sticky=tk.NSEW)
        self.scrollbar_output.grid(row=0, column=1, sticky=tk.NSEW)
        self.scrollbar_input = tk.Scrollbar(self.frame_input)
        self.scrollbar_input.config(command=self.input.yview)
        self.input.config(yscrollcommand=self.scrollbar_input.set)
        self.scrollbar_input.grid(row=0, column=1, sticky=tk.NSEW)
        self.input.grid(row=0, column=0, sticky=tk.NSEW)
        # 快捷选项
        self.button_quick = []
        self.display_quick_btn()
        # 关闭窗口时结束程序
        self.window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        # 显示窗口
        self.window.mainloop()

    def __del__(self):
        """
        析构函数
        :return:
        """
        self.socket.close()  # 套接字释放
        self.window.destroy()  # 销毁窗口

    def display_mode(self):
        """
        放置脚本单选框
        :return: None
        """
        rowcnt = 1
        for x, y in self.mode_dict.items():
            tk.Radiobutton(self.frame_right, text=x, variable=self.mode, value=y, command=self.display_quick_btn).grid(
                row=rowcnt, column=0, sticky=tk.W)
            rowcnt += 1

    def display_quick_btn(self):
        """
        布置快捷通话选项
        :return: None
        """
        print(self.mode.get())
        btn_cnt = len(self.quick_dict[self.mode.get()])
        for btn in self.button_quick:
            btn.destroy()
        self.button_quick = []
        self.click_quick = False
        for i in range(0, btn_cnt):
            item = self.quick_dict[self.mode.get()][i]
            t = item
            btn = tk.Button(self.frame_list, text=item, width=10)
            self.button_quick.append(btn)
            btn.bind("<ButtonRelease>", self.click_quick_btn)
            btn.grid(row=0, column=i + 1, padx=2)

    def click_quick_btn(self, event):
        """
        松开快捷选项的事件
        :param event:
        :return: None
        """
        self.input.delete('0.0', tk.END)
        self.input.insert(tk.END, event.widget['text'])

    def send_msg(self):
        """
        按下“发送”按钮的响应，显示消息并发送给服务器
        :return: None
        """
        # 显示消息在界面
        self.output.configure(state=tk.NORMAL)
        info_msg = "我:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        self.output.insert(tk.END, info_msg, 'self_msg')
        send_msg = self.input.get('0.0', tk.END) + '\n'
        self.output.insert(tk.END, send_msg, 'self_msg')
        self.input.delete('0.0', tk.END)
        self.output.configure(state=tk.DISABLED)
        # 发送消息给服务器
        send_msg = send_msg.rstrip()
        msg = {
            'flag': 'answer',
            'data': {
                'user-id': self.user_id,
                'message': send_msg
            }
        }
        self.socket.send(pickle.dumps(msg))

    def connect_server(self):
        """
        点击“开始通话”按钮的响应，尝试连接服务器
        :return:
        """
        try:
            self.socket.connect((self.ip, self.port))
            # print("Client Socket Connected Successfully!")
            first_msg = {
                'flag': 'first',
                'data': {
                    'user_id': self.user_id,
                    'script_name': self.mode.get()
                }
            }
            self.socket.send(pickle.dumps(first_msg))
            # 接收消息的线程
            self.thread_pool.apply_async(func=self.recv_msg)
        except:
            # print("Client Socket Connection Failed!")
            pass

    def recv_msg(self):
        """
        接收服务器的消息
        :return: None
        """
        while True:
            try:
                orign_data = self.socket.recv(1024)
                data = pickle.loads(orign_data)
                # print(data.get('flag'))
            except BlockingIOError:  # 未发送信息
                pass
            except ConnectionResetError:  # 服务器断开连接
                if self.start_connection:
                    print("ConnectionResetError")
                    self.connect_state.set("未连接")
                    self.start_connection = False
                    self.button_send.config(state=tk.DISABLED)  # 发送按钮禁用
                    self.button_start.config(state=tk.NORMAL)  # 通话按钮启用
                    self.socket.close()
                    messagebox.showwarning(title='警告', message='服务器连接断开')
                    break
            else:
                if data.get('flag') == 'repeat':  # 重复用户ID
                    messagebox.showerror(title='错误', message='重复'
                                                             '用户ID！')
                    self.window.destroy()
                    sys.exit(1)
                elif data.get('flag') == 'start':
                    self.connect_state.set("已连接")
                    self.start_connection = True
                    self.button_send.config(state=tk.NORMAL)  # 发送按钮恢复正常
                    self.button_start.config(state=tk.DISABLED)  # 通话按钮禁用
                elif not data:
                    messagebox.showerror(title='错误', message='服务器发送空消息！')
                    self.window.destroy()
                    sys.exit(1)
                else:   # 普通消息
                    # print(data)
                    self.thread_pool.apply_async(func=self.show_msg, args=(data,))


    def show_msg(self,data):
        """
        将服务器消息显示在页面上
        :param data: 服务器消息
        :return: None
        """
        if data['data']['message']:
            self.output.configure(state=tk.NORMAL)
            info_msg = "客服:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
            recv_msg = info_msg + data['data']['message'] + '\n\n'
            self.output.insert(tk.END, recv_msg, 'robot_msg')
            self.output.see(tk.END)
            self.output.configure(state=tk.DISABLED)