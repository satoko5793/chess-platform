# 导入GUI模块
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox

import copy


class Window(Tk):
    def __init__(self, backend, window_size, dd, p, chessboard_size=9):
        Tk.__init__(self)
        self.backend = backend
        # 模式，九路棋：9，十三路棋：13，十九路棋：19
        self.mode_num = chessboard_size
        self.window_size = window_size
        self.dd = dd  # 棋盘每格的边长
        # 棋盘的相对矫正比例
        self.p = p
        # 记录鼠标经过的地方，用于显示shadow时
        self.cross_last = None
        # 图片资源，存放在当前目录下的/Pictures/中
        self.photoW = PhotoImage(file="./Pictures/W.png")
        self.photoB = PhotoImage(file="./Pictures/B.png")
        self.photoBD = PhotoImage(file="./Pictures/" + "BD" + "-" + str(self.mode_num) + ".png")
        self.photoWD = PhotoImage(file="./Pictures/" + "WD" + "-" + str(self.mode_num) + ".png")
        self.photoBU = PhotoImage(file="./Pictures/" + "BU" + "-" + str(self.mode_num) + ".png")
        self.photoWU = PhotoImage(file="./Pictures/" + "WU" + "-" + str(self.mode_num) + ".png")
        # 用于黑白棋子图片切换的列表
        self.photoWBU_list = [self.photoBU, self.photoWU]
        self.photoWBD_list = [self.photoBD, self.photoWD]
        # 窗口大小
        self.geometry(str(int(600 * self.window_size)) + 'x' + str(int(400 * self.window_size)))
        # 画布控件，作为容器
        self.canvas_bottom = Canvas(self, bg='#38A', bd=0, width=600 * self.window_size, height=400 * self.window_size)
        self.canvas_bottom.place(x=0, y=0)
        # 切换游戏类型按钮
        self.changeButton = Button(self, text=('五子棋' if self.backend.chess_type == 0 else '围棋'), command=self.backend.newGame3)
        self.changeButton.place(x=480 * self.window_size, y=175 * self.window_size)
        # 几个功能按钮
        self.startButton = Button(self, text='开始游戏', command=self.backend.start)
        self.startButton.place(x=480 * self.window_size, y=200 * self.window_size)
        self.passmeButton = Button(self, text='弃一手', command=self.backend.passme)
        self.passmeButton.place(x=480 * self.window_size, y=225 * self.window_size)
        self.regretButton = Button(self, text='悔棋', command=self.backend.regret)
        self.regretButton.place(x=480 * self.window_size, y=250 * self.window_size)
        # 初始悔棋按钮禁用
        self.regretButton['state'] = DISABLED
        self.replayButton = Button(self, text='重新开始', command=self.backend.reload)
        self.replayButton.place(x=480 * self.window_size, y=275 * self.window_size)
        self.newGameButton1 = Button(self, text=('十三' if self.mode_num == 9 else '九') + '路棋', command=self.backend.newGame1)
        self.newGameButton1.place(x=480 * self.window_size, y=300 * self.window_size)
        self.newGameButton2 = Button(self, text=('十三' if self.mode_num == 19 else '十九') + '路棋', command=self.backend.newGame2)
        self.newGameButton2.place(x=480 * self.window_size, y=325 * self.window_size)
        self.quitButton = Button(self, text='退出游戏', command=self.quit)
        self.quitButton.place(x=480 * self.window_size, y=350 * self.window_size)
        # 画棋盘，填充颜色
        self.canvas_bottom.create_rectangle(
            0 * self.window_size, 0 * self.window_size, 400 * self.window_size, 400 * self.window_size, fill='#c51')
        # 刻画棋盘线及九个点
        # 先画外框粗线
        self.canvas_bottom.create_rectangle(
            20 * self.window_size, 20 * self.window_size, 380 * self.window_size, 380 * self.window_size, width=3)
        # 棋盘上的九个定位点，以中点为模型，移动位置，以作出其余八个点
        for m in [-1, 0, 1]:
            for n in [-1, 0, 1]:
                self.original = self.canvas_bottom.create_oval(200 * self.window_size - self.window_size * 2,
                                                               200 * self.window_size - self.window_size * 2,
                                                               200 * self.window_size + self.window_size * 2,
                                                               200 * self.window_size + self.window_size * 2,
                                                               fill='#000')
                self.canvas_bottom.move(self.original,
                                        m * self.dd * (2 if self.mode_num == 9 else (3 if self.mode_num == 13 else 6)),
                                        n * self.dd * (2 if self.mode_num == 9 else (3 if self.mode_num == 13 else 6)))
        # 画中间的线条
        for i in range(1, self.mode_num - 1):
            self.canvas_bottom.create_line(20 * self.window_size, 20 * self.window_size + i * self.dd,
                                           380 * self.window_size,
                                           20 * self.window_size + i * self.dd, width=2)
            self.canvas_bottom.create_line(20 * self.window_size + i * self.dd, 20 * self.window_size,
                                           20 * self.window_size + i * self.dd,
                                           380 * self.window_size, width=2)
        # 放置右侧初始图片
        self.pW = self.canvas_bottom.create_image(500 * self.window_size + 11, 65 * self.window_size, image=self.photoW)
        self.pB = self.canvas_bottom.create_image(500 * self.window_size - 11, 65 * self.window_size, image=self.photoB)
        # 每张图片都添加image标签，方便reload函数删除图片
        self.canvas_bottom.addtag_withtag('image', self.pW)
        self.canvas_bottom.addtag_withtag('image', self.pB)
        # 鼠标移动时，调用shadow函数，显示随鼠标移动的棋子
        self.canvas_bottom.bind('<Motion>', self.shadow)
        # 鼠标左键单击时，调用getdown函数，放下棋子
        self.canvas_bottom.bind('<Button-1>', self.backend.getDown)
        # 设置退出快捷键<Ctrl>+<D>，快速退出游戏
        self.bind('<Control-KeyPress-d>', self.backend.keyboardQuit)

    # 以下四个函数实现了右侧太极图的动态创建与删除
    def create_pW(self):
        self.pW = self.canvas_bottom.create_image(500 * self.window_size + 11, 65 * self.window_size,
                                                  image=self.photoW)
        self.canvas_bottom.addtag_withtag('image', self.pW)

    def create_pB(self):
        self.pB = self.canvas_bottom.create_image(500 * self.window_size - 11, 65 * self.window_size,
                                                  image=self.photoB)
        self.canvas_bottom.addtag_withtag('image', self.pB)

    def del_pW(self):
        self.canvas_bottom.delete(self.pW)

    def del_pB(self):
        self.canvas_bottom.delete(self.pB)

    def start(self, present):
        # 删除右侧太极图
        self.canvas_bottom.delete(self.pW)
        self.canvas_bottom.delete(self.pB)
        # 利用右侧图案提示开始时谁先落子
        if present == 0:
            self.create_pB()
            self.del_pW()
        else:
            self.create_pW()
            self.del_pB()

    def player_change(self, present):
        if present == 0:
            self.create_pW()
            self.del_pB()
        else:
            self.create_pB()
            self.del_pW()

    def regret(self, present):
        self.canvas_bottom.delete('image')
        if present == 0:
            self.create_pB()
        else:
            self.create_pW()

    def reload(self):
        self.canvas_bottom.delete('image')
        self.create_pB()

    # 显示鼠标移动下棋子的移动
    def shadow(self, event):
        if not self.backend.stop:
            # 找到最近格点，在当前位置靠近的格点出显示棋子图片，并删除上一位置的棋子图片
            if (10 * self.window_size < event.x < 390 * self.window_size) \
                    and (10 * self.window_size < event.y < 390 * self.window_size):  # 稍微放宽显示的范围
                dx = (event.x - 20 * self.window_size) % self.dd
                dy = (event.y - 20 * self.window_size) % self.dd
                self.cross = self.canvas_bottom.create_image(
                    event.x - dx + round(dx / self.dd) * self.dd + 22 * self.p,
                    event.y - dy + round(dy / self.dd) * self.dd - 27 * self.p,
                    image=self.photoWBU_list[self.backend.present])
                self.canvas_bottom.addtag_withtag('image', self.cross)
                if self.cross_last != None:
                    self.canvas_bottom.delete(self.cross_last)
                self.cross_last = self.cross
            else:  # 出棋盘也不显示
                self.canvas_bottom.delete(self.cross_last)

    # 警告消息框，接受标题和警告信息
    def showwarningbox(self, title, message):
        self.canvas_bottom.delete(self.cross)
        tkinter.messagebox.showwarning(title, message)

    def add_image(self, x, y, p1, p2, present):
        self.image_added = self.canvas_bottom.create_image(x, y, image=self.photoWBD_list[present])
        self.canvas_bottom.addtag_withtag('image', self.image_added)
        # 棋子与位置标签绑定，方便“杀死”
        self.canvas_bottom.addtag_withtag('position' + str(p1) + str(p2), self.image_added)

    def create_sign(self, x1, x2, x3, x4):
        # 删除上次的标记，重新创建标记
        self.canvas_bottom.delete('image_added_sign')
        self.image_added_sign = self.canvas_bottom.create_oval(x1, x2, x3, x4, width=3, outline='#3ae')
        self.canvas_bottom.addtag_withtag('image', self.image_added_sign)
        self.canvas_bottom.addtag_withtag('image_added_sign', self.image_added_sign)


class board:
    def __init__(self, chessboard_size=9):
        # 模式，九路棋：9，十三路棋：13，十九路棋：19
        self.mode_num = chessboard_size
        # 棋盘阵列,超过边界：-1，无子：0，黑棋：1，白棋：2
        self.chessboard = [[0 for i in range(self.mode_num + 2)] for i in range(self.mode_num + 2)]
        for m in range(self.mode_num + 2):
            for n in range(self.mode_num + 2):
                if m == 0 or n == 0 or m == self.mode_num + 1 or n == self.mode_num + 1:
                    self.chessboard[m][n] = -1
        # 拷贝三份棋盘“快照”，悔棋和判断“打劫”时需要作参考
        self.last_3_chessboard = copy.deepcopy(self.chessboard)
        self.last_2_chessboard = copy.deepcopy(self.chessboard)
        self.last_1_chessboard = copy.deepcopy(self.chessboard)

    def passme(self):
        # 拷贝棋盘状态，记录前三次棋局
        self.last_3_chessboard = copy.deepcopy(self.last_2_chessboard)
        self.last_2_chessboard = copy.deepcopy(self.last_1_chessboard)
        self.last_1_chessboard = copy.deepcopy(self.chessboard)

    def regret(self):
        list_of_b = []
        list_of_w = []
        for m in range(1, self.mode_num + 1):
            for n in range(1, self.mode_num + 1):
                self.chessboard[m][n] = 0
        for m in range(len(self.last_3_chessboard)):
            for n in range(len(self.last_3_chessboard[m])):
                if self.last_3_chessboard[m][n] == 1:
                    list_of_b += [[n, m]]
                elif self.last_3_chessboard[m][n] == 2:
                    list_of_w += [[n, m]]
        self.last_1_chessboard = copy.deepcopy(self.last_3_chessboard)
        for m in range(1, self.mode_num + 1):
            for n in range(1, self.mode_num + 1):
                self.last_2_chessboard[m][n] = 0
                self.last_3_chessboard[m][n] = 0
        return list_of_b, list_of_w

    def reload(self):
        for m in range(1, self.mode_num + 1):
            for n in range(1, self.mode_num + 1):
                self.chessboard[m][n] = 0
                self.last_3_chessboard[m][n] = 0
                self.last_2_chessboard[m][n] = 0
                self.last_1_chessboard[m][n] = 0
        return


class weiqi_board(board):
    def __init__(self, backend, window_size, dd, p, chessboard_size=9):
        super().__init__(chessboard_size)
        self.backend = backend
        # 模式，九路棋：9，十三路棋：13，十九路棋：19
        self.mode_num = chessboard_size
        self.window_size = window_size
        self.dd = dd  # 棋盘每格的边长
        # 棋盘的相对矫正比例
        self.p = p
        # 是否上一步跳过
        self.passed = False

    # 判断棋子（种类为yourChessman，位置为yourPosition）是否无气（死亡），有气则返回False，无气则返回无气棋子的列表
    # 本函数是游戏规则的关键，初始deadlist只包含了自己的位置，每次执行时，函数尝试寻找yourPosition周围有没有空的位置，有则结束，返回False代表有气；
    # 若找不到，则找自己四周的同类（不在deadlist中的）是否有气，即调用本函数，无气，则把该同类加入到deadlist，然后找下一个邻居，只要有一个有气，返回False代表有气；
    # 若四周没有一个有气的同类，返回deadlist,至此结束递归

    def if_dead(self, deadList, yourChessman, yourPosition):
        for i in [-1, 1]:
            if [yourPosition[0] + i, yourPosition[1]] not in deadList:
                if self.chessboard[yourPosition[1]][yourPosition[0] + i] == 0:
                    return False
            if [yourPosition[0], yourPosition[1] + i] not in deadList:
                if self.chessboard[yourPosition[1] + i][yourPosition[0]] == 0:
                    return False
        if ([yourPosition[0] + 1, yourPosition[1]] not in deadList) and (
                self.chessboard[yourPosition[1]][yourPosition[0] + 1] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0] + 1, yourPosition[1]]], yourChessman,
                                  [yourPosition[0] + 1, yourPosition[1]])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0] - 1, yourPosition[1]] not in deadList) and (
                self.chessboard[yourPosition[1]][yourPosition[0] - 1] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0] - 1, yourPosition[1]]], yourChessman,
                                  [yourPosition[0] - 1, yourPosition[1]])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0], yourPosition[1] + 1] not in deadList) and (
                self.chessboard[yourPosition[1] + 1][yourPosition[0]] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0], yourPosition[1] + 1]], yourChessman,
                                  [yourPosition[0], yourPosition[1] + 1])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        if ([yourPosition[0], yourPosition[1] - 1] not in deadList) and (
                self.chessboard[yourPosition[1] - 1][yourPosition[0]] == yourChessman):
            midvar = self.if_dead(deadList + [[yourPosition[0], yourPosition[1] - 1]], yourChessman,
                                  [yourPosition[0], yourPosition[1] - 1])
            if not midvar:
                return False
            else:
                deadList += copy.deepcopy(midvar)
        return deadList

    # 落子后，依次判断四周是否有棋子被杀死，并返回死棋位置列表
    def get_deadlist(self, x, y):
        deadlist = []
        for i in [-1, 1]:
            if self.chessboard[y][x + i] == (2 if self.backend.present == 0 else 1) and ([x + i, y] not in deadlist):
                killList = self.if_dead([[x + i, y]], (2 if self.backend.present == 0 else 1), [x + i, y])
                if not killList == False:
                    deadlist += copy.deepcopy(killList)
            if self.chessboard[y + i][x] == (2 if self.backend.present == 0 else 1) and ([x, y + i] not in deadlist):
                killList = self.if_dead([[x, y + i]], (2 if self.backend.present == 0 else 1), [x, y + i])
                if not killList == False:
                    deadlist += copy.deepcopy(killList)
        return deadlist

    def getDown(self, x, y):
        # 判断位置是否已经被占据
        if self.chessboard[y][x] == 0:
            # 未被占据，则尝试占据，获得占据后能杀死的棋子列表
            self.chessboard[y][x] = self.backend.present + 1
            deadlist = self.get_deadlist(x, y)
            self.backend.kill(deadlist)
            # 判断是否重复棋局
            if not self.last_2_chessboard == self.chessboard:
                # 判断是否属于有气和杀死对方其中之一
                if len(deadlist) > 0 or self.if_dead([[x, y]], self.backend.present + 1, [x, y]) == False:
                    # 当不重复棋局，且属于有气和杀死对方其中之一时，落下棋子有效
                    self.last_3_chessboard = copy.deepcopy(self.last_2_chessboard)
                    self.last_2_chessboard = copy.deepcopy(self.last_1_chessboard)
                    self.last_1_chessboard = copy.deepcopy(self.chessboard)
                    self.passed = False  # 清除弃子标记
                    return "落子有效"
                else:
                    # 不属于杀死对方或有气，则判断为无气，警告并弹出警告框
                    self.chessboard[y][x] = 0
                    return "无气"
            else:
                # 重复棋局，警告打劫
                self.chessboard[y][x] = 0
                self.backend.recover(deadlist, (1 if self.backend.present == 0 else 0))
                return "打劫"
        else:
            # 覆盖，声音警告
            return "覆盖"

    def check_win(self):
        komi = 7.5  # 贴目采用中国规则
        blacks = []
        whites = []
        black_territory = set()
        white_territory = set()
        neutral_territory = set()
        visited_stones = None

        # results={} #存放空子的地域属于哪个势力，有三种：黑、白、中立
        def findBoarders(stone, visited_stones=None):
            boarders = set()
            neighbours = [  # 按下、左、上、右顺时针的顺序
                (stone[0]-1, stone[1]),
                (stone[0], stone[1]-1),
                (stone[0]+1, stone[1]),
                (stone[0], stone[1]+1)
            ]
            for i in neighbours:
                if not (1 <= i[0] <= self.mode_num and 1 <= i[1] <= self.mode_num) or i in visited_stones:
                    continue
                if self.chessboard[i[0]][i[1]] == 0:  # 当前点位无子
                    visited_stones.add(i)
                    boarders |= findBoarders(i, visited_stones)
                elif self.chessboard[i[0]][i[1]] == 1:  # 当前点位为黑子
                    boarders.add(1)
                elif self.chessboard[i[0]][i[1]] == 2:  # 当前点位为白子
                    boarders.add(2)
                else:
                    pass
            return boarders

        # 组个点来看
        for i in range(1, self.mode_num+1):
            for j in range(1, self.mode_num+1):
                if self.chessboard[i][j] == 0:
                    if (i, j) in black_territory or (i, j) in white_territory or (i, j) in neutral_territory:
                        continue
                    else:
                        visited_stones = {(i, j)}
                        boarders = findBoarders((i, j), visited_stones)
                        if len(boarders) != 1:
                            neutral_territory |= visited_stones
                        else:
                            if 1 in boarders:  # 若边界被黑子占领
                                black_territory |= visited_stones
                            else:  # 若边界被白子占领
                                white_territory |= visited_stones
                elif self.chessboard[i][j] == 1:
                    blacks.append((i, j))
                elif self.chessboard[i][j] == 2:
                    whites.append((i, j))
                else:
                    pass
        black_counts = len(blacks) + len(black_territory)
        white_counts = len(whites) + len(white_territory)
        return black_counts - (white_counts + komi)


class wuziqi_board(board):
    def __init__(self, backend, window_size, dd, p, chessboard_size=9):
        super().__init__(chessboard_size)
        self.backend = backend
        # 模式，九路棋：9，十三路棋：13，十九路棋：19
        self.mode_num = chessboard_size
        self.window_size = window_size
        self.dd = dd  # 棋盘每格的边长
        # 棋盘的相对矫正比例
        self.p = p

    def getDown(self, x, y):
        # 判断位置是否已经被占据
        if self.chessboard[y][x] == 0:
            # 未被占据，则尝试占据，获得占据后能杀死的棋子列表
            self.chessboard[y][x] = self.backend.present + 1
            self.last_3_chessboard = copy.deepcopy(self.last_2_chessboard)
            self.last_2_chessboard = copy.deepcopy(self.last_1_chessboard)
            self.last_1_chessboard = copy.deepcopy(self.chessboard)
            return "落子有效"
        else:
            # 覆盖，声音警告
            return "覆盖"

    def check_win(self):
        win_flag, winner = 0, -1
        n = self.mode_num
        for i in range(1, n+1):
            for j in range(1, n+1):
                if self.chessboard[i][j] != 0:
                    # 检查 每行 是否有连续五个同一颜色的棋子
                    if i + 1 < n+1 and i + 2 < n+1 and i + 3 < n+1 and i + 4 < n+1:
                        if self.chessboard[i][j] == self.chessboard[i + 1][j] and \
                                self.chessboard[i][j] == self.chessboard[i + 2][j] and \
                                self.chessboard[i][j] == self.chessboard[i + 3][j] and \
                                self.chessboard[i][j] == self.chessboard[i + 4][j]:
                            win_flag = 1
                            winner = self.chessboard[i][j]
                            break

                    # 检查 每列 是否有连续五个同一颜色的棋子
                    if j + 1 < n+1 and j + 2 < n+1 and j + 3 < n+1 and j + 4 < n+1:
                        if self.chessboard[i][j] == self.chessboard[i][j + 1] and \
                                self.chessboard[i][j] == self.chessboard[i][j + 2] and \
                                self.chessboard[i][j] == self.chessboard[i][j + 3] and \
                                self.chessboard[i][j] == self.chessboard[i][j + 4]:
                            win_flag = 1
                            winner = self.chessboard[i][j]
                            break

                    # 检查 斜线上 是否有连续五个同一颜色的棋子
                    if i + 1 < n+1 and i + 2 < n+1 and i + 3 < n+1 and i + 4 < n+1 \
                            and j + 1 < n+1 and j + 2 < n+1 and j + 3 < n+1 and j + 4 < n+1:
                        if self.chessboard[i][j] == self.chessboard[i + 1][j + 1] and \
                                self.chessboard[i][j] == self.chessboard[i + 2][j + 2] and \
                                self.chessboard[i][j] == self.chessboard[i + 3][j + 3] and \
                                self.chessboard[i][j] == self.chessboard[i + 4][j + 4]:
                            win_flag = 1
                            winner = self.chessboard[i][j]
                            break
                    if i - 1 > 0 and i - 2 > 0 and i - 3 > 0 and i - 4 > 0 \
                            and j + 1 < n+1 and j + 2 < n+1 and j + 3 < n+1 and j + 4 < n+1:
                        if self.chessboard[i][j] == self.chessboard[i - 1][j + 1] and \
                                self.chessboard[i][j] == self.chessboard[i - 2][j + 2] and \
                                self.chessboard[i][j] == self.chessboard[i - 3][j + 3] and \
                                self.chessboard[i][j] == self.chessboard[i - 4][j + 4]:
                            win_flag = 1
                            winner = self.chessboard[i][j]
                            break
        tie = True
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if self.chessboard[i][j] == 0:
                    return win_flag, winner
        if tie:
            win_flag = 2
        return win_flag, winner


class Chess:
    def __init__(self, chessboard_size=9, chess_type=0):
        # 种类：围棋：0，五子棋：1
        self.chess_type = chess_type
        # 模式，九路棋：9，十三路棋：13，十九路棋：19
        self.mode_num = chessboard_size
        self.window_size = 1.8
        self.dd = 360 * self.window_size / (self.mode_num - 1)  # 棋盘每格的边长
        # 棋盘的相对矫正比例
        self.p = 1 if self.mode_num == 9 else (2 / 3 if self.mode_num == 13 else 4 / 9)
        self.window = Window(self, self.window_size, self.dd, self.p, chessboard_size)
        if self.chess_type == 1:
            self.window.passmeButton['state'] = DISABLED  # 五子棋没有弃子
        if self.chess_type == 0:
            self.board = weiqi_board(self, self.window_size, self.dd, self.p, chessboard_size)
        else:
            self.board = wuziqi_board(self, self.window_size, self.dd, self.p, chessboard_size)
        # 当前轮到的玩家，黑：0，白：1，执黑先行
        self.present = 0
        # 初始停止，点击“开始游戏”运行游戏
        self.stop = True
        # 悔棋次数，次数大于0才可悔棋，初始置0（初始不能悔棋），悔棋后置0，下棋或弃手时恢复为1，以禁止连续悔棋
        self.regretchance = 0

    # 开始游戏函数
    def start(self):
        # 图标处理
        self.window.start(self.present)
        # 开始标志，解除stop
        self.stop = None

    # 放弃一手函数，跳过落子环节
    def passme(self):
        # 悔棋恢复
        if not self.regretchance == 1:
            self.regretchance += 1
        else:
            self.window.regretButton['state'] = NORMAL
        # 拷贝棋盘状态，记录前三次棋局
        self.board.passme()
        self.window.canvas_bottom.delete('image_added_sign')
        # 围棋连续弃子则结算
        if self.chess_type == 0:
            if not self.board.passed:
                self.board.passed = True
            else:
                result = self.board.check_win()
                self.stop = True
                message = ("黑子" if result > 0 else "白子") + "胜利！"  # 黑子给白子贴3.75目，该规则下无法平局
                self.window.showwarningbox("游戏结束", message)

        # 轮到下一玩家
        self.window.player_change(self.present)
        self.present = 1 - self.present

    # 悔棋函数，可悔棋一回合，下两回合不可悔棋
    def regret(self):
        # 判定是否可以悔棋，以前第三手棋局复原棋盘
        if self.regretchance == 1:
            self.regretchance = 0
            self.window.regretButton['state'] = DISABLED
            self.window.regret(self.present)  # 修改UI
            list_of_b, list_of_w = self.board.regret()
            self.recover(list_of_b, 0)
            self.recover(list_of_w, 1)

    # 重新加载函数,删除图片，序列归零，设置一些初始参数，点击“重新开始”时调用
    def reload(self):
        if self.stop == 1:
            self.stop = 0
        self.regretchance = 0
        self.present = 0
        self.window.reload()
        self.board.reload()

    # 落子，并驱动玩家的轮流下棋行为
    def getDown(self, event):
        if not self.stop:
            # 先找到最近格点
            if (20 * self.window_size - self.dd * 0.4 < event.x < self.dd * 0.4 + 380 * self.window_size) and (
                    20 * self.window_size - self.dd * 0.4 < event.y < self.dd * 0.4 + 380 * self.window_size):
                dx = (event.x - 20 * self.window_size) % self.dd
                dy = (event.y - 20 * self.window_size) % self.dd
                x = int((event.x - 20 * self.window_size - dx) / self.dd + round(dx / self.dd) + 1)
                y = int((event.y - 20 * self.window_size - dy) / self.dd + round(dy / self.dd) + 1)
                # 判断位置是否已经被占据
                result = self.board.getDown(x, y)
                if result != "覆盖":
                    self.window.add_image(
                        event.x - dx + round(dx / self.dd) * self.dd + 4 * self.p,
                        event.y - dy + round(dy / self.dd) * self.dd - 5 * self.p,
                        x, y, self.present
                    )
                    if self.chess_type == 0:  # 围棋落子
                        if result == "落子有效":
                            # 当不重复棋局，且属于有气和杀死对方其中之一时，落下棋子有效
                            if not self.regretchance == 1:
                                self.regretchance += 1
                            else:
                                self.window.regretButton['state'] = NORMAL
                            # 删除上次的标记，重新创建标记
                            self.window.create_sign(
                                event.x - dx + round(dx / self.dd) * self.dd + 0.5 * self.dd,
                                event.y - dy + round(dy / self.dd) * self.dd + 0.5 * self.dd,
                                event.x - dx + round(dx / self.dd) * self.dd - 0.5 * self.dd,
                                event.y - dy + round(dy / self.dd) * self.dd - 0.5 * self.dd
                            )
                            # 轮到下一玩家
                            self.window.player_change(self.present)
                            self.present = 1 - self.present
                        elif result == "无气":
                            self.window.canvas_bottom.delete('position' + str(x) + str(y))
                            self.window.bell()
                            self.window.showwarningbox('无气', "你被包围了！")
                        elif result == "打劫":
                            self.window.canvas_bottom.delete('position' + str(x) + str(y))
                            self.window.bell()
                            self.window.showwarningbox("打劫", "此路不通！")
                    else:  # 五子棋落子
                        # 落下棋子有效
                        if not self.regretchance == 1:
                            self.regretchance += 1
                        else:
                            self.window.regretButton['state'] = NORMAL
                        # 删除上次的标记，重新创建标记
                        self.window.create_sign(
                            event.x - dx + round(dx / self.dd) * self.dd + 0.5 * self.dd,
                            event.y - dy + round(dy / self.dd) * self.dd + 0.5 * self.dd,
                            event.x - dx + round(dx / self.dd) * self.dd - 0.5 * self.dd,
                            event.y - dy + round(dy / self.dd) * self.dd - 0.5 * self.dd
                        )
                        # 轮到下一玩家
                        self.window.player_change(self.present)
                        self.present = 1 - self.present
                        win, winner = self.board.check_win()
                        if win:
                            self.stop = True
                            if win == 1:
                                message = ("黑子" if winner == 1 else "白子") + "胜利！"
                            else:
                                message = "平局，无子可下"
                            self.window.showwarningbox("游戏结束", message)
                else:
                    # 覆盖，声音警告
                    self.window.bell()
            else:
                # 超出边界，声音警告
                self.window.bell()

    # 恢复位置列表list_to_recover为b_or_w指定的棋子
    def recover(self, list_to_recover, b_or_w):
        if len(list_to_recover) > 0:
            for i in range(len(list_to_recover)):
                self.board.chessboard[list_to_recover[i][1]][list_to_recover[i][0]] = b_or_w + 1
                self.window.add_image(
                    20 * self.window_size + (list_to_recover[i][0] - 1) * self.dd + 4 * self.p,
                    20 * self.window_size + (list_to_recover[i][1] - 1) * self.dd - 5 * self.p,
                    list_to_recover[i][0], list_to_recover[i][1], b_or_w
                )

    # 杀死位置列表killList中的棋子，即删除图片，位置值置0
    def kill(self, killList):
        if len(killList) > 0:
            for i in range(len(killList)):
                self.board.chessboard[killList[i][1]][killList[i][0]] = 0
                self.window.canvas_bottom.delete('position' + str(killList[i][0]) + str(killList[i][1]))

    # 键盘快捷键退出游戏
    def keyboardQuit(self, event):
        self.window.quit()

    # 以下两个函数修改全局变量值，newApp使主函数循环，以建立不同参数的对象
    def newGame1(self):
        global mode_num, newApp
        mode_num = (13 if self.mode_num == 9 else 9)
        newApp = True
        self.window.quit()

    def newGame2(self):
        global mode_num, newApp
        mode_num = (13 if self.mode_num == 19 else 19)
        newApp = True
        self.window.quit()

    def newGame3(self):
        global chess_type, newApp
        chess_type = 1 - chess_type
        newApp = True
        self.window.quit()


# 声明全局变量，用于新建Application对象时切换成不同模式的游戏
global mode_num, newApp, chess_type
mode_num = 9
newApp = False
chess_type = 0  # 0表示围棋，1表示五子棋
if __name__ == '__main__':
    # 循环，直到不切换游戏模式
    while True:
        newApp = False
        app = Chess(mode_num, chess_type)
        app.window.title('围棋' if chess_type == 0 else '五子棋')
        app.window.mainloop()
        if newApp:
            app.window.destroy()
        else:
            break
