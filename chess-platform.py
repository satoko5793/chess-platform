import UserSystem
from Window import *
from boards import *
from heibai_board import *
import Momento
import time
from UserSystem import *

class Chess:
    def __init__(self, client, chessboard_size=9, chess_type=0):
        # 客户端
        self.client = client
        # 种类：围棋：0，五子棋：1. 黑白棋：2
        self.chess_type = chess_type
        # 模式，九路棋：9，十三路棋：13，十九路棋：19
        self.mode_num = chessboard_size
        self.window_size = 1.8
        self.dd = 360 * self.window_size / (self.mode_num - 1)  # 棋盘每格的边长
        # 当前轮到的玩家，黑：0，白：1，执黑先行
        self.present = 0
        # 棋盘的相对矫正比例
        self.p = 1 if self.mode_num == 9 else (2 / 3 if self.mode_num == 13 else 4 / 9)
        self.window = Window(self, self.window_size, self.dd, self.p, chessboard_size)
        if self.chess_type == 1:
            self.window.passmeButton['state'] = DISABLED  # 五子棋没有弃子
            self.window.ai2Button['state'] = NORMAL  #  五子棋有ai
            self.window.ai1Button['state'] = NORMAL
        if self.chess_type == 0:
            self.board = weiqi_board(self, self.window_size, self.dd, self.p, chessboard_size)
        elif self.chess_type == 1:
            self.board = wuziqi_board(self, self.window_size, self.dd, self.p, chessboard_size)
        else:
            self.board = heibai_board(self, self.window_size, self.dd, self.p, chessboard_size)
            self.board.init()
        # 初始停止，点击“开始游戏”运行游戏
        self.stop = True
        # 悔棋次数，次数大于0才可悔棋，初始置0（初始不能悔棋），悔棋后置0，下棋或弃手时恢复为1，以禁止连续悔棋
        self.regretchance = 0
        # 录像回放功能相关类
        self.lookback = Momento.LookBack()
        # 用户系统
        self.usersystem = UserSystem()
        self.curentUsers = [User('游客1', 0, 'user'), User('游客2', 0, 'user')]

    # 开始游戏函数
    def start(self):
        # 图标处理
        self.window.start(self.present)
        self.window.update_user_label()
        self.window.update_user_record()
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
        if self.chess_type == 2:  # 黑白棋更新可下位置，要在玩家交换后更新
            self.board.get_avalible_drop()

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
            if self.chess_type == 2:  # 黑白棋更新可下位置，要在玩家交换后更新
                self.board.get_avalible_drop()
            self.lookback.delete_move(2)  # 删除2步记录

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
                            # 添加记录
                            self.lookback.add_move(self.present, x, y)
                            # 轮到下一玩家
                            self.change_player()
                        elif result == "无气":
                            self.window.canvas_bottom.delete('position' + str(x) + str(y))
                            self.window.bell()
                            self.window.showwarningbox('无气', "你被包围了！")
                        elif result == "打劫":
                            self.window.canvas_bottom.delete('position' + str(x) + str(y))
                            self.window.bell()
                            self.window.showwarningbox("打劫", "此路不通！")
                    else:  # 五子棋黑白棋落子
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
                        # 添加记录
                        self.lookback.add_move(self.present, x, y)
                        win, winner = self.board.check_win()
                        if win:
                            self.stop = True
                            if win == 1:
                                message = ("黑子" if winner == 1 else "白子") + "胜利！"
                                if winner == 1:
                                    self.curentUsers[0].win += 1
                                    self.curentUsers[1].loss += 1  # 修改这里就会修改usersystem里的users
                                else:
                                    self.curentUsers[1].win += 1
                                    self.curentUsers[0].loss += 1
                                self.window.update_user_record()
                                self.usersystem.save()
                            else:
                                message = "平局，无子可下"
                            self.window.showwarningbox("游戏结束", message)
                            return
                        # 轮到下一玩家
                        self.change_player()
                        if self.chess_type == 2:  # 黑白棋更新可下位置，要在玩家交换后更新
                            self.board.get_avalible_drop()
                else:
                    # 覆盖，声音警告
                    self.window.bell()
            else:
                # 超出边界，声音警告
                self.window.bell()


    def change_player(self):
        self.window.player_change(self.present)
        self.present = 1 - self.present
        self.window.update_user_label()
        if self.curentUsers[self.present].role != 'user':
            self.window.update()
            time.sleep(0.5)
            if self.curentUsers[self.present].role == 'ai1':
                self.board.ai_move1()
            elif self.curentUsers[self.present].role == 'ai2':
                self.board.ai_move2()
            # 落下棋子有效
            if not self.regretchance == 1:
                self.regretchance += 1
            else:
                self.window.regretButton['state'] = NORMAL
            win, winner = self.board.check_win()
            if win:
                self.stop = True
                if win == 1:
                    message = ("黑子" if winner == 1 else "白子") + "胜利！"
                    if winner == 1:
                        self.curentUsers[0].win += 1
                        self.curentUsers[1].loss += 1
                        self.usersystem.addwin(self.curentUsers[0].username)
                        self.usersystem.addloss(self.curentUsers[1].username)
                    else:
                        self.curentUsers[1].win += 1
                        self.curentUsers[0].loss += 1
                        self.usersystem.addwin(self.curentUsers[1].username)
                        self.usersystem.addloss(self.curentUsers[0].username)
                    self.window.update_user_record()
                    self.usersystem.save()
                else:
                    message = "平局，无子可下"
                self.window.showwarningbox("游戏结束", message)
                return
            self.change_player()


    def getDowninBoard(self, player, row, col):
        self.present = player
        if self.chess_type == 2:
            self.board.get_avalible_drop()
        self.board.getDown(row, col)
        self.updateboard([[col, row]])

    def lookBack(self):
        self.window.reload()
        self.board.reload()
        self.stop = 1
        print(self.lookback.moves)
        for player, row, col in self.lookback.moves:
            self.getDowninBoard(player, row, col)
            self.window.update()
            # 等待1秒
            time.sleep(1)

    def add_ai1(self):  # 添加1级ai
        self.curentUsers[self.present] = User("一级AI", 0, 'ai1')
        self.window.update_user_label()

    def add_ai2(self):  # 添加2级ai
        self.curentUsers[self.present] = User("二级AI", 0, 'ai2')
        self.window.update_user_label()

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

    # 只删图片,给黑白棋用的
    def delete_image(self, killList):
        if len(killList) > 0:
            for i in range(len(killList)):
                self.window.canvas_bottom.delete('position' + str(killList[i][1]) + str(killList[i][0]))
    # 认输
    def giveup(self):
        self.stop = True
        message = ("黑子" if self.present == 0 else "白子") + "认输," + ("白子" if self.present == 0 else "黑子") + "胜利！"
        self.window.showwarningbox("游戏结束", message)

    # 键盘快捷键退出游戏
    def keyboardQuit(self, event):
        self.window.quit()

    # 以下函数修改Client变量值，newApp使主函数循环，以建立不同参数的对象
    def newGame1(self):
        self.client.mode_num = (13 if self.mode_num == 9 else 9)
        self.client.newApp = True
        self.window.quit()

    def newGame2(self):
        self.client.mode_num = (13 if self.mode_num == 19 else 19)
        self.client.newApp = True
        self.window.quit()

    def newGame3(self):
        self.client.chess_type = (self.client.chess_type+1)%3
        self.client.newApp = True
        self.window.quit()

    def save(self, filepath):
        Momento.save(filepath, self.board.chessboard)

    def load(self, filepath):
        new_board = Momento.load(filepath)
        if len(new_board) != self.mode_num+2:
            self.window.showwarningbox("警告", "存档不符合，无法读取")
            return
        self.reload()
        self.board.chessboard = Momento.load(filepath)
        self.updateboard()
        if self.chess_type == 2:  # 黑白棋更新可下位置，要在玩家交换后更新
            self.board.get_avalible_drop()

    def updateboard(self, addList=None):
        if addList == None:
            for i in range(1, self.mode_num+1):
                for j in range(1, self.mode_num+1):
                    if self.board.chessboard[i][j] != 0:
                        self.window.add_image(
                            21.5 * self.window_size + (j-1) * self.dd,
                            19 * self.window_size + (i-1) * self.dd,
                            j, i,
                            self.board.chessboard[i][j]-1
                        )
        else:
            for i, j in addList:
                if self.board.chessboard[i][j] != 0:
                    self.window.add_image(
                        21.5 * self.window_size + (j - 1) * self.dd,
                        19 * self.window_size + (i - 1) * self.dd,
                        j, i,
                        self.board.chessboard[i][j] - 1
                    )

    def register(self, username, password):
        self.usersystem.add_user(username, password, 'user')
        self.usersystem.save()

    def login(self, username, password):
        result = self.usersystem.login(username, password)
        if result:
            self.curentUsers[self.present] = self.usersystem.users[username]
            self.window.update_user_label()
            self.window.update_user_record()
        else:
            print("用户名或密码不正确，登录失败")
        return result

class Client:
    def __init__(self):
        # 用于新建Application对象时切换成不同模式的游戏
        self.mode_num = 9
        self.newApp = False
        self.chess_type = 0  # 0表示围棋，1表示五子棋. 2表示黑白棋

    def run(self):
        while True:
            self.newApp = False
            app = Chess(self, self.mode_num, self.chess_type)
            if self.chess_type == 0:
                title = '围棋'
            elif self.chess_type == 1:
                title = '五子棋'
            else:
                title = '黑白棋'
            app.window.title(title)
            app.window.mainloop()
            if self.newApp:
                app.window.destroy()
            else:
                break


if __name__ == '__main__':
    c = Client()
    c.run()
