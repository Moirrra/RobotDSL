import pytest
from socket import *
import pickle
import random
import time
from RSL_pkg import server
from multiprocessing.pool import ThreadPool


@pytest.mark.parametrize(
    "ip,port",
    [('127.0.0.1',8888)]
)
def testServer(ip,port):
    thread_pool = ThreadPool(10)
    thread_pool.apply_async(func=testConnection, args=(ip, port))
    thread_pool.apply_async(func=testConnection, args=(ip, port))
    thread_pool.apply_async(func=testConnection, args=(ip, port))
    thread_pool.apply_async(func=testConnection, args=(ip, port))
    thread_pool.apply_async(func=testConnection, args=(ip, port))
    # server
    s = server.Server(ip, port)


def testConnection(ip, port, user_id, script_name):
    user_id = str(random.randint(1, 10))
    client = socket(AF_INET, SOCK_STREAM)
    thread_pool = ThreadPool(3)
    while True:
        try:
            client.connect((ip, port))
            first_msg = {
                'flag': 'first',
                'data': {
                    'user_id': user_id,
                    'script_name': "online_shop_robot"
                }
            }
            client.send(pickle.dumps(first_msg))
            thread_pool.apply_async(func=recv_msg,args=(client,user_id))
            break
        except BlockingIOError:  # 未发送信息
            pass
        except ConnectionResetError:  # 服务器断开连接
            pass

def recv_msg(client, user_id):
    print("recv_msg")
    # 自动应答
    while True:
        time.sleep(1)
        try:
            orign_data = client.recv(1024)
            data = pickle.loads(orign_data)
            print("recv from server: {}".format(data))
            if data.get('flag') == 'repeat':
                print("Same UserID")
                break
            elif data.get("flag") == "start":
                pass
            elif data['data']['message'] == "请输入您需要的服务：":
                print("1")
                answer = ["物流查询","退换货","投诉","催发货","结束服务"]
                index = random.randint(0, 4)
                msg = {
                    'flag': 'answer',
                    'data': {
                        'message': answer[index]
                    }
                }
                print(msg)
                client.send(pickle.dumps(msg))
            elif "请输入订单号" in data['data']['message']:
                msg = {
                    'flag': 'answer',
                    'data': {
                        'message': "12345-"+user_id
                    }
                }
                client.send(pickle.dumps(msg))
            elif "您的意见" in data['data']['message']:
                msg = {
                    'flag': 'answer',
                    'data': {
                        'message': "很久不发货"
                    }
                }
                client.send(pickle.dumps(msg))
            elif "五星好评" in data['data']['message']:
                break
            else:
                pass
        except BlockingIOError:  # 未发送信息
            pass
        except ConnectionResetError:  # 服务器断开连接
            break

if __name__ == '__main__':
    pytest.main(["-s","test_server.py"])