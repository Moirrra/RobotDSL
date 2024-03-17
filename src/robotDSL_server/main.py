from RSL_pkg import server


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 8889
    s = server.Server(ip, port)
