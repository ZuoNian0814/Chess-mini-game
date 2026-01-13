import copy
import random
import time
import numpy as np

class Queue:
    def __init__(self, max_len):
        self.max_len = max_len
        self.queue = []

    def put(self, x):
        self.queue.append(x)
        if len(self.queue) > self.max_len:
            self.queue.pop(0)

    def get(self):
        if self.queue:
            a = self.queue[-1]
            self.queue.pop(-1)
            return a
        else:
            return None

class Env:
    def __init__(self, round_id=1):
        self.round_id = round_id
        self.upgrade = False
        self.chess_id_dict = {
            1: 'King', 2: 'King',
            3: 'Queen', 4: 'Queen',
            5: 'Bishop', 6: 'Bishop',
            7: 'Bishop', 8: 'Bishop',
            9: 'Knight', 10: 'Knight',
            11: 'Knight', 12: 'Knight',
            13: 'Rook', 14: 'Rook',
            15: 'Rook', 16: 'Rook',
            17: 'Pawn', 18: 'Pawn',
            19: 'Pawn', 20: 'Pawn',
            21: 'Pawn', 22: 'Pawn',
            23: 'Pawn', 24: 'Pawn',
            25: 'Pawn', 26: 'Pawn',
            27: 'Pawn', 28: 'Pawn',
            29: 'Pawn', 30: 'Pawn',
            31: 'Pawn', 32: 'Pawn',
        }
        self.ground = [
            [14, 10,  6,  4,  2,  8, 12, 16],
            [18, 20, 22, 24, 26, 28, 30, 32],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [17, 19, 21, 23, 25, 27, 29, 31],
            [13,  9,  5,  3,  1,  7, 11, 15],
        ]
        self.queue = Queue(100)

        self.online = False
        self.my_r = None
        self.winner = None

    def init(self, online=False):
        self.ground = [
            [14, 10, 6, 4, 2, 8, 12, 16],
            [18, 20, 22, 24, 26, 28, 30, 32],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [17, 19, 21, 23, 25, 27, 29, 31],
            [13, 9, 5, 3, 1, 7, 11, 15],
        ]
        self.online = online
        self.round_id = 1

        self.queue = Queue(100)

        self.online = False
        self.my_r = None
        self.winner = None

    def get_move(self, grid, round_id=None, without_king=False, ground=None):
        if self.upgrade:
            return None
        else:
            if ground:
                ground = ground
            else:
                ground = self.ground

            if round_id:
                round_id = round_id
            else:
                round_id = self.round_id
            x, y = self.grid_to_xy(grid)
            chess_id = ground[y][x]
            if not chess_id or chess_id % 2 != round_id % 2:
                return None
            if chess_id < 0:
                return None
            chess = self.chess_id_dict[chess_id]
            move_target = []
            if chess == 'King' and not without_king:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        new_x, new_y = x + dx, y + dy
                        if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
                            continue
                        if not ground[new_y][new_x] or ground[new_y][new_x] % 2 != ground[y][x] % 2:
                            next_grid = self.xy_to_grid(new_x, new_y)
                            if not next_grid:
                                continue
                            move_target.append(next_grid)

            if chess == 'Queen':
                range_0, rang_1, range_2 = range(0, 1), range(-1, -9, -1), range(1, 8)
                d_range_list = [
                    (range_0, rang_1),      # 上
                    (range_2, rang_1),      # 右上
                    (range_2, range_0),     # 右
                    (range_2, range_2),     # 右下
                    (range_0, range_2),     # 下
                    (rang_1, range_2),      # 左下
                    (rang_1, range_0),      # 左
                    (rang_1, rang_1),       # 左上
                ]
                for range_x, range_y in d_range_list:
                    test = False
                    for dy in range_y:
                        for dx in range_x:
                            if dy != 0 and dx != 0:
                                if abs(dx*dy) != dx ** 2 or abs(dx*dy) != dy ** 2:
                                    continue
                            new_x, new_y = x + dx, y + dy
                            if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
                                continue
                            next_grid = self.xy_to_grid(new_x, new_y)
                            if not next_grid:
                                continue

                            if ground[new_y][new_x]:
                                if ground[new_y][new_x] % 2 != round_id % 2:
                                    move_target.append(next_grid)
                                test = True

                            if test:
                                break
                            move_target.append(next_grid)
                        if test:
                            break

            # 象
            if chess == 'Bishop':
                d_list = [-2, 2]
                for dx in d_list:
                    for dy in d_list:
                        new_x, new_y = x + dx, y + dy
                        if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
                            continue
                        next_grid = self.xy_to_grid(new_x, new_y)
                        if not next_grid:
                            continue
                        if ground[new_y][new_x]:
                            if ground[new_y][new_x] % 2 != round_id % 2:
                                move_target.append(next_grid)
                            continue
                        # 跨棋
                        new_x, new_y = x + dx // 2, y + dy // 2
                        if ground[new_y][new_x]:
                            continue
                        move_target.append(next_grid)

            # 马
            if chess == 'Knight':
                d_list = [-2, 2, -1, 1]
                for dx in d_list:
                    for dy in d_list:
                        if dx == dy or dx + dy == 0:
                            continue
                        new_x, new_y = x + dx, y + dy
                        if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
                            continue
                        next_grid = self.xy_to_grid(new_x, new_y)
                        if not next_grid:
                            continue
                        if ground[new_y][new_x]:
                            if ground[new_y][new_x] % 2 != round_id % 2:
                                move_target.append(next_grid)
                            continue
                        move_target.append(next_grid)

            # 车
            if chess == 'Rook':
                range_0, rang_1, range_2 = range(0, 1), range(-1, -9, -1), range(1, 8)
                d_range_list = [
                    (range_0, rang_1),  # 上
                    (range_2, range_0),  # 右
                    (range_0, range_2),  # 下
                    (rang_1, range_0),  # 左
                ]
                for range_x, range_y in d_range_list:
                    test = False
                    for dy in range_y:
                        for dx in range_x:
                            if dy != 0 and dx != 0:
                                if abs(dx * dy) != dx ** 2 or abs(dx * dy) != dy ** 2:
                                    continue
                            new_x, new_y = x + dx, y + dy
                            if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
                                continue
                            next_grid = self.xy_to_grid(new_x, new_y)
                            if not next_grid:
                                continue

                            if ground[new_y][new_x]:
                                if ground[new_y][new_x] % 2 != round_id % 2:
                                    move_target.append(next_grid)
                                test = True

                            if test:
                                break
                            move_target.append(next_grid)
                        if test:
                            break

            # 兵
            if chess == 'Pawn':
                start_row = '2' if round_id % 2 else '7'
                if start_row in grid:
                    distance = 3
                else:
                    distance = 2
                move_range = range(-1, -distance, -1) if round_id % 2 else range(1, distance)
                # 前进
                for dy in move_range:
                    new_x, new_y = x, y + dy
                    if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
                        continue
                    if ground[new_y][new_x]:
                        break
                    next_grid = self.xy_to_grid(new_x, new_y)
                    if not next_grid:
                        continue
                    move_target.append(next_grid)

                # 吃棋
                move_x = [-1, 1]
                dy = -1 if round_id % 2 else 1
                for dx in move_x:
                    new_x, new_y = x + dx, y + dy
                    if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
                        continue
                    if not ground[new_y][new_x] or ground[new_y][new_x] % 2 == round_id % 2:
                        continue
                    next_grid = self.xy_to_grid(new_x, new_y)
                    if not next_grid:
                        continue
                    move_target.append(next_grid)

            return move_target

    def move(self, grid_0, grid_1):
        self.queue.put(copy.deepcopy(self.ground))

        ground = copy.deepcopy(self.ground)
        round_id = self.round_id
        # 手动校验可移动位置
        target = self.get_move(grid_0)
        if not target:
            return False

        # 合法性校验
        x0, y0 = self.grid_to_xy(grid_0)
        chess_id = ground[y0][x0]
        if not ground[y0][x0] or ground[y0][x0] % 2 != round_id % 2:
            return False
        if grid_1 not in target:
            return False
        x1, y1 = self.grid_to_xy(grid_1)

        # 判断吃掉过路兵
        if ground[y1][x1] < 0 and ground[y0][x0] > 16:
            kill_Pawn = -ground[y1][x1]
            for x in range(8):
                for y in range(8):
                    if ground[y][x] == kill_Pawn:
                        ground[y][x] = 0

        # 清除上一回合的过路兵标记
        for x in range(8):
            for y in range(8):
                if ground[y][x] < 0:
                    ground[y][x] = 0

        # 添加过路兵标记
        if abs(y1 - y0) == 2 and self.chess_id_dict[chess_id] == 'Pawn':
            ground[(y1 + y0) // 2][x1] = -chess_id

        # 移动棋子
        ground[y1][x1] = ground[y0][x0]
        ground[y0][x0] = 0

        # 验证应将，如果不能解除King的威胁则撤回此步骤 ============================
        simulation_ground = self.simulation_move(grid_0, grid_1)
        King_target, King_loc = self.get_King_space(self.round_id, simulation_ground)
        danger = self.get_danger(self.round_id, simulation_ground)
        if set(King_loc) & set(danger) == set(King_loc):
            return False
        # ==============================================================

        # 兵升变
        if y1 in [0, 7] and self.chess_id_dict[chess_id] == 'Pawn':
            print('兵升变')
            self.upgrade = True

        if not self.upgrade:
            self.round_id += 1

        self.ground = ground

        if self.done():
            print('游戏结束了')
            print('黑白'[(self.round_id - 1) % 2], '胜利')
            self.winner = (self.round_id - 1) % 2

        return True

    def done(self, round_id=None):
        if round_id:
            round_id = round_id
        else:
            round_id = self.round_id

        done_list = []
        for x in range(8):
            for y in range(8):
                chess_id = self.ground[y][x]
                if chess_id <= 0 or chess_id % 2 != round_id % 2:
                    continue
                grid_0 = self.xy_to_grid(x, y)
                move_grids = self.get_move(grid_0, without_king=True)
                for grid_1 in move_grids:
                    # 验证应将，如果不能解除King的威胁则撤回此步骤 ============================
                    simulation_ground = self.simulation_move(grid_0, grid_1)
                    King_target, King_loc = self.get_King_space(self.round_id, simulation_ground)
                    danger = self.get_danger(self.round_id, simulation_ground)
                    if set(King_loc) & set(danger) == set(King_loc):
                        pass
                    else:
                        done_list.append((grid_0, grid_1))
                    # ==============================================================
        if done_list:
            print(done_list)
            return False
        else:
            return True

    def get_King_space(self, round_id, ground=None):
        if ground:
            ground = ground
        else:
            ground = self.ground
        target = []
        loc = []
        for y in range(8):
            for x in range(8):
                chess_id = ground[y][x]
                if chess_id in [1, 2] and chess_id % 2 == round_id % 2:
                    grid = self.xy_to_grid(x, y)
                    target = self.get_move(grid=grid)
                    loc = [grid]
                if target:
                    break
            if target:
                break
        return target, loc

    def get_danger(self, round_id, ground=None):
        if ground:
            ground = ground
        else:
            ground = self.ground
        all_danger = []
        for y in range(8):
            for x in range(8):
                chess_id = ground[y][x]
                if chess_id < 0:    # 避免无法定位过路兵标记
                    continue
                if chess_id % 2 != round_id:
                    grid = self.xy_to_grid(x, y)
                    next_target = self.get_move(grid, round_id + 1, without_king=True, ground=ground)
                    if next_target:
                        all_danger.extend(next_target)
        return list(set(all_danger))

    def simulation_move(self, grid_0, grid_1):
        ground = copy.deepcopy(self.ground)
        round_id = self.round_id
        # 手动校验可移动位置
        target = self.get_move(grid_0)

        if not target:
            return False

        # 合法性校验
        x0, y0 = self.grid_to_xy(grid_0)
        chess_id = ground[y0][x0]
        if not ground[y0][x0] or ground[y0][x0] % 2 != round_id % 2:
            return False
        if grid_1 not in target:
            return False
        x1, y1 = self.grid_to_xy(grid_1)

        # 判断吃掉过路兵
        if ground[y1][x1] < 0 and ground[y0][x0] > 16:
            kill_Pawn = -ground[y1][x1]
            for x in range(8):
                for y in range(8):
                    if ground[y][x] == kill_Pawn:
                        ground[y][x] = 0

        # 清除上一回合的过路兵标记
        for x in range(8):
            for y in range(8):
                if ground[y][x] < 0:
                    ground[y][x] = 0

        # 添加过路兵标记
        if abs(y1 - y0) == 2 and self.chess_id_dict[chess_id] == 'Pawn':
            ground[(y1 + y0) // 2][x1] = -chess_id

        # 移动棋子
        ground[y1][x1] = ground[y0][x0]
        ground[y0][x0] = 0
        return ground

    def upgrade_pawn(self, chess_type):
        upgrade_list = [
            {'Queen': 4, 'Bishop': 6, 'Knight': 10, 'Rook': 14},
            {'Queen': 3, 'Bishop': 5, 'Knight': 9, 'Rook': 13},
        ]
        for x in range(8):
            for y in range(8):
                if y in (0, 7) and self.ground[y][x] > 16:
                    self.ground[y][x] = upgrade_list[self.round_id % 2][chess_type]
                    self.upgrade = False
                    self.round_id += 1
                if not self.upgrade:
                    break
            if not self.upgrade:
                break

    def revoke(self):
        if self.queue.queue:
            self.round_id -= 1
            self.ground = self.queue.get()

    def xy_to_grid(self, x, y, visual=None, my_visual=None):
        if x < 0 or (8 - y) < 0:
            return None

        if my_visual is not None:
            if my_visual:
                return f"{'ABCDEFGH'[x]}{8 - y}"
            else:
                return f"{'ABCDEFGH'[::-1][x]}{y + 1}"
        try:
            if visual:
                if self.round_id % 2:
                    return f"{'ABCDEFGH'[x]}{8 - y}"
                else:
                    return f"{'ABCDEFGH'[::-1][x]}{y + 1}"
            else:
                return f"{'ABCDEFGH'[x]}{8 - y}"
        except IndexError:
            return None

    def grid_to_xy(self, grid, visual=False, my_visual=None):
        grid = grid.upper()
        if my_visual is not None:
            if my_visual:
                x = list('ABCDEFGH').index(grid[0])
                y = 8 - int(grid[1])
                return x, y
            else:
                x = list('ABCDEFGH')[::-1].index(grid[0])
                y = int(grid[1]) - 1
                return x, y
        try:
            if visual:
                if self.round_id % 2:
                    x = list('ABCDEFGH').index(grid[0])
                    y = 8 - int(grid[1])
                    return x, y
                else:
                    x = list('ABCDEFGH')[::-1].index(grid[0])
                    y = int(grid[1]) - 1
                    return x, y
            else:
                x = list('ABCDEFGH').index(grid[0])
                y = 8 - int(grid[1])
                return x, y
        except IndexError:
            return None

    def show_target(self, target):
        if target:
            ground = [[0 for _ in range(8)] for _ in range(8)]
            for grid in target:
                x, y = self.grid_to_xy(grid)
                ground[y][x] = 255
            arr = np.array(ground)
            print(arr)

    def show_ground(self):
        arr = np.array(self.ground)
        print(arr)

    def get_flip_ground(self):
        flip_arr = np.array([
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
        ])
        return (flip_arr @ np.array(self.ground) @ flip_arr).tolist()

if __name__ == '__main__':
    env = Env()

    target = env.get_move('D2')
    print(target)
    env.show_target(target)

    result = env.move('D2', 'D4')
    env.show_ground()


