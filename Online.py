import random

import numpy as np
import requests
import socket
import threading
import json
import time  # 导入时间模块，用于延时等待
from flask import Flask, jsonify, request
import logging
from Environment import Env

logging.getLogger('werkzeug').setLevel(logging.ERROR)

def get_internal_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 无需可达，仅用于获取内网IP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class Server:
    def __init__(self):
        # 1. 将Flask app作为实例属性，而非类属性
        self.app = Flask(__name__)
        self.open_test = False
        self.my_ip = get_internal_ip()
        self.players_list = {1: self.my_ip}
        self.round_id = None

        self.invitation = None
        self.my_client = None
        self.my_env = None
        self.accept = False
        self.winner = None

        # 2. 手动绑定路由与视图函数（闭包形式，确保访问实例属性self.open_test）
        self._register_routes()

    def bind(self, client=None, env=None):
        if client:
            self.my_client = client
        if env:
            self.my_env = env

    def init(self):
        # 1. 将Flask app作为实例属性，而非类属性
        self.app = Flask(__name__)
        self.open_test = False
        self.my_ip = get_internal_ip()
        self.players_list = {1: self.my_ip}
        self.round_id = None

        self.invitation = None
        self.my_client.init()
        self.my_env.init()
        self.accept = False
        self.winner = None

        # 2. 手动绑定路由与视图函数（闭包形式，确保访问实例属性self.open_test）
        self._register_routes()

    def _register_routes(self):
        """手动注册所有路由，通过闭包绑定实例self"""
        # 根路由
        @self.app.route('/', methods=['GET'])
        def visit():
            if self.open_test and len(self.players_list) < 2:
                from_ip = request.args.get('from')
                client_ip = request.remote_addr
                # print(from_ip)
                return f"{client_ip}"  # 合法响应：字符串
            else:
                return "服务未开启（open_test=False）", 403  # 合法响应：字符串+状态码

        @self.app.route('/join', methods=['GET'])
        def join():
            if self.open_test:
                from_ip = request.args.get('from')
                # print(f'来自：{from_ip}，的 join 请求')

                self.invitation = from_ip
                if self.accept:
                    self.my_env.init()

                    self.my_client.server_ip = self.my_ip

                    if len(self.players_list) == 2:
                        # print(self.players_list)
                        print('玩家已满，游戏开启')

                    self.players_list[0] = from_ip
                    self.round_id = random.randint(0, 1)
                    placeholder_json = {
                        "command": 'join',
                        'you_round': 0,
                    }
                    return jsonify(placeholder_json)
                else:
                    placeholder_json = {
                        "command": 'join',
                        'you_round': None,
                    }
                    return jsonify(placeholder_json)
            else:
                return jsonify({"error": "服务未开启"}), 403

        @self.app.route('/join_over', methods=['GET'])
        def join_over():
            self.invitation = None
            return jsonify({"command": "join_over"})

        @self.app.route('/get_ground', methods=['GET'])
        def get_ground():
            from_ip = request.args.get('from')
            if self.open_test and len(self.players_list) == 2 and from_ip in list(self.players_list.values()):
                # print(f'来自：{from_ip}，的 get_ground 请求')
                placeholder_json = {
                    "command": 'get_ground',
                    'ground': self.my_env.ground,
                    'round_id': self.my_env.round_id,
                    'winner': self.winner,
                    'upgrade': (self.my_env.upgrade, self.my_env.round_id)
                }
                self.winner = self.my_env.winner
                return jsonify(placeholder_json)
            else:
                return jsonify({"error": "服务未开启"}), 403

        @self.app.route('/get_f_ground', methods=['GET'])
        def get_f_ground():
            from_ip = request.args.get('from')
            if self.open_test and len(self.players_list) == 2 and from_ip in list(self.players_list.values()):
                # print(f'来自：{from_ip}，的 get_f_ground 请求')
                placeholder_json = {
                    "command": 'get_ground',
                    'ground': self.my_env.get_flip_ground(),
                    'round_id': self.my_env.round_id,
                    'winner': self.winner,
                    'upgrade': (self.my_env.upgrade, self.my_env.round_id)
                }
                self.winner = self.my_env.winner
                return jsonify(placeholder_json)
            else:
                return jsonify({"error": "服务未开启"}), 403

        @self.app.route('/revoke', methods=['GET'])
        def revoke():
            from_ip = request.args.get('from')
            if self.open_test and len(self.players_list) == 2 and from_ip in list(self.players_list.values()):
                # print(f'来自：{from_ip}，的 revoke 请求')
                placeholder_json = {
                    "command": 'revoke',
                }
                self.my_env.revoke()
                return jsonify(placeholder_json)
            else:
                return jsonify({"error": "服务未开启"}), 403

        @self.app.route('/surrender', methods=['GET'])
        def surrender():
            from_ip = request.args.get('from')
            if self.open_test and len(self.players_list) == 2 and from_ip in list(self.players_list.values()):
                my_round = request.args.get('my_round')
                # print(f'来自：{from_ip}，的 revoke 请求')
                placeholder_json = {
                    "command": 'surrender',
                    "winner": 1 - int(my_round)
                }
                self.winner = 1 - int(my_round)
                self.my_env.revoke()
                return jsonify(placeholder_json)
            else:
                return jsonify({"error": "服务未开启"}), 403

        @self.app.route('/upgrade', methods=['GET'])
        def upgrade():
            from_ip = request.args.get('from')
            if self.open_test and len(self.players_list) == 2 and from_ip in list(self.players_list.values()):
                chess_type = request.args.get('chess_type')
                # print(f'来自：{from_ip}，的 revoke 请求')
                placeholder_json = {
                    "command": 'upgrade',
                }
                self.my_env.upgrade_pawn(chess_type)
                return jsonify(placeholder_json)
            else:
                return jsonify({"error": "服务未开启"}), 403

        @self.app.route('/get_target', methods=['GET'])
        def get_target():
            from_ip = request.args.get('from')
            if self.open_test and len(self.players_list) == 2 and from_ip in list(self.players_list.values()):
                # print(f'来自：{from_ip}，的 get_target 请求')
                grid = request.args.get('grid')
                result = self.my_env.get_move(grid)
                placeholder_json = {
                    "command": 'get_target',
                    "target": result
                }
                return jsonify(placeholder_json)
            else:
                return jsonify({"error": "服务未开启"}), 403

        @self.app.route('/move', methods=['GET'])
        def move():
            from_ip = request.args.get('from')
            if self.open_test and len(self.players_list) == 2 and from_ip in list(self.players_list.values()):
                grid_0, grid_1 = request.args.get('grid0'), request.args.get('grid1')  # 获取第一个元素
                # print(f'来自：{from_ip}，的 move 请求，起始：{grid_0}；终点：{grid_1}')
                response_data = {
                    "command": 'move'
                }
                if grid_0 and grid_1:
                    grids = (grid_0, grid_1)
                    response_data["grids"] = list(grids)  # 元组转列表兼容JSON

                    result = self.my_env.move(grid_0, grid_1)
                    response_data['result'] = result
                return jsonify(response_data)
            else:
                return jsonify({"error": "服务未开启"}), 403

    def _run_server(self):
        host_ip = get_internal_ip()
        print(f"Flask服务器启动中，地址：http://{host_ip}:2394")
        self.app.run(host=host_ip, port=2394, debug=False)

    def run_server(self):
        threading.Thread(target=self._run_server, daemon=True).start()

class Client:
    def __init__(self, server):
        self.my_server = server
        self.my_ip = get_internal_ip()
        self.target_port = 2394
        self.request_test = False
        self.server_ip = None
        self.join = False
        self.scan_list = []
        self.scan_over = True

    def init(self):
        self.my_ip = get_internal_ip()
        self.target_port = 2394
        self.request_test = False
        self.server_ip = None
        self.join = False
        self.scan_list = []
        self.scan_over = True

    def get_request(self, url, timeout, target_ip):
        try:
            response = requests.get(url, timeout=timeout)
            result = response.text
            if target_ip in result:
                # print(f'扫描到服务器：{target_ip}')
                self.request_test = True
                self.scan_list.append(target_ip)
        except Exception as e:
            pass

    def scan(self):
        self.scan_list = []
        self.scan_over = False
        self.request_test = False
        for i in range(2, 256):
            if self.request_test:
                break
            target_ip_parts = self.my_ip.split('.')
            target_ip_parts[3] = str(i)
            target_ip = ".".join(target_ip_parts)

            url = f"http://{target_ip}:{self.target_port}"

            threading.Thread(target=self.get_request, args=(url, 1, target_ip), daemon=True).start()
        self.scan_over = True

    def send_command(self, command, grids=None, grid=None, my_round=None, chess_type=None):
        if not self.server_ip:
            print("未找到可用服务器")
            return None
        try:
            # 基础URL构建
            base_url = f"http://{self.server_ip}:{self.target_port}/{command}"

            # 核心：如果是move指令且传递了二元元组，拼接查询参数
            if command == 'move':
                if not grids:
                    raise ValueError("move指令必须传入移动的起点和终点！")
                else:
                    # 校验：确保params_tuple是二元元组
                    if isinstance(grids, tuple) and len(grids) == 2:
                        # 拆分元组元素，拼接为查询字符串（tup1、tup2对应服务器端的参数名）
                        grid0, grid1 = grids
                        url = f"{base_url}?&from={self.my_ip}&grid0={grid0}&grid1={grid1}"
                    else:
                        url = base_url
            elif command == 'join':
                url = f"{base_url}?&from={self.my_ip}"
            elif command == 'get_target':
                url = f"{base_url}?&from={self.my_ip}&grid={grid}"
            elif command == 'surrender':
                url = f"{base_url}?&from={self.my_ip}&my_round={my_round}"
            elif command == 'upgrade':
                url = f"{base_url}?&from={self.my_ip}&chess_type={chess_type}"
            else:
                url = f"{base_url}?&from={self.my_ip}"

            response = requests.get(url=url, timeout=1)
            result = response.text
            return json.loads(result)
        except Exception as e:
            print(f"指令{command}请求失败：{e}")
            return None

if __name__ == '__main__':
    env = Env()

    # 启动服务器
    server = Server(env)
    server.open_test = True
    server.run_server()

    time.sleep(1)

    # 启动客户端并扫描
    client = Client(server)
    server.bind(client=client, env=env)
    client.scan()
    time.sleep(1)
    client.server_ip = client.scan_list[0]

    result = client.send_command(command='join')
    print(f"join 结果：{result}")

    # 调用客户端方法（验证功能）
    result = client.send_command(command='get_ground')
    print(f"get_ground 结果：{result}")

    result = client.send_command(command='get_target', grid='C2')
    print(f"get_target 结果：{result}")

    grids = ('C1', 'C2')  # 测试二元元组（支持数字、字符串等类型）
    result = client.send_command(command='move', grids=grids)
    print(f"move 结果：{result}")
