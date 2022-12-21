import copy
import random

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

    # AI
    def ai_move1(self):
        possible_moves = []
        for i in range(1, self.mode_num+1):
            for j in range(1, self.mode_num+1):
                if self.chessboard[i][j] == 0:
                    possible_moves.append([i, j])
        if len(possible_moves)-1 < 0:
            return
        index = random.randint(0, len(possible_moves)-1)
        i = possible_moves[index][0]
        j = possible_moves[index][1]
        self.chessboard[i][j] = self.backend.present+1
        self.last_3_chessboard = copy.deepcopy(self.last_2_chessboard)
        self.last_2_chessboard = copy.deepcopy(self.last_1_chessboard)
        self.last_1_chessboard = copy.deepcopy(self.chessboard)
        self.backend.updateboard([[i, j]])
        self.backend.lookback.add_move(self.backend.present, i, j)  # 添加记录

    def ai_move2(self):  # 找现有棋子的周围下棋
        my_chess = self.backend.present+1
        for i in range(1, self.mode_num+1):
            for j in range(1, self.mode_num+1):
                if self.chessboard[i][j] == my_chess:
                    for x in range(-1,2):
                        for y in range(-1,2):
                            if self.chessboard[i+x][j+y] == 0:
                                self.chessboard[i+x][j+y] = my_chess
                                self.last_3_chessboard = copy.deepcopy(self.last_2_chessboard)
                                self.last_2_chessboard = copy.deepcopy(self.last_1_chessboard)
                                self.last_1_chessboard = copy.deepcopy(self.chessboard)
                                self.backend.updateboard([[i+x, j+y]])
                                self.backend.lookback.add_move(self.backend.present, i+x, j+y)  # 添加记录
                                return
                            elif self.chessboard[i+x][j+y] == my_chess and self.chessboard[i-x][j-y] == 0:
                                self.chessboard[i-x][j-y] = my_chess
                                self.last_3_chessboard = copy.deepcopy(self.last_2_chessboard)
                                self.last_2_chessboard = copy.deepcopy(self.last_1_chessboard)
                                self.last_1_chessboard = copy.deepcopy(self.chessboard)
                                self.backend.updateboard([[i - x, j - y]])
                                self.backend.lookback.add_move(self.backend.present, i - x, j - y)  # 添加记录
                                return
        self.ai_move1()  # 不行就随便下


    def getDown(self, x, y):
        # 判断位置是否已经被占据
        if self.chessboard[y][x] == 0:
            # 未被占据，则尝试占据
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