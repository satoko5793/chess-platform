from boards import *

class heibai_board(board):
    def __init__(self, backend, window_size, dd, p, chessboard_size=9):
        super().__init__(chessboard_size)
        self.backend = backend
        # 模式，九路棋：9，十三路棋：13，十九路棋：19
        self.mode_num = chessboard_size
        self.window_size = window_size
        self.dd = dd  # 棋盘每格的边长
        # 棋盘的相对矫正比例
        self.p = p

    def init(self):
        mid = self.mode_num // 2
        self.chessboard[mid][mid] = 1
        self.chessboard[mid + 1][mid + 1] = 1
        self.chessboard[mid + 1][mid] = 2
        self.chessboard[mid][mid + 1] = 2
        self.backend.updateboard()
        # 拷贝三份棋盘“快照”，悔棋和判断“打劫”时需要作参考
        self.last_3_chessboard = copy.deepcopy(self.chessboard)
        self.last_2_chessboard = copy.deepcopy(self.chessboard)
        self.last_1_chessboard = copy.deepcopy(self.chessboard)
        # 可下位置和对应修改棋子
        self.drop_points = None
        self.change_points = None
        self.get_avalible_drop()

    def getDown(self, x, y):
        # 判断位置是否已经被占据
        if [y, x] in self.drop_points:
            # 属于可以落子的位置，则尝试占据
            self.chessboard[y][x] = self.backend.present + 1
            self.change_chess(y, x)
            self.last_3_chessboard = copy.deepcopy(self.last_2_chessboard)
            self.last_2_chessboard = copy.deepcopy(self.last_1_chessboard)
            self.last_1_chessboard = copy.deepcopy(self.chessboard)
            return "落子有效"
        else:
            # 覆盖，声音警告
            return "覆盖"

    # 修改棋子
    def change_chess(self, row, col):
        try:
            index = self.drop_points.index([row, col])
        except:
            print("输入行列不可落子，算法有问题")
            return
        for i in self.change_points[index]:
            r = i[0]
            c = i[1]
            self.chessboard[r][c] = 2//self.chessboard[r][c]  # 2变1， 1变2
        # 调用 platform 函数修改棋盘棋子颜色
        self.backend.delete_image(self.change_points[index])
        self.backend.updateboard(self.change_points[index])
        return

    def search_avalible_drop(self, player):
        ava = []
        ava_row = []
        current_player = player
        for row in range(1, self.mode_num + 1):
            for col in range(1, self.mode_num + 1):
                ava_row = self.search_row(row, col, current_player)
                ava_col = self.search_col(row, col, current_player)
                ava_dig = self.search_diagonal(row, col, current_player)
                ava_fdig = self.search_fdiagonal(row, col, current_player)
                if ava_row != []:
                    ava.append(ava_row)
                if ava_col != []:
                    ava.append(ava_col)
                if ava_dig != []:
                    ava.append(ava_dig)
                if ava_fdig != []:
                    ava.append(ava_fdig)
        drop_points, change_points = self.format_avalible_drop(ava)
        return drop_points, change_points

    def get_avalible_drop(self):  # 通过当前玩家序号，当前局面矩阵以及落子点计算新的局面矩阵
        current_player = self.backend.present
        drop_points, change_points = self.search_avalible_drop(current_player)
        self.drop_points = drop_points
        self.change_points = change_points
        for i in range(self.mode_num+2):
            print(self.chessboard[i])
        print("drop_points:", drop_points)
        print("change_points:", change_points)

    def search_row(self, row, col, current_player):  # 竖向搜索 输入坐标，玩家序号，当前局面矩阵判断是否可以落子
        avalible_row = []
        avalible_row_u = []
        avalible_row_d = []
        opponent = (1-current_player)+1  # 对手在棋盘上的棋子的序号
        current_situation = self.chessboard
        if self.chessboard[row][col] == 0:
            for i in range(row + 1, self.mode_num+2):
                if current_situation[i][col] == opponent:
                    avalible_row_u.append([i, col])
                else:
                    if current_situation[i][col] == 0 or current_situation[i][col] == -1:
                        avalible_row_u = []
                    break
            for i in range(1, row+1):
                if current_situation[row - i][col] == opponent:
                    avalible_row_d.append([row - i, col])
                else:
                    if current_situation[row - i][col] == 0 or current_situation[row - i][col] == -1:  # 如果另一侧是空的，那也不能下
                        avalible_row_d = []
                    break  # 另一侧是自己的子，可以下
        avalible_row = avalible_row_u + avalible_row_d
        if len(avalible_row) > 0:
            return [[row, col], avalible_row]
        else:
            return []

    def search_col(self, row, col, current_player):  # 横向搜索
        avalible_col_u = []
        avalible_col_d = []
        avalible_col = []
        opponent = (1 - current_player) + 1  # 对手在棋盘上的棋子的序号
        # print("current_player:", current_player)
        # print("opponent:", opponent)
        current_situation = self.chessboard
        if current_situation[row][col] == 0:
            for i in range(col + 1, self.mode_num+2):
                if current_situation[row][i] == opponent:
                    avalible_col_u.append([row, i])
                else:
                    if current_situation[row][i] == 0 or current_situation[row][i] == -1:
                        avalible_col_u = []
                    break
            for i in range(1, col+1):
                if current_situation[row][col - i] == opponent:
                    avalible_col_d.append([row, col - i])
                else:
                    if current_situation[row][col - i] == 0 or current_situation[row][col - i] == -1:
                        avalible_col_d = []
                    break
        avalible_col = avalible_col_u + avalible_col_d
        if len(avalible_col) > 0:
            return [[row, col], avalible_col]
        else:
            return []

    def search_diagonal(self, row, col, current_player):  # 正对角线搜索
        avalible_dig_u = []
        avalible_dig_d = []
        avalible_dig = []
        opponent = (1 - current_player) + 1  # 对手在棋盘上的棋子的序号
        current_situation = self.chessboard
        if current_situation[row][col] == 0:
            for i in range(1, self.mode_num):
                if current_situation[row - i][col + i] == opponent:
                    avalible_dig_u.append([row - i, col + i])
                elif current_situation[row - i][col + i] == -1:  # 超出下棋范围
                    avalible_dig_u = []
                    break
                else:
                    if current_situation[row - i][col + i] == 0:
                        avalible_dig_u = []
                    break
            for i in range(1, self.mode_num):
                if current_situation[row + i][col - i] == opponent:
                    avalible_dig_d.append([row + i, col - i])
                elif current_situation[row + i][col - i] == -1:  # 超出下棋范围
                    avalible_dig_d = []
                    break
                else:
                    if current_situation[row + i][col - i] == 0:
                        avalible_dig_d = []
                    break
        avalible_dig = avalible_dig_u + avalible_dig_d
        if len(avalible_dig) > 0:
            return [[row, col], avalible_dig]
        else:
            return []

    def search_fdiagonal(self, row, col, current_player):  # 副对角线搜索
        avalible_fdig = []
        avalible_fdig_u = []
        avalible_fdig_d = []
        opponent = (1 - current_player) + 1  # 对手在棋盘上的棋子的序号
        current_situation = self.chessboard
        if current_situation[row][col] == 0:
            if current_situation[row][col] == 0:
                for i in range(1, self.mode_num):
                    if current_situation[row - i][col - i] == opponent:
                        avalible_fdig_u.append([row - i, col - i])
                    elif current_situation[row - i][col - i] == -1:  # 超出下棋范围
                        avalible_fdig_u = []
                        break
                    else:
                        if current_situation[row - i][col - i] == 0:
                            avalible_fdig_u = []
                        break
                for i in range(1, self.mode_num):
                    if current_situation[row + i][col + i] == opponent:
                        avalible_fdig_d.append([row + i, col + i])
                    elif current_situation[row + i][col + i] == -1:  # 超出下棋范围
                        avalible_fdig_d = []
                        break
                    else:
                        if current_situation[row + i][col + i] == 0:
                            avalible_fdig_d = []
                        break
        avalible_fdig = avalible_fdig_u + avalible_fdig_d
        if len(avalible_fdig) > 0:
            return [[row, col], avalible_fdig]
        else:
            return []

    def reload(self):
        for m in range(1, self.mode_num + 1):
            for n in range(1, self.mode_num + 1):
                self.chessboard[m][n] = 0
                self.last_3_chessboard[m][n] = 0
                self.last_2_chessboard[m][n] = 0
                self.last_1_chessboard[m][n] = 0
        self.init()
        return

    def format_avalible_drop(self, drop_list):
        print("drop_list:", drop_list)
        drop_points = []
        change_points = []
        for i in range(len(drop_list)):
            if drop_list[i][0] in drop_points:
                change_points[len(change_points) - 1].append(drop_list[i][1][0])
            else:
                drop_points.append(drop_list[i][0])
                change_points.append(drop_list[i][1])
        return drop_points, change_points

    def check_win(self):
        self.get_avalible_drop()
        if 0 == len(self.drop_points):
            opponet = 1-self.backend.present
            op_drops, op_change = self.search_avalible_drop(opponet)
            if 0 == len(op_drops):
                count_b, count_w = 0, 0
                for i in range(1, self.mode_num+1):
                    for j in range(1, self.mode_num+1):
                        if self.chessboard[i][j] == 1:
                            count_b += 1
                        elif self.chessboard[i][j] == 2:
                            count_w += 1
                if count_b > count_w:
                    return 1, 1
                elif count_w > count_b:
                    return 1, 2
                else:
                    return 1, 3  # 平局
        return 0, 1