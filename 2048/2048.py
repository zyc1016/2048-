import pyglet
import random
import copy
from pyglet.window import key

Win_width = 530
Win_height = 720
#棋盘起始位置左下角的x,y
start_x = 15
start_y = 110
#每行的块数
window_block_num = 4
#总宽度和每块的高度
board_width = (Win_width -2 * start_x)
block_windth = board_width/window_block_num
colors = {
    0:(204,192,179),2:(238,228,218),4:(237,224,200),8:(242,177,121),
    16:(245,149,99),32:(246,124,95),64:(246,94,59),128:(237,207,114),
    256:(233,170,7),512:(215,159,14),1024:(222,186,30),2048:(222,212,30),
    4096:(205,222,30),8192:(179,222,30),16384:(153,222,30),32768:(106,222,30),
    65536:(69,222,30),131072:(237,207,114),262144:(237,207,114),
    524288:(237,207,114)
}
label_color = (119,110,101,255)
bg_color = (250,248,239,255)
line_color = (165,165,165,225)

class Window(pyglet.window.Window):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.game_init()

    def game_init(self):
        self.main_batch = pyglet.graphics.Batch()

        self.data = [[0 for i in range(window_block_num)] for j in range(window_block_num)]
        #随机两个位置填充2或者4
        count=0
        while count<2:
            row = random.randint(0,window_block_num-1)
            col = random.randint(0,window_block_num-1)
            if self.data[row][col]!=0:
                count+=1
                continue
            self.data[row][col]=2 if random.randint(0,1) else 4
            count +=1
        #增加悔棋功能
        self.buffer = [copy.deepcopy(self.data)]
        self.max_buf_len = 10
        #背景spirite
        background_img = pyglet.image.SolidColorImagePattern(color=bg_color)
        self.background = pyglet.sprite.Sprite(
            background_img.create_image(Win_width,Win_height),0,0)

        #Title bold字体加粗  font_size字体大小
        self.title_label = pyglet.text.Label(text = '2048',bold = True,
            color = label_color,x=start_x,y=board_width+start_y+30,
            font_size =36,batch=self.main_batch)
        #Score
        self.score =0
        self.score_label = pyglet.text.Label(text = "score = %d "%(self.score),bold=True,
             color = label_color,x=200,y=board_width+start_y+30,
            font_size=36,batch=self.main_batch)

        #help
        self.help_label = pyglet.text.Label(text = "please use up ,down,->,<- to play !",
             bold=True,color=label_color,x=start_x,y=start_y-30,
            font_size=18,batch=self.main_batch)
        #悔棋
        self.undo_label = pyglet.text.Label(text = "press u to undo,you can undo %d times "%(len(self.buffer)),bold=True,
             color = (119,110,101,255),x=start_x,y=60,
            font_size=16,batch=self.main_batch)
        self.restart_label = pyglet.text.Label(text = "press R to restart,ESC to quit",bold=True,
                                               color=(119, 110, 101, 255), x=start_x, y=35,
                                               font_size=16, batch=self.main_batch)

    def on_draw(self):
        self.clear()
        self.score_label.text = "score = %d" %(self.score)
     #   self.score_label.text = "press u to undo,you can undo %d times "%(len(self.buffer))
        self.background.draw()
        self.main_batch.draw()
        #画方格
        for row  in range(window_block_num):
            for col in range(window_block_num):
                x = start_x+block_windth*col
                y = start_y+board_width - block_windth -block_windth*row
                self.draw_tile((x,y,block_windth,block_windth),self.data[row][col])
        self.main_batch.draw()
        self.draw_grid(start_x,start_y)

    def draw_grid(self,startx,starty):
        #线的数量
        rows = columns = window_block_num+1
        #水平线
        for i in range(rows):
            pyglet.graphics.draw(
                2,pyglet.gl.GL_LINES,
                ('v2f',(
                         startx,i*block_windth+starty,
                         window_block_num*block_windth+startx,i*block_windth+starty
                       )
                ),
                ('c4B',line_color*2)
            )
        #垂直线
        for j in range(columns):
            pyglet.graphics.draw(
                2,pyglet.gl.GL_LINES,
                ('v2f',(
                    j * block_windth + startx, starty,
                    j * block_windth + startx, window_block_num*block_windth+starty,
                        )
                ),('c4B',line_color*2)
            )
    #填入方格数字
    def draw_tile(self,xywh,data):
        x,y,dx,dy = xywh
        color_rgb = colors[data]
        corners = [x+dx,y+dy,x,y+dy,x,y,x+dx,y]
        pyglet.graphics.draw(
            4,pyglet.gl.GL_QUADS,('v2f',corners),('c3B',color_rgb*4)
        )
        if data !=0:
            a=pyglet.text.Label(text=str(data), bold=True,anchor_x='center',
                                anchor_y='center', color=(0,0,0,255), x=x+dx/2, y=y+dy/2,
                                font_size=28)
            a.draw()
    def on_key_press(self,symbol,modifiers):
        eq_tile = False
        key_press = False
        score = 0
        if symbol ==key.UP:
            self.data,eq_tile,score = self.slideUpDown(True)
            key_press = True
        elif symbol ==key.DOWN:
            self.data,eq_tile,score = self.slideUpDown(False)
            key_press = True
        elif symbol == key.LEFT:
            self.data,eq_tile,score = self.slideLeftRight(True)
            key_press = True
        elif symbol == key.RIGHT:
            self.data,eq_tile,score = self.slideLeftRight(False)
            key_press = True
        elif symbol == key.ESCAPE:
            self.close()
        #悔棋
        elif symbol == key.U:
            if len(self.buffer)>0:
                self.data = self.buffer[-1]
                del self.buffer[-1]
        #重新开始游戏
        elif symbol == key.R:
            self.game_init()
        self.score += score
        if key_press and (not self.put_tile()):
            __,a,__ = self.slideUpDown(True)
            __,b,__ = self.slideUpDown(False)
            __,c,__ = self.slideLeftRight(True)
            __,d,__ = self.slideLeftRight(False)
            if a and b and c and d:
                print("Game over")
                a = pyglet.text.Label(text = "You lose,\nPlease try again!",bold=True,
                                  anchor_x='center',anchor_y='center',color =(255,255,205,255),
                                  x=Win_width/2,y=Win_height/2,width =500 ,font_size=38,batch =self.main_batch)
        if key_press and (not eq_tile):
            if len(self.buffer) == self.max_buf_len:
                del self.buffer[0]
            self.buffer.append(copy.deepcopy(self.data))
    def merge(self,vlist,direct):
        score = 0
        if direct:
            i = 1
            while i < len(vlist):
                if vlist[i-1] == vlist[i]:
                    """当两个块值相等时，则删除一个，并让另一个值*2"""
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                i += 1
        else:
            i=len(vlist)-1
            while i > 0:
                if vlist[i-1] == vlist[i]:
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                i -= 1
        return score

    def slideUpDown(self, up):
        olddata = copy.deepcopy(self.data)
        score = 0
        for col in range(window_block_num):
            #抽取一维非零向量
            cv1 = [olddata[row][col] for row in range(window_block_num) if olddata[row][col] != 0]
            #合并
            if len(cv1) >= 2:
                score += self.merge(cv1,up)
            #补零
            for i in range(window_block_num-len(cv1)):
                if up:cv1.append(0)
                else : cv1.insert(0,0)
            #回填
            for row in range(window_block_num):
                olddata[row][col] = cv1[row]
        return olddata, olddata == self.data, score

    def slideLeftRight(self, left):
        olddata = copy.deepcopy(self.data)
        score = 0
        for row in range(window_block_num):
            #抽取一维非零向量
            rv1 = [olddata[row][col] for col in range(window_block_num) if olddata[row][col]!=0]
            #合并
            if len(rv1) >= 2:
                score += self.merge(rv1, left)
            #补零
            for i in range(window_block_num-len(rv1)):
                if left : rv1.append(0)
                else : rv1.insert(0, 0)
            #回填
            for col in range(window_block_num):
                olddata[row][col] = rv1[col]
        return olddata,olddata == self.data, score

    def put_tile(self):
        available = []
        for row in range(window_block_num):
            for col in range(window_block_num):
                if self.data[row][col] == 0:
                    available.append((row,col))
        if available:
            row,col = available[random.randint(0, len(available)-1)]
            self.data[row][col] = 2 if random.randint(0, 1) else 4
            return True
        else:
            return False


#创建窗口
win = Window(Win_width,Win_height)
#设置图标
icon = pyglet.image.load('icon.ico')
win.set_icon(icon)
pyglet.app.run()
