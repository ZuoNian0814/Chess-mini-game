import copy
import json
import time
import pygame
import numpy as np
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from Environment import Env
from Online import Server, Client

def enlarge_pixel_art(image, magnification, background_color=None):
    # 获取原始图像的尺寸
    width, height = image.size

    # 计算放大后的图像尺寸
    new_width = width * magnification
    new_height = height * magnification

    # 创建一个新的空白图像，模式为 RGBA
    new_image = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    pink_image = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(new_image)
    draw_p = ImageDraw.Draw(pink_image)

    # 遍历原始图像的每个像素
    for y in range(height):
        for x in range(width):
            # 计算放大后像素的位置
            start_x = x * magnification
            start_y = y * magnification
            end_x = start_x + magnification
            end_y = start_y + magnification
            r, g, b, a = image.getpixel((x, y))
            draw.rectangle([start_x, start_y, end_x, end_y], fill=(r, g, b, a))
            if a == 0 and background_color is not None:
                # 如果像素是透明的且指定了背景颜色，则填充背景颜色
                r, g, b = tuple(int(background_color[i:i + 2], 16) for i in (1, 3, 5))
                a = 255
            # 在新图像上绘制矩形
            if r == 250 and g == 246 and b == 234:
                # 如果像素是透明的且指定了背景颜色，则填充背景颜色
                draw_p.rectangle([start_x, start_y, end_x, end_y], fill='#ffb2c9')
            elif r == 233 and g == 220 and b == 204:
                # 如果像素是透明的且指定了背景颜色，则填充背景颜色
                draw_p.rectangle([start_x, start_y, end_x, end_y], fill='#f38c96')
            else:
                draw_p.rectangle([start_x, start_y, end_x, end_y], fill=(r, g, b, a))

    return new_image, pink_image

ui_config = {
    '1': (0, 201, 6, 208),
    '2': (8, 201, 14, 208),
    '3': (16, 201, 22, 208),
    '4': (24, 201, 30, 208),
    '5': (32, 201, 38, 208),
    '6': (40, 201, 46, 208),
    '7': (48, 201, 54, 208),
    '8': (56, 201, 62, 208),
    '9': (64, 201, 70, 208),
    '0': (72, 201, 78, 208),
    '.': (80, 201, 86, 208),
    '▶': (64, 176, 70, 183),
    '📶': (72, 176, 78, 183),
    '→': (80, 244, 90, 251),
    ' ': (20, 379, 26, 383),
    'A': (0, 186, 6, 192),
    'B': (8, 186, 14, 192),
    'C': (16, 186, 22, 192),
    'D': (24, 186, 30, 192),
    'E': (32, 186, 38, 192),
    'F': (40, 186, 46, 192),
    'G': (48, 186, 54, 192),
    'H': (56, 186, 62, 192),
    'select': (32, 240, 48, 256),
    'King_0': (0, 208, 16, 224),
    'Queen_0': (16, 208, 32, 224),
    'Rook_0': (32, 208, 48, 224),
    'Bishop_0': (48, 208, 64, 224),
    'Knight_0': (64, 208, 80, 224),
    'Pawn_0': (80, 208, 96, 224),
    'King_1': (0, 224, 16, 240),
    'Queen_1': (16, 224, 32, 240),
    'Rook_1': (32, 224, 48, 240),
    'Bishop_1': (48, 224, 64, 240),
    'Knight_1': (64, 224, 80, 240),
    'Pawn_1': (80, 224, 96, 240),
    'close_0': (64, 240, 71, 247),
    'close_1': (64, 249, 71, 256),
    'switch_0_0': (0, 262, 16, 272), 'switch_0_1': (16, 262, 32, 272),
    'switch_1_0': (32, 262, 48, 272), 'switch_1_1': (48, 262, 64, 272),
    'surrender_0': (230, 192, 239, 202), 'surrender_1': (240, 192, 249, 202),
    # 'start_window': (0, 0, 166, 167),
    'title': (43, 56, 123, 90),
    'ground_window': (168, 0, 334, 167),
    'ground': (181, 22, 321, 162),
    'start_window': (336, 0, 502, 167),
    'invitation_win': (0, 288, 124, 354),
    'accept_0': (29, 327, 93, 345), 'accept_1': (160, 380, 224, 398),
    'online_win': (0, 355, 123, 432),
    'setting_win': (0, 434, 124, 496),
    'upgrade_win': (131, 288, 255, 354),
    'play_0': (96, 176, 160, 194),
    'play_1': (161, 176, 225, 194),
    'setting_0': (96, 195, 160, 213),
    'setting_1': (161, 195, 225, 213),
    'online_0': (96, 214, 160, 232),
    'online_1': (161, 214, 225, 232),
    'ok_0': (160, 327, 224, 345), 'ok_1': (160, 361, 224, 379),
    'revoke_0': (231, 176, 239, 183), 'revoke_1': (240, 176, 248, 183),
    'game_over_win': (376, 174, 499, 239),
    'exit_0': (405, 213, 469, 231), 'exit_1': (405, 243, 469, 261),
    'victory': (292, 176, 372, 199),
    'defeat': (292, 200, 372, 223),
    'over': (292, 224, 372, 247),
}

col_list = ['#e9b5a3', '#b27349', '#403353']
alpha_bg = '#00ff00'
magnification = 3

ui_images = {}
all_image = Image.open('UI/atlas.png')
for k, box in ui_config.items():
    img = all_image.crop(box)
    magnify_img, bg_image = enlarge_pixel_art(img, magnification, background_color=alpha_bg)
    ui_images[k] = (magnify_img, bg_image)


class Window:
    def __init__(
            self, alpha_bg, magnification, env, server, client, visual,
            music=True, voice=True, win_x=None, win_y=None
    ):
        self.server = server
        self.server.run_server()
        self.client = client
        self.env = env
        self.visual = visual  # 每回合切换视角
        self.photo = {}
        self.screen = []  # 动态控件容器
        self.music = music  # 音乐
        self.voice = voice  # 音效
        self.online = False  # 在线标识
        self.play = False  # 正在对局标识
        self.choice_move = False  # 是否选择落子标识
        self.select_loc = None
        self.upgrade_chess = None
        self.next_loc = []
        self.while_num0 = 0
        self.magnification = magnification
        self.alpha_bg = alpha_bg
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes('-transparentcolor', self.alpha_bg)
        self.root.attributes('-topmost', True)

        self.flash = 0
        self.challenges_await = 0
        self.scan_count = 0     # 周期性扫描

        self.my_round = None
        self.round_id = 1
        self.game_result = None
        self.ground_mark = None

        start_bg_img, ground_bg_img = ui_images['start_window'][1], ui_images['ground_window'][1]
        self.photo['start_bg_label'] = (ImageTk.PhotoImage(start_bg_img), ImageTk.PhotoImage(ground_bg_img))
        self.bg_photo = self.photo['start_bg_label'][0]
        self.bg_label = tk.Label(self.root, image=self.bg_photo, bd=0)
        self.bg_label.pack()
        self.bg_label.bind("<ButtonPress-1>", self._on_button_press0)
        self.bg_label.bind("<ButtonRelease-1>", self._on_button_release0)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        win_w, win_h = start_bg_img.size

        if win_x and win_y:
            self.root.geometry(f'+{win_x}+{win_y}')
            self.win_x, self.win_y = win_x, win_y
        else:
            self.win_x = int((screen_width - win_w) / 2)
            self.win_y = int((screen_height - win_h) / 2) - 50
            self.root.geometry(f'+{self.win_x}+{self.win_y}')

        close_label = tk.Label(self.bg_label, bd=0)
        self.button_bind(close_label, 'close_label', ui_images['close_0'][1], ui_images['close_1'][1],
                         (self.root.destroy, pygame.mixer.music.stop))
        close_label.configure(image=self.photo['close_label'][0])
        close_label.place(x=155 * magnification, y=4 * magnification)

        self._start_screen_place()
        pygame.init()
        pygame.mixer.init()
        try:
            pygame.mixer.music.load("sound/bgm.wav")  # 支持MP3（需依赖）、OGG、WAV
            pygame.mixer.music.play(-1)  # -1表示循环播放
            pygame.mixer.music.set_volume(0.5)
        except: pass
        self.click_sound = pygame.mixer.Sound("sound/click.wav")
        self.click_sound.set_volume(0.3)
        self.error_sound = pygame.mixer.Sound("sound/error.wav")
        self.error_sound.set_volume(0.4)
        self.invitation_sound = pygame.mixer.Sound("sound/invitation.wav")
        self.invitation_sound.set_volume(0.6)

        self.light = False

        self.update()

    def click_s(self):
        if self.voice:
            self.click_sound.play()

    def button_bind(self, label, button_title, img_0, img_1, command, switch=False):
        w, h = img_0.size
        self.photo[button_title] = (ImageTk.PhotoImage(img_0), ImageTk.PhotoImage(img_1))
        label.bind("<ButtonPress-1>", lambda e: label.configure(image=self.photo[button_title][1]))
        label.bind("<ButtonRelease-1>", lambda e: (
            None if switch else label.configure(image=self.photo[button_title][0]),
            [c() for c in command] if type(command) is tuple else command() if 0 < e.x < w and 0 < e.y < h else 0,
            self.click_s()
            )
        )

    def _place_forget(self):
        for i in self.screen:
            i.place_forget()
            self.screen.remove(i)
        self.screen = []

    def _start_screen_place(self):
        def play():
            self.online = False
            self._place_forget()
            self._play_screen_place()

        def setting():
            self._place_forget()
            self._setting_screen_place()

        def online():
            self._place_forget()
            self._online_screen_place()

        self.photo['title_label'] = ImageTk.PhotoImage(ui_images['title'][1])
        title_label = tk.Label(self.bg_label, image=self.photo['title_label'], bd=0)
        title_label.place(x=43 * magnification, y=56 * magnification)

        play_label = tk.Label(self.bg_label, bd=0)
        self.button_bind(play_label, 'play_label', ui_images['play_0'][1], ui_images['play_1'][1], play)
        play_label.configure(image=self.photo['play_label'][0])
        play_label.place(x=51 * magnification, y=93 * magnification)

        setting_label = tk.Label(self.bg_label, bd=0)
        self.button_bind(setting_label, 'setting_label', ui_images['setting_0'][1], ui_images['setting_1'][1], setting)
        setting_label.configure(image=self.photo['setting_label'][0])
        setting_label.place(x=51 * magnification, y=112 * magnification)

        online_label = tk.Label(self.bg_label, bd=0)
        self.button_bind(online_label, 'online_label', ui_images['online_0'][1], ui_images['online_1'][1], online)
        online_label.configure(image=self.photo['online_label'][0])
        online_label.place(x=51 * magnification, y=131 * magnification)

        self.screen.extend([title_label, play_label, setting_label, online_label])

    def _upgrade_place(self):
        def ok():
            if self.online:
                self.client.send_command('upgrade', chess_type=self.upgrade_chess)
                self._place_forget()
                self.update()
            else:
                self.env.upgrade_pawn(self.upgrade_chess)
                self._place_forget()
                self.update()

        def Queen():
            self.upgrade_chess = 'Queen'
            Pawn_label.configure(image=self.photo['Queen_label'][0])

        def Bishop():
            self.upgrade_chess = 'Bishop'
            Pawn_label.configure(image=self.photo['Bishop_label'][0])

        def Knight():
            self.upgrade_chess = 'Knight'
            Pawn_label.configure(image=self.photo['Knight_label'][0])

        def Rook():
            self.upgrade_chess = 'Rook'
            Pawn_label.configure(image=self.photo['Rook_label'][0])

        self.photo['upgrade_win'] = ImageTk.PhotoImage(ui_images['upgrade_win'][1])
        title_label = tk.Label(self.bg_label, image=self.photo['upgrade_win'], bd=0)
        title_label.place(x=21 * magnification, y=62 * magnification)

        f = enlarge_pixel_art
        Pawn_label = tk.Label(title_label, bd=0)
        img_0, img_1 = f(ui_images['Pawn_0'][0], 1, col_list[2])[1], f(ui_images['Pawn_1'][0], 1, col_list[2])[1]
        self.button_bind(Pawn_label, 'Pawn_label', img_0, img_1, lambda: print('pawn'))
        Pawn_label.configure(image=self.photo['Pawn_label'][0])
        Pawn_label.place(x=14 * magnification, y=19 * magnification)

        Queen_label = tk.Label(title_label, bd=0)
        img_0, img_1 = f(ui_images['Queen_0'][0], 1, col_list[2])[1], f(ui_images['Queen_1'][0], 1, col_list[2])[1]
        self.button_bind(Queen_label, 'Queen_label', img_0, img_1, Queen)
        Queen_label.configure(image=self.photo['Queen_label'][0])
        Queen_label.place(x=47 * magnification, y=19 * magnification)

        Bishop_label = tk.Label(title_label, bd=0)
        img_0, img_1 = f(ui_images['Bishop_0'][0], 1, col_list[2])[1], f(ui_images['Bishop_1'][0], 1, col_list[2])[1]
        self.button_bind(Bishop_label, 'Bishop_label', img_0, img_1, Bishop)
        Bishop_label.configure(image=self.photo['Bishop_label'][0])
        Bishop_label.place(x=63 * magnification, y=19 * magnification)

        Knight_label = tk.Label(title_label, bd=0)
        img_0, img_1 = f(ui_images['Knight_0'][0], 1, col_list[2])[1], f(ui_images['Knight_1'][0], 1, col_list[2])[1]
        self.button_bind(Knight_label, 'Knight_label', img_0, img_1, Knight)
        Knight_label.configure(image=self.photo['Knight_label'][0])
        Knight_label.place(x=79 * magnification, y=19 * magnification)

        Rook_label = tk.Label(title_label, bd=0)
        img_0, img_1 = f(ui_images['Rook_0'][0], 1, col_list[2])[1], f(ui_images['Rook_1'][0], 1, col_list[2])[1]
        self.button_bind(Rook_label, 'Rook_label', img_0, img_1, Rook)
        Rook_label.configure(image=self.photo['Rook_label'][0])
        Rook_label.place(x=95 * magnification, y=19 * magnification)

        ok_label = tk.Label(title_label, bd=0)
        img_0, img_1 = f(ui_images['ok_0'][0], 1, col_list[2])[1], f(ui_images['ok_1'][0], 1, col_list[2])[1]
        self.button_bind(ok_label, 'ok_label', img_0, img_1, ok)
        ok_label.configure(image=self.photo['ok_label'][0])
        ok_label.place(x=29 * magnification, y=39 * magnification)

        self.screen = [title_label, Pawn_label, Queen_label, Bishop_label, Knight_label, Rook_label, ok_label]

    def update(self):
        if self.play:
            if self.game_result == 'v':
                self._game_over_place('victory')
                return
            elif self.game_result == 'd':
                self._game_over_place('defeat')
                return

            if self.online and self.server.accept:
                if self.flash < 100:
                    self.flash += 1
                else:
                    self.flash = 0

                if self.flash % 20 in [0, 1, 3]:
                    if self.round_id % 2 == self.my_round % 2:
                        switch = True
                        light = True
                    else:
                        switch = False
                        light = True
                else:
                    switch = False
                    light = False

                if light != self.light:
                    if light and switch:
                        if switch:
                            self.round_mark_label1.configure(image=self.photo['round_mark_label'])
                            self.round_mark_label0.configure(image=self.photo[' '])
                        else:
                            self.round_mark_label0.configure(image=self.photo['round_mark_label'])
                            self.round_mark_label1.configure(image=self.photo[' '])
                    else:
                        self.round_mark_label0.configure(image=self.photo[' '])
                        self.round_mark_label1.configure(image=self.photo[' '])
                    self.light = light

            upgrade, upgrade_round = False, None
            if self.online and self.server.accept:
                if self.my_round % 2:
                    result = self.client.send_command(command='get_ground')
                else:
                    result = self.client.send_command(command='get_f_ground')
                ground = result['ground']
                self.round_id = result['round_id']
                winner = result['winner']
                upgrade, upgrade_round = result['upgrade']
                if winner is not None:
                    if winner % 2 == self.my_round % 2:
                        self.game_result = 'v'
                    else:
                        self.game_result = 'd'
            else:
                if self.env.round_id % 2 or not self.visual:
                    ground = self.env.ground
                else:
                    ground = self.env.get_flip_ground()

            if self.ground_mark != copy.deepcopy(ground) or self.select_loc or self.next_loc:
                self.ground_mark = copy.deepcopy(ground)
                ground_img = copy.deepcopy(ui_images['ground'][0])
                for y0 in [-1, 135]:
                    x0, y0 = 11 * magnification, y0 * magnification
                    for i in range(8):
                        if self.env.round_id % 2 or not self.visual:
                            char = 'ABCDEFGH'[i]
                        else:
                            char = 'ABCDEFGH'[::-1][i]
                        img = ui_images[char][0]
                        ground_img.paste(img, (x0, y0))
                        x0 += 16 * magnification

                for x0 in [-1, 135]:
                    x0, y0 = x0 * magnification, 11 * magnification
                    for i in range(8):
                        if self.env.round_id % 2 or not self.visual:
                            char = '87654321'[i]
                        else:
                            char = '87654321'[::-1][i]
                        img = ui_images[char][0]
                        ground_img.paste(img, (x0, y0))
                        y0 += 16 * magnification

                x0, y0 = 6 * magnification, 6 * magnification
                for y in range(8):
                    for x in range(8):
                        chess_id = ground[y][x]
                        if chess_id > 0:
                            chess_name = self.env.chess_id_dict[chess_id]
                            chess_img = ui_images[f"{chess_name}_{chess_id % 2}"][0]
                            loc = x0 + x * 16 * magnification, y0 + y * 16 * magnification
                            ground_img.paste(chess_img, loc, chess_img)

                if self.select_loc:
                    x, y = self.select_loc
                    loc = x0 + x * 16 * magnification, y0 + y * 16 * magnification
                    select_img = ui_images["select"][0]
                    ground_img.paste(select_img, loc, select_img)

                if self.next_loc:
                    next_loc = [self.env.grid_to_xy(loc, my_visual=self.my_round) for loc in self.next_loc]
                    for x, y in next_loc:
                        loc = x0 + x * 16 * magnification, y0 + y * 16 * magnification
                        select_img = ui_images["select"][0]
                        ground_img.paste(select_img, loc, select_img)

                self.photo['ground'] = ImageTk.PhotoImage(ground_img)
                self.ground_label.configure(image=self.photo['ground'])

            if self.online:
                if upgrade:
                    if self.my_round % 2 == upgrade_round % 2:
                        self._upgrade_place()
                        return
            else:
                # 游戏结束
                if self.env.winner is not None:
                    self._game_over_place()
                    return

                if self.env.upgrade:
                    self._upgrade_place()
                    return

        if self.server.invitation:
            if not self.challenges_await:
                self._invitation_place()

        self.root.after(100, self.update)

    def _invitation_test(self):
        if self.server.invitation is None:
            self.challenges_await = False
            for i in self.invitation_win_item:
                i.place_forget()
            return

        self.root.after(500, self._invitation_test)

    def _invitation_place(self):
        self.challenges_await = True
        self.invitation_sound.play()
        def accept():
            if self.server.invitation:
                self.server.accept = True
                self.server.invitation = None
            else:
                self.server.accept = False
                self.server.invitation = None
                win_label.place_forget()

        self.photo['invitation_win'] = ImageTk.PhotoImage(ui_images['invitation_win'][1])
        win_label = tk.Label(self.bg_label, image=self.photo['invitation_win'], bd=0)
        win_label.place(x=21 * magnification, y=62 * magnification)

        inv_close_label = tk.Label(win_label, bd=0)
        self.button_bind(inv_close_label, 'inv_close_label', ui_images['close_0'][1], ui_images['close_1'][1], win_label.place_forget)
        inv_close_label.configure(image=self.photo['inv_close_label'][0])
        inv_close_label.place(x=111 * magnification, y=6 * magnification)

        accept_label = tk.Label(win_label, bd=0)
        self.button_bind(accept_label, 'accept_label', ui_images['accept_0'][1], ui_images['accept_1'][1], accept)
        accept_label.configure(image=self.photo['accept_label'][0])
        accept_label.place(x=29 * magnification, y=39 * magnification)

        bg = self._get_font_img(self.server.invitation, 0)
        self.photo['invitation_ip_photo'] = ImageTk.PhotoImage(bg)
        ip_label = tk.Label(win_label, bd=0, image=self.photo['invitation_ip_photo'])
        ip_label.place(x=42 * self.magnification, y=14 * self.magnification)

        self.invitation_win_item = [win_label]
        self.screen.extend([win_label, accept_label, ip_label])

        self._invitation_test()

    def _ground_click(self, e):
        x, y = e.x, e.y
        if x > 133 * self.magnification or y > 133 * self.magnification:
            return
        loc_x, loc_y = (x - 6 * self.magnification) // (16 * self.magnification), (y - 6 * self.magnification) // (
                16 * self.magnification)
        if self.select_loc:
            s_x, s_y = self.select_loc
        else:
            s_x, s_y = None, None
        self.select_loc = (loc_x, loc_y)

        loc = self.env.xy_to_grid(loc_x, loc_y, my_visual=self.my_round)
        if self.choice_move:
            if self.next_loc:
                if loc not in self.next_loc:
                    if self.online:
                        if self.round_id % 2 == self.my_round % 2:
                            target = self.client.send_command(command='get_target', grid=loc)['target']
                        else:
                            target = []
                        self.next_loc = target
                        self.choice_move = True
                    else:
                        target = self.env.get_move(loc)
                        self.next_loc = target
                        self.choice_move = True
                else:
                    if s_x is not None and s_y is not None:
                        end_loc = self.env.xy_to_grid(loc_x, loc_y, my_visual=self.my_round)
                        start_loc = self.env.xy_to_grid(s_x, s_y, my_visual=self.my_round)
                        if self.online:
                            if self.round_id % 2 == self.my_round % 2:
                                result = self.client.send_command(command='move', grids=(start_loc, end_loc))
                                if not result['result']:
                                    self.error_sound.play()
                            else:
                                pass
                        else:
                            result = self.env.move(start_loc, end_loc)
                            if not result:
                                self.error_sound.play()
                        self.choice_move = False
                        self.next_loc = None
            else:
                if self.online:
                    if self.round_id % 2 == self.my_round % 2:
                        target = self.client.send_command(command='get_target', grid=loc)['target']
                    else:
                        target = []
                    self.next_loc = target
                    self.choice_move = True
                else:
                    target = self.env.get_move(loc)
                    self.next_loc = target
                    self.choice_move = True
        else:
            if self.online:
                if self.round_id % 2 == self.my_round % 2:
                    target = self.client.send_command(command='get_target', grid=loc)['target']
                else:
                    target = []
                self.next_loc = target
                self.choice_move = True
            else:
                target = self.env.get_move(loc)
                self.next_loc = target
                self.choice_move = True

    def _play_screen_place(self):
        def revoke():
            if self.online and self.round_id % 2 == self.my_round:
                self.client.send_command('revoke')
            else:
                self.env.revoke()

        def surrender():
            if self.online:
                result = self.client.send_command(command='surrender', my_round=self.my_round)
            else:
                self._game_over_place()

        if self.online:
            if self.my_round is None:
                self.my_round = 1

        self.env.init(online=len(self.server.players_list) == 2)
        self.bg_label.configure(image=self.photo['start_bg_label'][1])

        ground_img = ui_images['ground'][0]
        self.photo['ground'] = ImageTk.PhotoImage(ground_img)
        self.ground_label = tk.Label(self.bg_label, image=self.photo['ground'], bd=0)
        self.ground_label.bind("<Button-1>", self._ground_click)
        self.ground_label.place(x=13 * magnification, y=22 * magnification)

        revoke_label = tk.Label(self.bg_label, bd=0)
        self.button_bind(revoke_label, 'revoke_label', ui_images['revoke_0'][1], ui_images['revoke_1'][1], revoke)
        revoke_label.configure(image=self.photo['revoke_label'][0])
        revoke_label.place(x=153 * magnification, y=22 * magnification)

        self.round_mark_label0 = tk.Label(self.bg_label, bd=0)
        self.photo['round_mark_label'] = ImageTk.PhotoImage(ui_images['→'][1])
        self.photo[' '] = ImageTk.PhotoImage(ui_images[' '][1])
        self.round_mark_label0.configure(image=self.photo[' '])
        self.round_mark_label0.place(x=5 * magnification, y=22 * magnification)

        self.round_mark_label1 = tk.Label(self.bg_label, bd=0)
        self.round_mark_label1.configure(image=self.photo[' '])
        self.round_mark_label1.place(x=5 * magnification, y=155 * magnification)

        surrender_label = tk.Label(self.bg_label, bd=0)
        self.button_bind(surrender_label, 'surrender_label', ui_images['surrender_0'][1], ui_images['surrender_1'][1],
                         surrender)
        surrender_label.configure(image=self.photo['surrender_label'][0])
        surrender_label.place(x=151 * magnification, y=154 * magnification)

        self.screen.extend(
            [self.bg_label, self.ground_label, revoke_label, self.round_mark_label0, self.round_mark_label1,
             surrender_label])
        self.play = True

    def _game_over_place(self, mode='over'):
        self.play = False
        def exit_game():
            self.env.init()
            self.server.init()
            self.client.init()
            self.root.destroy()
            a = Window(alpha_bg, magnification, env, server, client, False, music=self.music, voice=self.voice,
                    win_x=self.win_x, win_y=self.win_y)

        self.photo['game_over_win'] = ImageTk.PhotoImage(ui_images['game_over_win'][1])
        win_label = tk.Label(self.bg_label, image=self.photo['game_over_win'], bd=0)
        win_label.place(x=21 * magnification, y=62 * magnification)

        self.photo['over'] = (
            ImageTk.PhotoImage(ui_images['over'][1]),
            ImageTk.PhotoImage(ui_images['victory'][1]),
            ImageTk.PhotoImage(ui_images['defeat'][1]),
        )
        self.over_label = tk.Label(win_label, bd=0)
        if mode == 'victory':
            self.over_label.configure(image=self.photo['over'][1])
        elif mode == 'defeat':
            self.over_label.configure(image=self.photo['over'][2])
        else:
            self.over_label.configure(image=self.photo['over'][0])

        self.over_label.place(x=21 * magnification, y=15 * magnification)

        exit_label = tk.Label(win_label, bd=0)
        self.button_bind(exit_label, 'exit_label', ui_images['exit_0'][1], ui_images['exit_1'][1], exit_game)
        exit_label.configure(image=self.photo['exit_label'][0])
        exit_label.place(x=29 * magnification, y=39 * magnification)

        self.screen.extend([win_label, exit_label])

    def _setting_screen_place(self):
        self.photo['setting_win'] = ImageTk.PhotoImage(ui_images['setting_win'][1])
        title_label = tk.Label(self.bg_label, image=self.photo['setting_win'], bd=0)
        title_label.place(x=21 * magnification, y=62 * magnification)

        close_label = tk.Label(self.bg_label, bd=0)
        self.button_bind(close_label, 'close_label', ui_images['close_0'][1], ui_images['close_1'][1],
                         (self._place_forget, self._start_screen_place))
        close_label.configure(image=self.photo['close_label'][0])
        close_label.place(x=132 * magnification, y=68 * magnification)

        self.music_switch_l = tk.Label(self.bg_label, bd=0)
        self.button_bind(self.music_switch_l, 'music_switch_l', ui_images['switch_1_0'][1], ui_images['switch_1_1'][1],
                         self._music, switch=True)
        if self.music:
            self.music_switch_l.configure(image=self.photo['music_switch_l'][1])
        else:
            self.music_switch_l.configure(image=self.photo['music_switch_l'][0])
        self.music_switch_l.place(x=59 * magnification, y=89 * magnification)

        self.voice_switch_l = tk.Label(self.bg_label, bd=0)
        self.button_bind(self.voice_switch_l, 'voice_switch_l', ui_images['switch_1_0'][1], ui_images['switch_1_1'][1],
                         self._voice, switch=True)
        if self.voice:
            self.voice_switch_l.configure(image=self.photo['voice_switch_l'][1])
        else:
            self.voice_switch_l.configure(image=self.photo['voice_switch_l'][0])
        self.voice_switch_l.place(x=104 * magnification, y=89 * magnification)

        self.screen.extend([title_label, close_label, self.music_switch_l, self.voice_switch_l])

    def _music(self):
        if self.music:
            self.music = False
            pygame.mixer.music.pause()
            self.music_switch_l.configure(image=self.photo['music_switch_l'][0])
        else:
            self.music = True
            pygame.mixer.music.unpause()
            self.music_switch_l.configure(image=self.photo['music_switch_l'][1])

    def _voice(self):
        if self.voice:
            self.voice = False
            self.voice_switch_l.configure(image=self.photo['voice_switch_l'][0])
        else:
            self.voice = True
            self.voice_switch_l.configure(image=self.photo['voice_switch_l'][1])

    def _online_screen_place(self):
        self.photo['online_win'] = ImageTk.PhotoImage(ui_images['online_win'][1])
        self.online_bg_label = tk.Label(self.bg_label, image=self.photo['online_win'], bd=0)
        self.online_bg_label.place(x=21 * magnification, y=62 * magnification)

        close_label = tk.Label(self.bg_label, bd=0)
        self.button_bind(close_label, 'close_label', ui_images['close_0'][1], ui_images['close_1'][1],
                         (self._place_forget, self._start_screen_place))
        close_label.configure(image=self.photo['close_label'][0])
        close_label.place(x=132 * magnification, y=68 * magnification)

        self.online_switch_l = tk.Label(self.bg_label, bd=0)
        self.button_bind(self.online_switch_l, 'online_switch_l', ui_images['switch_0_0'][1],
                         ui_images['switch_0_1'][1], self._online, switch=True)
        if self.online:
            self.online_switch_l.configure(image=self.photo['online_switch_l'][1])
        else:
            self.online_switch_l.configure(image=self.photo['online_switch_l'][0])
        self.online_switch_l.place(x=92 * magnification, y=121 * magnification)

        self.ip_label = tk.Label(self.online_bg_label, bd=0)

        self.ip_label_0 = tk.Label(self.online_bg_label, bd=0)
        self.ip_label_0.bind("<ButtonPress-1>", self._click_player)
        self.ip_label_1 = tk.Label(self.online_bg_label, bd=0)
        self.ip_label_1.bind("<ButtonPress-1>", self._click_player)
        self.ip_label_2 = tk.Label(self.online_bg_label, bd=0)
        self.ip_label_2.bind("<ButtonPress-1>", self._click_player)

        self.screen.extend([self.online_bg_label, close_label, self.ip_label, self.ip_label_0, self.ip_label_1,
                            self.ip_label_2, self.online_switch_l])

    def _join_game(self):
        result = self.client.send_command(command='join')
        self.challenges_await += 1
        if result:
            if result['you_round'] is not None:
                self._place_forget()
                self.my_round = result['you_round']
                self.server.accept = True
                self._play_screen_place()
                return

        if self.challenges_await >= 5:
            self.challenges_await = 0
            result = self.client.send_command(command='join_over')
            self.client.server_ip = None
            return
        self.root.after(1000, self._join_game)

    def _click_player(self, e):
        if self.client.server_ip is None:
            self.client.server_ip = e.widget["text"]
            self._join_game()

    def _get_font_img(self, chars, bg_index):
        w, h = len(chars) * 5 * self.magnification + 1 * self.magnification, 8 * self.magnification
        bg = Image.new('RGB', (w, h), col_list[bg_index])
        x = 0
        for char in chars:
            char_img = ui_images[char][0]
            bg.paste(char_img, (x, 0), char_img)
            x += 5 * self.magnification
        return bg

    def _online_update(self):
        if self.scan_count >= 30:
            self.scan_count = 0
        else:
            self.scan_count += 1
        if self.online_bg_label.winfo_ismapped() and not self.play:
            ip = self.server.my_ip
            bg = self._get_font_img(ip, 0)

            # my_ip
            self.photo['ip_photo'] = ImageTk.PhotoImage(bg)
            self.ip_label.configure(image=self.photo['ip_photo'])
            self.ip_label.place(x=37 * self.magnification, y=14 * self.magnification)

            # other_player
            if self.scan_count % 5 == 0:
                self.client.scan()
                while not self.client.scan_over:
                    pass

            i = 0
            ip_l_list = [self.ip_label_0, self.ip_label_1, self.ip_label_2]
            for player_ip in self.client.scan_list:
                if player_ip == self.server.my_ip:
                    s = f"0.0.0.0"
                else:
                    s = f"{player_ip}"
                # ▶ 📶
                s = f"▶ {s}" + (15 - len(s)) * ' ' + '📶'
                ip_l = ip_l_list[i]
                img = self._get_font_img(s, 2)
                self.photo[f'ip_{i}_photo'] = ImageTk.PhotoImage(img)
                ip_l.configure(image=self.photo[f'ip_{i}_photo'], text=player_ip)
                ip_l.place(x=15 * self.magnification, y=(25 + i * 7) * self.magnification)
                i += 1
            for i in range(i, 3):
                ip_l_list[i].place_forget()
            if not self.online:
                for ip_l in ip_l_list + [self.ip_label]:
                    ip_l.place_forget()
                return

            # 如果玩家已满开始游戏
            if len(self.server.players_list) == 2:
                self._play_screen_place()
                return

        self.root.after(300, self._online_update)

    def _online(self):
        if self.online:
            self.online = False
            self.online_switch_l.configure(image=self.photo['online_switch_l'][0])
        else:
            self.online = True
            self._online_update()
            self.online_switch_l.configure(image=self.photo['online_switch_l'][1])

        self.server.open_test = self.online

    def _on_button_press0(self, event):
        """鼠标按下事件处理（用于拖动窗口）"""
        self.while_num0 = 0
        while True:
            if self.while_num0 == 0:
                x, y = self.root.winfo_pointerxy()
                x0, y0 = event.x, event.y
                self.win_x, self.win_y = x - x0, y - y0
                self.root.geometry("+{}+{}".format(self.win_x, self.win_y))
                self.root.update()
            else:
                break

    def _on_button_release0(self, event):
        """鼠标释放事件处理（用于拖动窗口）"""
        if self.while_num0 == 2:
            pass
        else:
            self.while_num0 = 1

    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    my_camp = 1
    env = Env(my_camp)
    server = Server()
    client = Client(server)
    server.bind(client=client, env=env)
    win = Window(alpha_bg, magnification, env, server, client, False)

    # ground = env.get_flip_ground()
    # win.update_ground(ground)

    win.mainloop()