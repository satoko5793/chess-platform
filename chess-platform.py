from Window import *
from boards import *
import Momento

class Chess:
    def __init__(self, client, chessboard_size=9, chess_type=0):
        # 客户端
        self.client = client
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

    # 认输
    def giveup(self):
        self.stop = True
        message = ("黑子" if self.present == 0 else "白子") + "认输," + ("白子" if self.present == 0 else "黑子") + "胜利！"
        self.window.showwarningbox("游戏结束", message)

    # 键盘快捷键退出游戏
    def keyboardQuit(self, event):
        self.window.quit()

    # 以下两个函数修改全局变量值，newApp使主函数循环，以建立不同参数的对象
    def newGame1(self):
        self.client.mode_num = (13 if self.mode_num == 9 else 9)
        self.client.newApp = True
        self.window.quit()

    def newGame2(self):
        self.client.mode_num = (13 if self.mode_num == 19 else 19)
        self.client.newApp = True
        self.window.quit()

    def newGame3(self):
        self.client.chess_type = 1 - self.client.chess_type
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
        for i in range(1, self.mode_num+1):
            for j in range(1, self.mode_num+1):
                if self.board.chessboard[i][j] != 0:
                    self.window.add_image(
                        21.5 * self.window_size + (j-1) * self.dd,
                        19 * self.window_size + (i-1) * self.dd,
                        j, i,
                        self.board.chessboard[i][j]-1
                    )


class Client:
    def __init__(self):
        # 用于新建Application对象时切换成不同模式的游戏
        self.mode_num = 9
        self.newApp = False
        self.chess_type = 0  # 0表示围棋，1表示五子棋

    def run(self):
        while True:
            self.newApp = False
            app = Chess(self, self.mode_num, self.chess_type)
            app.window.title('围棋' if self.chess_type == 0 else '五子棋')
            app.window.mainloop()
            if self.newApp:
                app.window.destroy()
            else:
                break


if __name__ == '__main__':
    c = Client()
    c.run()
