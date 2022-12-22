# 导入GUI模块
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
import tkinter.filedialog

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
        #用户名字
        self.userlabel = Label(self, text="")
        self.userlabel.place(x=500 * self.window_size-25, y=120 * self.window_size)
        #用户战绩
        self.userRecord = Label(self, text="")
        self.userRecord.place(x=500 * self.window_size - 25, y=140 * self.window_size)
        # 2级ai
        self.ai2Button = Button(self, text='设为二级ai', command=self.backend.add_ai2)
        self.ai2Button.place(x=500 * self.window_size, y=350 * self.window_size)
        self.ai2Button['state'] = DISABLED
        # 1级ai
        self.ai1Button = Button(self, text='设为一级ai', command=self.backend.add_ai1)
        self.ai1Button.place(x=500 * self.window_size, y=325 * self.window_size)
        self.ai1Button['state'] = DISABLED
        # 注册
        self.registerButton = Button(self, text='用户注册', command=self.register)
        self.registerButton.place(x=500 * self.window_size, y=300 * self.window_size)
        # 登录
        self.loginButton = Button(self, text='用户登录', command=self.login)
        self.loginButton.place(x=500 * self.window_size, y=275 * self.window_size)
        # 回放
        self.lookbackButton = Button(self, text='回放棋局', command=self.backend.lookBack)
        self.lookbackButton.place(x=500 * self.window_size, y=250 * self.window_size)
        # 认输
        self.giveupButton = Button(self, text='投子认负', command=self.backend.giveup)
        self.giveupButton.place(x=500 * self.window_size, y=225 * self.window_size)
        # 保存读取游戏
        self.saveButton = Button(self, text='保存棋局', command=self.save)
        self.saveButton.place(x=500 * self.window_size, y=175 * self.window_size)
        self.loadButton = Button(self, text='读取棋局', command=self.load)
        self.loadButton.place(x=500 * self.window_size, y=200 * self.window_size)
        # 切换游戏类型按钮
        if self.backend.chess_type == 0:
            next_game = '五子棋'
        elif self.backend.chess_type == 1:
            next_game = '黑白棋'
        else:
            next_game = '围棋'
        self.changeButton = Button(self, text=(next_game), command=self.backend.newGame3)
        self.changeButton.place(x=440 * self.window_size, y=175 * self.window_size)
        # 几个功能按钮
        self.startButton = Button(self, text='开始游戏', command=self.backend.start)
        self.startButton.place(x=440 * self.window_size, y=200 * self.window_size)
        self.passmeButton = Button(self, text='弃一手', command=self.backend.passme)
        self.passmeButton.place(x=440 * self.window_size, y=225 * self.window_size)
        self.regretButton = Button(self, text='悔棋', command=self.backend.regret)
        self.regretButton.place(x=440 * self.window_size, y=250 * self.window_size)
        # 初始悔棋按钮禁用
        self.regretButton['state'] = DISABLED
        self.replayButton = Button(self, text='重新开始', command=self.backend.reload)
        self.replayButton.place(x=440 * self.window_size, y=275 * self.window_size)
        self.newGameButton1 = Button(self, text=('十三' if self.mode_num == 9 else '九') + '路棋', command=self.backend.newGame1)
        self.newGameButton1.place(x=440 * self.window_size, y=300 * self.window_size)
        self.newGameButton2 = Button(self, text=('十三' if self.mode_num == 19 else '十九') + '路棋', command=self.backend.newGame2)
        self.newGameButton2.place(x=440 * self.window_size, y=325 * self.window_size)
        self.quitButton = Button(self, text='退出游戏', command=self.quit)
        self.quitButton.place(x=440 * self.window_size, y=350 * self.window_size)
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

    # 创建登录按钮并绑定回调函数
    def login(self):
        login_window = Toplevel()
        login_window.title("登录窗口")

        Label(login_window, text="用户名:").grid(row=0)
        username_entry = Entry(login_window)
        username_entry.grid(row=0, column=1)

        Label(login_window, text="密码:").grid(row=1)
        password_entry = Entry(login_window, show="*")
        password_entry.grid(row=1, column=1)

        def do_login():
            # 获取用户名和密码
            username = username_entry.get()
            password = password_entry.get()
            # 在这里进行登录操作
            self.backend.login(username, password)
            login_window.destroy()
            self.userlabel.configure(text=self.backend.curentUsers[self.backend.present].username)

        login_button = Button(login_window, text="登录", command=do_login)
        login_button.grid(row=2)

    # 创建登录按钮并绑定回调函数
    def register(self):
        register_window = Toplevel()
        register_window.title("注册窗口")

        Label(register_window, text="用户名:").grid(row=0)
        username_entry = Entry(register_window)
        username_entry.grid(row=0, column=1)

        Label(register_window, text="密码:").grid(row=1)
        password_entry = Entry(register_window)
        password_entry.grid(row=1, column=1)

        def do_register():
            # 获取用户名和密码
            username = username_entry.get()
            password = password_entry.get()
            # 在这里进行登录操作
            self.backend.register(username, password)
            register_window.destroy()

        register_button = Button(register_window, text="注册", command=do_register)
        register_button.grid(row=2)

    def save(self):
        wordFile = tkinter.filedialog.askdirectory(title='选择存放的位置！', initialdir=r'./test')
        print("保存到"+wordFile)
        self.backend.save(wordFile)

    def load(self):
        file_path = tkinter.filedialog.askopenfilename(title='请选择一个文件', initialdir=r'./test')
        print("读取"+file_path)
        self.backend.load(file_path)

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

    def update_user_label(self):
        self.userlabel.configure(text=self.backend.curentUsers[self.backend.present].username)

    def update_user_record(self):
        user1 = self.backend.curentUsers[0]
        user2 = self.backend.curentUsers[1]
        message = user1.username + " 胜利" + str(user1.win) + "次，失败" + str(user1.loss) + "次\n"\
                  + user2.username + " 胜利" + str(user2.win) + "次，失败" + str(user2.loss) + "次"
        self.userRecord.configure(text=message)

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
        # self.canvas_bottom.delete(self.cross)
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