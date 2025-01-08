import pygame as pg
import os
from config_4 import *
import time


class GameObject:
    def __init__(self, image, color, pos):
        self.image = image
        self.color = color
        self.pos = image.get_rect(center=pos)
        self.alpha = 255  # 透明度
        self.target_alpha = 255
        self.fade_speed = 5

    def update_alpha(self):
        if self.alpha < self.target_alpha:
            self.alpha = min(self.alpha + self.fade_speed, self.target_alpha)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.alpha - self.fade_speed, self.target_alpha)
        self.image.set_alpha(self.alpha)


# 按钮类，生成了悔棋按钮和恢复按钮
class Button(object):
    # 具有图像surface，宽高和坐标属性
    def __init__(self, text, color, x=None, y=None):
        self.surface = font_big.render(text, True, color)
        self.WIDTH = self.surface.get_width()
        self.HEIGHT = self.surface.get_height()
        self.x = x
        self.y = y

    # 这个方法用于确定鼠标是否点击了对应的按钮
    def check_click(self, position):
        x_match = self.x < position[0] < self.x + self.WIDTH
        y_match = self.y < position[1] < self.y + self.HEIGHT
        if x_match and y_match:
            return True
        else:
            return False


def set_chess(board_inner, x, y, chr):
    if board_inner[x][y] != ' ':
        print('该位置已有棋子')
        print(x, y)
        return False
    else:
        board_inner[x][y] = chr
        print(x, y)
        # for _ in board_inner:
        #     print(_)
        # print()
        return True


def check_win(board_inner):
    for list_str in board_inner:
        if ''.join(list_str).find('O' * 5) != -1:
            print('白棋获胜')
            return 0
        elif ''.join(list_str).find('X' * 5) != -1:
            print('黑棋获胜')
            return 1
    else:
        return -1


def check_win_all(board_inner):
    board_c = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_c[x - y].append(board_inner[x][y])
    board_d = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_d[x + y].append(board_inner[x][y])
    return [check_win(board_inner), check_win([list(i) for i in zip(*board_inner)]), check_win(board_c),
            check_win(board_d)]


# 获得分数
def value(board_inner, temp_list, value_model, chr):
    score = 0
    num = 0
    for list_str in board_inner:
        if ''.join(list_str).count(chr) < 2:
            continue
        a = 0
        for i in range(11):
            if a == 0:
                temp = []
                for j in range(5, 12):
                    if i + j > len(list_str):
                        break
                    num += 1
                    s = ''.join(list_str[i:i + j])
                    s_num = min(s.count(chr), 5)
                    if s_num < 2:
                        continue
                    else:
                        if i == 0:
                            for k in [t for _ in value_model[0].items() for t in _[1] if int(_[0]) <= s_num]:
                                if s == k[1][0]:
                                    temp.append((i, k))
                        else:
                            if i + j < len(list_str):
                                for k in [t for _ in value_model[1].items() for t in _[1] if int(_[0]) <= s_num]:
                                    if s == k[1][0]:
                                        temp.append((i, k))
                            elif i + j == len(list_str):
                                for k in [t for _ in value_model[2].items() for t in _[1] if int(_[0]) <= s_num]:
                                    if s == k[1][0]:
                                        temp.append((i, k))
            else:
                a -= 1
                temp = []
            if temp:
                max_value = max([i[1][1][1] for i in temp])
                max_shape = [i for i in temp if i[1][1][1] == max_value][0]
                if max_shape[1][0] in ['4_1_e', '4_1_1',
                                       '4_2_5', '4_2_6', '4_2_7', '4_2_8_e', '4_2_9',
                                       '4_3_4_s',
                                       '3p_0', '3p_0_1',
                                       '3p_1_3', '3_1_4_e', '3_1_5',
                                       '3_2_5_s',
                                       '3_3', '3_3_1', '3_3_2_e', '3_3_3',
                                       '2_0_5',
                                       '2_1',
                                       '2_2_1', '2_2_2_e', '2_2_3']:
                    a = 1
                elif max_shape[1][0] in ['4_2_1', '4_2_2', '4_2_3_e', '4_2_4',
                                         '4_3', '4_3_8', '4_3_9',
                                         '3p_1', '3_1_1_e', '3_1_2',
                                         '2_0',
                                         '2_2']:
                    a = 2
                elif max_shape[1][0] in ['3p_2']:
                    a = 3
                elif max_shape[1][0] in ['4_2']:
                    a = 5
                temp_list.append(max_shape)
                score += max_value
    return score


# 计算附加分
def additional(te_list):
    score = 0
    temp_list = [i[1][0][:2] for i in te_list]
    if sum([temp_list.count(i) for i in ['4_', '3p']]) >= 2:
        score += 30
    elif sum([temp_list.count(i) for i in ['3p', '3_']]) >= 2 \
            and sum([temp_list.count(i) for i in ['3p']]) > 0:
        score += 15
    return score


# 计算总分
def value_all(board_inner, temp_list, value_model, chr):
    board_c = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_c[x + y].append(board_inner[x][y])
    board_d = [[] for _ in range(29)]
    for x in range(15):
        for y in range(15):
            board_d[x - y].append(board_inner[x][y])
    a = value(board_inner, temp_list, value_model, chr)
    b = value([list(i) for i in zip(*board_inner)], temp_list, value_model, chr)
    c = value(board_c, temp_list, value_model, chr)
    d = value(board_d, temp_list, value_model, chr)
    add = additional(temp_list)
    return a + b + c + d + add


# 计算ai落子
def value_chess(board_inner):
    t1 = time.time()
    if board_inner == [[' '] * 15 for _ in range(15)]:
        return 7, 7, 0
    temp_list_x = []
    temp_list_o = []
    tp_list_x_2 = []
    tp_list_o_2 = []
    tp_list_d = []
    score_x = value_all(board_inner, temp_list_x, value_model_X, 'X')
    pos_x = (0, 0)
    score_o = value_all(board_inner, temp_list_o, value_model_O, 'O')
    pos_o = (0, 0)
    pos_d = (0, 0)
    score_x_2 = 0
    score_o_2 = 0
    score_diff = 0
    chess_range_x = [x for x in range(15) if ''.join(board_inner[x]).replace(' ', '') != '']
    chess_range_y = [y for y in range(15) if ''.join([list(i) for i in zip(*board_inner)][y]).replace(' ', '') != '']
    range_x = (max(0, min(chess_range_x) - 2), min(max(chess_range_x) + 2, 15))
    range_y = (max(0, min(chess_range_y) - 2), min(max(chess_range_y) + 2, 15))
    num = 0
    for x in range(*range_x):
        for y in range(*range_y):
            tp_list_x = []
            tp_list_o = []
            tp_list_c = []
            if board_inner[x][y] != ' ':
                continue
            else:
                num += 1
                board_inner[x][y] = 'X'
                score_a = value_all(board_inner, tp_list_x, value_model_X, 'X')
                score_c = value_all(board_inner, tp_list_c, value_model_O, 'O')
                if score_a > score_x_2:
                    pos_x = x, y
                    tp_list_x_2 = tp_list_x
                    score_x_2 = score_a
                board_inner[x][y] = 'O'
                score_b = value_all(board_inner, tp_list_o, value_model_O, 'O')
                if score_b > score_o_2:
                    pos_o = x, y
                    tp_list_o_2 = tp_list_o
                    score_o_2 = score_b
                board_inner[x][y] = ' '
                diff = 1.1 * (score_a - score_x) + score_o - score_c + score_b - score_c
                if diff > score_diff:
                    pos_d = x, y
                    tp_list_d = tp_list_x
                    score_diff = diff
    print('value_chess本次循环次数：{}'.format(num))
    print("value_chess循环遍历执行完毕，用时{}秒".format(round(time.time() - t1, 2)))
    # 三种不同的策略
    if score_x_2 >= 1000:
        print('——' * 30)
        print('策略1棋面：')
        print('黑棋棋面：', temp_list_x)
        print('白棋棋面：', temp_list_o)
        score = score_x_2
        pos = pos_x
        x, y = pos
        board_inner[x][y] = 'X'
        score_o_e = value_all(board_inner, temp_list_o, value_model_O, 'O')
        board_inner[x][y] = ' '
        print('执行策略1、直接获胜')
        print('黑棋最佳落子：坐标{}，黑棋得分{}，白棋得分{}'.format(pos, score, score_o_e))
        print('白棋原分数{}，预期最高分数{}，分数差值{}'.format(score_o, score_o_2, score_o_2 - score_o))
        print('若白棋落子{}，白棋棋型{}'.format(pos_o, tp_list_o_2))
        print('黑棋原分数{}，预期最高分数{}，分数差值{}'.format(score_x, score_x_2, score_x_2 - score_x))
        print('若黑棋落子{}，黑棋棋型{}'.format(pos_x, tp_list_x_2))
        print('——' * 30)
        print("value_chess执行完毕，用时{}秒".format(round(time.time() - t1, 2)))
    elif score_o_2 >= 1000:
        print('——' * 30)
        print('策略2棋面：')
        print('黑棋棋面：', temp_list_x)
        print('白棋棋面：', temp_list_o)
        x, y = pos_o
        board_inner[x][y] = 'X'
        temp_list_x.clear()
        score = value_all(board_inner, temp_list_x, value_model_X, 'X')
        score_o_e = value_all(board_inner, temp_list_o, value_model_O, 'O')
        board_inner[x][y] = ' '
        pos = pos_o
        print('执行策略2、防守：防止对方获胜')
        print('黑棋最佳落子：坐标{}，黑棋得分{}，白棋得分{}'.format(pos, score, score_o_e))
        print('白棋原分数{}，预期最高分数{}，分数差值{}'.format(score_o, score_o_2, score_o_2 - score_o))
        print('若白棋落子{}，白棋棋型{}'.format(pos_o, tp_list_o_2))
        print('黑棋原分数{}，预期最高分数{}，分数差值{}'.format(score_x, score_x_2, score_x_2 - score_x))
        print('若黑棋落子{}，黑棋棋型{}'.format(pos_x, tp_list_x_2))
        print('——' * 30)
        print("value_chess执行完毕，用时{}秒".format(round(time.time() - t1, 2)))
    else:
        print('——' * 30)
        print('策略3棋面：')
        print('黑棋棋面：', temp_list_x)
        print('白棋棋面：', temp_list_o)
        x, y = pos_d
        board_inner[x][y] = 'X'
        temp_list_x.clear()
        temp_list_o.clear()
        score = value_all(board_inner, temp_list_x, value_model_X, 'X')
        score_o_e = value_all(board_inner, temp_list_o, value_model_O, 'O')
        board_inner[x][y] = 'O'
        score_test = value_all(board_inner, [], value_model_O, 'O')
        board_inner[x][y] = ' '
        pos = pos_d
        print('黑棋原得分', score_x)
        print('黑棋得分', score)
        print('白棋原得分', score_o)
        print('白棋得分', score_o_e)
        print('若该位置落白棋，白棋得分', score_test)
        print('落子后黑棋棋面', temp_list_x)
        print('执行策略3、防守：防守+进攻')
        print('我方增长得分+对方减少得分：{}'.format(score_diff))
        print('黑棋最佳落子：坐标{}，黑棋得分{}，白棋得分{}'.format(pos, score, score_o_e))
        print('白棋原分数{}，预期最高分数{}，分数差值{}'.format(score_o, score_o_2, score_o_2 - score_o))
        print('若白棋落子{}，白棋棋型{}'.format(pos_o, tp_list_o_2))
        print('黑棋原分数{}，预期最高分数{}，分数差值{}'.format(score_x, score_x_2, score_x_2 - score_x))
        print('若黑棋落子{}，黑棋棋型{}'.format(pos_x, tp_list_x_2))
        print('——' * 30)
        print("value_chess执行完毕，用时{}秒".format(round(time.time() - t1, 2)))
    return *pos, score


def main(board_inner):
    pg.init()
    clock = pg.time.Clock()
    objects = []  # 下棋记录列表
    recover_objects = []  # 悔棋记录列表
    ob_list = [objects, recover_objects]
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    black = pg.image.load("data/chess_black.png").convert_alpha()
    white = pg.image.load("data/chess_white.png").convert_alpha()
    background = pg.image.load("data/2.png").convert_alpha()
    regret_button = Button('悔棋', RED, 665, 200)
    recover_button = Button('恢复', BLUE, 665, 300)
    restart_button = Button('重新开始', GREEN, 625, 400)
    screen.blit(regret_button.surface, (regret_button.x, regret_button.y))
    screen.blit(recover_button.surface, (recover_button.x, recover_button.y))
    screen.blit(restart_button.surface, (restart_button.x, restart_button.y))
    pg.display.set_caption("五子棋")
    flag = 0
    going = True
    chess_list = [black, white]
    letter_list = ['X', 'O']
    word_list = ['黑棋', '白棋']
    word_color = [(0, 0, 0), (255, 255, 255)]

    while going:
        screen.blit(background, (0, 0))
        text = font.render("{}回合".format(word_list[flag]), True, word_color[flag])
        text_pos = text.get_rect(centerx=background.get_width() / 2, y=2)
        screen.blit(text, text_pos)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                # 点击了悔棋按钮或者恢复按钮
                if regret_button.check_click(pos) or recover_button.check_click(pos):
                    index = 0 if regret_button.check_click(pos) else 1
                    if ob_list[index]:
                        x, y = [round((p + 18 - 27) / 40) for p in ob_list[index][-1].pos[:2]]
                        board_inner[y][x] = ' ' if index == 0 else ob_list[index][-1].color
                        ob_list[index - 1].append(ob_list[index][-1])
                        ob_list[index].pop()
                        if ob_list[index]:
                            x, y = [round((p + 18 - 27) / 40) for p in ob_list[index][-1].pos[:2]]
                            board_inner[y][x] = ' ' if index == 0 else ob_list[index][-1].color
                            ob_list[index - 1].append(ob_list[index][-1])
                            ob_list[index].pop()
                elif restart_button.check_click(pos):
                    hint_text = font.render("游戏重新开始", True, word_color[flag])
                    hint_text_pos = hint_text.get_rect(centerx=background.get_width() / 2, y=200)
                    screen.blit(hint_text, hint_text_pos)
                    pg.display.update()
                    pg.time.delay(1000)
                    board_inner = [[' '] * 15 for _ in range(15)]
                    objects.clear()
                    recover_objects.clear()
                    flag = 0
                    continue
                else:
                    a, b = round((pos[0] - 27) / 40), round((pos[1] - 27) / 40)
                    if a >= 15 or b >= 15:
                        continue
                    else:
                        x, y = max(0, a) if a < 0 else min(a, 14), max(0, b) if b < 0 else min(b, 14)
                        if set_chess(board_inner, y, x, letter_list[flag]):
                            new_chess = GameObject(chess_list[flag], letter_list[flag], (27 + x * 40, 27 + y * 40))
                            new_chess.target_alpha = 0
                            objects.append(new_chess)
                            recover_objects.clear()
                            if 0 in check_win_all(board_inner) or 1 in check_win_all(board_inner):
                                for o in objects:
                                    screen.blit(o.image, o.pos)
                                win_text = font.render("{}获胜，游戏5秒后重新开始".format(word_list[flag]), True,
                                                       word_color[flag])
                                win_text_pos = win_text.get_rect(centerx=background.get_width() / 2, y=200)
                                screen.blit(win_text, win_text_pos)
                                pg.display.update()
                                pg.time.delay(5000)
                                board_inner = [[' '] * 15 for _ in range(15)]
                                objects.clear()
                                recover_objects.clear()
                                flag = 0
                                continue
                            flag = [1, 0][flag]
                        else:
                            hint_text = font.render("该位置已有棋子", True, word_color[flag])
                            hint_text_pos = hint_text.get_rect(centerx=background.get_width() / 2, y=200)
                            for o in objects:
                                screen.blit(o.image, o.pos)
                            screen.blit(hint_text, hint_text_pos)
                            pg.display.update()
                            pg.time.delay(300)
        # AI执黑落子
        if flag == 0:
            y, x = value_chess(board_inner)[:2]
            if set_chess(board_inner, y, x, letter_list[flag]):
                new_chess = GameObject(chess_list[flag], letter_list[flag], (27 + x * 40, 27 + y * 40))
                new_chess.target_alpha = 0
                objects.append(new_chess)
            if 0 in check_win_all(board_inner) or 1 in check_win_all(board_inner):
                for o in objects:
                    screen.blit(o.image, o.pos)
                win_text = font.render("{}获胜，游戏5秒后重新开始".format(word_list[flag]), True,
                                       word_color[flag])
                win_text_pos = win_text.get_rect(centerx=background.get_width() / 2, y=200)
                screen.blit(win_text, win_text_pos)
                pg.display.update()
                pg.time.delay(5000)
                board_inner = [[' '] * 15 for _ in range(15)]
                objects.clear()
                recover_objects.clear()
                flag = 0
                continue
            flag = [1, 0][flag]

        for o in objects:
            o.update_alpha()
            screen.blit(o.image, o.pos)

        clock.tick(60)
        pg.display.update()


if __name__ == '__main__':
    pg.init()
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    font = pg.font.Font('font/MFJinHei_Noncommercial-Regular.otf', 20)
    font_big = pg.font.Font('font/MFJinHei_Noncommercial-Regular.otf', 40)
    main(board)
    pg.quit()
