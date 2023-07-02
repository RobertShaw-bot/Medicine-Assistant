import contextlib
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivymd.app import MDApp
from functions import callbacklogin, callbackregister
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.uix.camera import Camera
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock, mainthread
from kivymd.uix.pickers import MDTimePicker
from kivy.uix.label import Label
from PIL import Image
from datetime import datetime
import pyttsx3
import time
import os
from kivy.metrics import dp
from kivy.app import App
import functions
import pymysql
from kivymd.uix.datatables import MDDataTable
Window.size = (600, 800)
ip= "db4free.net"
use="mediciner"
passd="wbx20030206@"
data="project_medicine"
# ip= "192.168.2.111"
# use="app_data"
# passd="Wbx20030206@"
# data="name"

global screen
global file_path
global IDnum1
reminderflag=False
reminderflagdouble=False
screen = ScreenManager()

class SplashScreen(Screen):
    pass

class RegisterScreen(Screen):  
  
  def callbackregister(self, *args):
    callbackregister(self,*args)

  def registro(self, nome, cpf, senha):
    from functions import create_post
    create_post(self, nome, cpf, senha)  

class LoginScreen(Screen):
  def callbacklogin(self, *args):
    callbacklogin(self,*args)
    
  def loga(self, cpf, senha):
    from functions import get_post
    get_post(self, cpf, senha)
    
class DashboardScreen(Screen):
    pass

class PopupLay(MDFloatLayout):
    def jump_to_reminder(self):
        global reminderflagdouble
        reminderflagdouble=True
        MDApp.get_running_app().root.current = 'reminderscreen'

class SearchMedicineScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.search_list=[]
    def search_in_database(self,medicine_name):
        functions.search_in_database(self,medicine_name)
    def on_row_press(self, instance_table, instance_row):
        # 获取点击行的列索引
        column_index = instance_row.index
        if column_index%6 == 1:  # 批准文号列的索引为1
            # 执行批准文号列的点击处理逻辑
            self.number=instance_row.text[29:42]
            show=PopupLay()
            popupWindow=Popup(title='  ',content=show,size_hint=(0.8,0.3))
            popupWindow.open()
    def SearchHistyoryScreen_on_pre_enter(self):
        functions.SearchHistyoryScreen_on_pre_enter(self)
    def on_leave(self, *args): # 类似于屏幕的析构函数
        self.ids.search_result.clear_widgets()

class CaptureScreen(Screen):
    def take_photo_and_screenshot(self):
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png(f"IMG_{timestr}")
        file_name = f"IMG_{timestr}.png"
        folder_path = "KivyApp/kivyCamera" # 指定文件夹路径
        file_path = os.path.join(folder_path, file_name)
        camera.export_to_png(file_path)
        self.manager.get_screen('cropscreen').image_path = file_path
        self.manager.current = 'cropscreen'
          
class CropScreen(Screen):
    rect_box = ObjectProperty(None)
    t_x = NumericProperty(0.0)
    t_y = NumericProperty(0.0)
    x1 = y1 = x2 = y2 = 0.0
    cancel_flag=False
    ok_flag=False
    LDx= NumericProperty(0)
    LDy= NumericProperty(0)
    RTx= NumericProperty(0)
    RTy= NumericProperty(0)
    image_x=NumericProperty(0)
    image_y=NumericProperty(0)

    def __init__(self, **kwargs):
        super(CropScreen, self).__init__(**kwargs)
        self.image_path=' '

    def on_pre_enter(self, *args):
        self.ids.image.source = self.image_path
        self.image=Image.open(self.image_path)
        self.image_x, self.image_y = self.ids.image.pos
        self.image_width,self.image_height=self.ids.image.size
    
    def clear_touch_selector(self):
        self.ids.touch_selector.cancel_flag=True
        self.ids.touch_selector.first_tap=True
        self.ids.touch_selector.cancel_flag=False
        self.ids.touch_selector.resize_flag=True
        self.ids.touch_selector.size_selected[0]=0
        self.ids.touch_selector.size_selected[1]=0
        self.ids.touch_selector.remove_old_line()
        with contextlib.suppress(Exception):
                self.ids.touch_selector.list_lines_in_image.pop(0).points = []
        self.ids.touch_selector.canvas.clear()
        self.manager.current = 'capturescreen'

    def image_accepted_by_user(self):

        timestr = time.strftime("%Y%m%d_%H%M%S")
        file_name = f"IMG_{timestr}.png"
        folder_path = "KivyApp/kivyCamera"
        file_path = os.path.join(folder_path, file_name)

        if self.ids.touch_selector.list_lines_in_image==[]:
            self.manager.get_screen('resultscreen').image_finalpath=self.image_path
            self.leave_cropscreen()
        else:
            self.image_x, self.image_y = self.ids.image.pos
            self.LDx = self.ids.touch_selector.LDx-self.image_x
            self.LDy = self.ids.touch_selector.LDy-self.image_y
            self.LTy = self.ids.touch_selector.LTy-self.image_y
            self.RTx = self.ids.touch_selector.RTx-self.image_x
            self.RTy = self.ids.touch_selector.RTy-self.image_y
            self.RDy = self.ids.touch_selector.RDy-self.image_y
            self.image_width,self.image_height=self.ids.image.size
            # print("height",self.image_height)
            # print("width",self.image_width)
            upper=max(abs(self.image_height-self.LTy),abs(self.image_height-self.RDy))
            lower=min(abs(self.image_height-self.LTy),abs(self.image_height-self.RDy))
            # print("坐标是：",self.LDx,lower,self.RTx,upper)
            self.cropped_image=self.image.crop((self.LDx,lower,self.RTx,upper))
            # self.cropped_image=self.image.crop((self.LDx,self.LDy,self.RTx,self.RTy))
            
            self.cropped_image.save(file_path)
            self.manager.get_screen('resultscreen').image_finalpath=file_path
            self.ids.touch_selector.cancel_flag=True
            self.ids.touch_selector.first_tap=True
            self.ids.touch_selector.remove_old_line()
            self.leave_cropscreen()
    def leave_cropscreen(self):
        self.popup = Popup(title=' ', content=Label(text='开发人员努力识别中...',font_name='Chinesebold.ttf'), size_hint=(.4, .4))
        self.popup.open()
        # 模拟加载时间，加载完成后关闭Popup组件并切换到下一个屏幕
        Clock.schedule_once(self.load_data, 2)
    def load_data(self, dt):
        # 在这里加载数据
        self.popup.dismiss()
        self.manager.current = 'resultscreen'

class TouchSelector(Widget):
    id="TouchSelector"
    # Points of Line object
    Ax = NumericProperty(0)
    Ay = NumericProperty(0)
    Bx = NumericProperty(0)
    By = NumericProperty(0)
    Cx = NumericProperty(0)
    Cy = NumericProperty(0)
    Dx = NumericProperty(0)
    Dy = NumericProperty(0)
    LTx= NumericProperty(0)
    LTy= NumericProperty(0)
    LDx= NumericProperty(0)
    LDy= NumericProperty(0)
    RTx= NumericProperty(0)
    RTy= NumericProperty(0)
    RDx= NumericProperty(0)
    RDy= NumericProperty(0)
    width = NumericProperty(0)
    length = NumericProperty(0)
    touch_pos=" "
    cancel_flag=False
    resize_flag=False

    # Object line
    line = ObjectProperty()

    # List of line objects drawn
    list_lines_in_image = ListProperty([])

    # Size of the selected rectangle
    size_selected = ListProperty([0,0])

    # Size previous of the selected rectangle
    size_selected_previous = ListProperty([0,0])

    # Size temporary of the selected rectangle
    size_selected_temp = ListProperty([0,0])

    # Line Color and width
    line_color = ListProperty([1, 1, 1, 1])
    line_width = NumericProperty(3)

    # First tap in TouchSelector
    first_tap = True
    dragging=False
   
    
    def __init__(self, *args, **kwargs):
        super(TouchSelector, self).__init__(*args, **kwargs)
        self.bind(list_lines_in_image=self.remove_old_line)

    def on_touch_up(self, touch):
        self.size_selected = self.size_selected_temp
        if self.first_tap ==True: 
            self.width=abs(self.Cx - self.Dx)/2
            self.length=abs(self.Cy - self.By)/2
            self.tx=(self.Ax+self.Bx)/2
            self.ty=(self.Ay+self.Dy)/2
            self.LTx=self.tx-self.width
            self.LTy=self.ty+self.length
            self.RTx=self.tx+self.width
            self.RTy=self.ty+self.length
            self.RDx=self.tx+self.width
            self.RDy=self.ty-self.length
            self.LDx=self.tx-self.width
            self.LDy=self.ty-self.length 
            self.size_selected = abs(self.RDx - self.LDx), abs(self.RTy - self.RDy)
            self.first_tap=False
        if self.resize_flag==False:
            self.size_selected = abs(self.RDx - self.LDx), abs(self.RTy - self.RDy)
        else:
            self.resize_flag=False

    def on_touch_down(self, touch):  # sourcery skip: low-code-quality
        if self.size_selected[0] == 0 and self.size_selected[1] == 0:
            with self.canvas:
                self._extracted_from_on_touch_down_7(touch)
        else:
            touch.grab(self)
            if self.LTx < touch.x < self.RDx and self.RDy < touch.y < self.LTy:
                self.touch_pos="inside"
                self.dragging=True
            elif self.LTx==touch.x and self.LDy< touch.y <self.LTy:
                self.touch_pos="Left_border"
                self.dragging=True
            elif self.RTx-5<touch.x<self.RTx+5 and self.LDy< touch.y <self.LTy:
                self.touch_pos="right_border"
                self.dragging=True
            elif self.LTy-5<touch.y<self.LTy+5 and self.LTx< touch.x <self.RTx:
                self.touch_pos="up_border"
                self.dragging=True
            elif self.LDy-5<touch.y<self.LDy+5 and self.LTx< touch.x <self.RTx:
                self.touch_pos="down_border"
                self.dragging=True
            elif self.LTx-5<touch.x<self.LTx+5 and self.LTy-5<touch.y<self.LTy+5:
                self.touch_pos="Left_top"
            elif self.RTx-5<touch.x<self.RTx+5 and self.RTy-5<touch.y<self.RTy+5:
                self.touch_pos="Right_top"
                self.dragging=True
            elif self.RDx-5<touch.x<self.RDx and self.RDy-5<touch.y<self.RDy+5:
                self.touch_pos="Right_dowm"
                self.dragging=True
            elif self.LDx-5<touch.x<self.LDx+5 and self.LDy-5<touch.y<self.LDy+5:
                self.touch_pos="Left_down"
                self.dragging=True

    # TODO Rename this here and in `on_touch_down`
    def _extracted_from_on_touch_down_7(self, touch):
        Color(self.line_color)

        # Save initial tap position
        self.Ax, self.Ay = self.first_touch_x, self.first_touch_y = touch.x, touch.y

        # Initilize positions to save
        self.Bx, self.By = 0, 0
        self.Cx, self.Cy = 0, 0
        self.Dx, self.Dy = 0, 0

        # Create initial point with touch x and y postions.
        self.line = Line(points=([self.Ax, self.Ay]), width=self.line_width, joint='miter', joint_precision=30)

        # Save the created line
        self.list_lines_in_image.append(self.line)
       
    
   
    def remove_old_line(self, instance=None, list_lines=None):
        """Remove the old line draw"""
        if len(self.list_lines_in_image) > 0 and self.cancel_flag==True:
            self.cancel_flag=False
            self.resize_flag=True
            self.size_selected[0]=0
            self.size_selected[1]=0
            with contextlib.suppress(Exception):
                self.list_lines_in_image.pop(0).points = []
            self.canvas.clear()

    def delete_line(self, pos=0):
        with contextlib.suppress(Exception):
            self.list_lines_in_image.pop(pos).points = []

    def draw_rectangle(self):
        self.line.points = [self.LTx, self.LTy,
                            self.RTx, self.RTy,
                            self.RDx, self.RDy,
                            self.LDx, self.LDy,
                            self.LTx, self.LTy]

    def on_touch_move(self, touch):  # sourcery skip: low-code-quality
        if self.size_selected[0] == 0 and self.size_selected[1] == 0:
            # Assign the position of the touch at the point C
            self.Cx, self.Cy = touch.x, touch.y

            # There are two known points A (starting point) and C (endpoint)
            # Assign the  positions x and y  known of the points
            self.Bx, self.By = self.Cx, self.Ay
            self.Dx, self.Dy = self.Ax, self.Cy

            # Assign points positions to the last line created
            self.line.points = [self.Ax, self.Ay,
                                self.Bx, self.By,
                                self.Cx, self.Cy,
                                self.Dx, self.Dy,
                                self.Ax, self.Ay]


        elif self.dragging==True:
            dx, dy = touch.dx, touch.dy
            if self.touch_pos=="inside":
                self.LTx=self.LTx+dx
                self.LTy=self.LTy+dy
                self.RTx=self.RTx+dx
                self.RTy=self.RTy+dy
                self.RDx=self.RDx+dx
                self.RDy=self.RDy+dy
                self.LDx=self.LDx+dx
                self.LDy=self.LDy+dy
                self.draw_rectangle()
            elif self.touch_pos=="Left_border":
                self.LTx=self.LTx+dx
                self.LDx=self.LDx+dx
                self.draw_rectangle()
            elif self.touch_pos=="right_border":
                self.RTx=self.RTx+dx
                self.RDx=self.RDx+dx
                self.draw_rectangle()
            elif self.touch_pos=="down_border":
                self.RDy=self.RDy+dy
                self.LDy=self.LDy+dy
                self.draw_rectangle()
            elif self.touch_pos=="up_border":
                self.LTy=self.LTy+dy
                self.RTy=self.RTy+dy
                self.draw_rectangle()
            elif self.touch_pos=="Left_top":
                self.LTx=self.LTx+dx
                self.LTy=self.LTy+dy
                self.RTy=self.RTy+dy
                self.LDx=self.LDx+dx
                self.draw_rectangle()
            elif self.touch_pos=="Right_top":
                self.RTx=self.RTx+dx
                self.RTy=self.RTy+dy
                self.LTy=self.LTy+dy
                self.RDx=self.RDx+dx
                self.draw_rectangle()
            elif self.touch_pos=="Left_down":
                self.LDx=self.LDx+dx
                self.LDy=self.LDy+dy
                self.LTx=self.LTx+dx
                self.RDy=self.RDy+dy
                self.draw_rectangle()
            elif self.touch_pos=="Right_down":
                self.RDx=self.RDx+dx
                self.RDy=self.RDy+dy
                self.RTx=self.RTx+dx
                self.LDy=self.LDy+dy
                self.draw_rectangle()
    

class PopupLayout(MDFloatLayout):
    def jump_to_reminder(self):
        global reminderflag
        reminderflag=True
        MDApp.get_running_app().root.current = 'reminderscreen'
        
class ResultScreen(Screen):
    text_results=[]
    final_results=[]
    text1=''
    text2=''
    text3=''
    IDnum1=''
    IDnum2=''
    IDnum3=''
    image_path1=''
    image_path2=''
    image_path3=''
    
    def __init__(self, **kwargs):
        super(ResultScreen, self).__init__(**kwargs)
        self.image_finalpath=' '

    def ocr_img(self,image_finalpath):
        from functions import ocr_img
        return ocr_img(self,image_finalpath)
    
    def search_name(self,element:list):
        from functions import search_name
        return search_name(self,self.text_results)
    
    def search_in_database1(self,result:dict):
        from functions import search_in_database1
        return search_in_database1(self,result)

    def get_result(self):  # sourcery skip: remove-pass-body
        # a buffer screen should be displayed here, when the function was used,
        # a screen will be display among screen
        # it will disappear after recognize-function was complete
        self.text_results=self.ocr_img(self.image_finalpath)
        # print(self.image_finalpath)
        # print(self.text_results)
        # print(len(self.text_results))
        if self.text_results[0]=='':
            self.popup = Popup(title=' ', content=Label(text='请确保药盒对准摄像头',font_name='Chinesebold.ttf'), size_hint=(.4, .4))
            self.popup.open()
        # 模拟加载时间，加载完成后关闭Popup组件并切换到下一个屏幕
            time.sleep(2)
            tag=1
            self.manager.current="capturescreen"
        else:
            pipei_result=self.search_name(self.text_results)
            result=self.search_in_database1(pipei_result)
            # result=[('健胃消食片', '国药准字Z20083409'), ('健胃消食片', '国药准字Z20063599'), ('健胃消食片', '国药准字Z20054124')]
            if len(result)==0:
                self.popup = Popup(title=' ', content=Label(text='未查询到药品',font_name='Chinesebold.ttf'), size_hint=(.4, .4))
                self.popup.open()
        # 模拟加载时间，加载完成后关闭Popup组件并切换到下一个屏幕
                time.sleep(2)
                self.manager.current="capturescreen"
            else:
                self.ids.textone.text=result[0][0]
                self.ids.texttwo.text=result[1][0]
                self.ids.textthree.text=result[2][0]
                self.IDnum1=result[0][1]
                self.IDnum2=result[1][1]
                self.IDnum3=result[2][1]
                mydb=pymysql.connect(
                    host=ip,
                    user=use,
                    password=passd,
                    database=data
                )
                curson=mydb.cursor()
                curson.execute('SELECT * FROM 药品图片 WHERE 批准文号 =%s',(self.IDnum1,))
                result_image1 = [row[3] for row in curson.fetchall()]
                curson.execute('SELECT * FROM 药品图片 WHERE 批准文号 =%s',(self.IDnum2,))
                result_image2 = [row[3] for row in curson.fetchall()]
                curson.execute('SELECT * FROM 药品图片 WHERE 批准文号 =%s',(self.IDnum3,))
                result_image3 = [row[3] for row in curson.fetchall()]
                if result_image1==[None] and result_image2==[None] and result_image3==[None]:
                    self.popup = Popup(title=' ', content=Label(text='暂无该药品，请联系工作人员',font_name='Chinesebold.ttf'), size_hint=(.4, .4))
                    self.popup.open()
            # 模拟加载时间，加载完成后关闭Popup组件并切换到下一个屏幕
                    time.sleep(2)
                    self.manager.current="capturescreen"
                else:
                    if result_image1==[None]:
                        pass
                    else:
                        with open("KivyApp/resultimage/result1.jpg","wb")as tf:
                            tf.write(result_image1[0]) 
                        self.image_path1="KivyApp/resultimage/result1.jpg"
                        self.ids.imageone.source=self.image_path1
                        
                    if result_image2==[None]:
                        pass
                    else:
                        with open("KivyApp/resultimage/result2.jpg","wb")as tf:
                            tf.write(result_image2[0]) 
                        self.image_path2="KivyApp/resultimage/result2.jpg"
                        self.ids.imagetwo.source=self.image_path2

                    if result_image3==[None]:
                        pass
                    else:
                        with open("KivyApp/resultimage/result3.jpg","wb")as tf:
                            tf.write(result_image3[0]) 
                        self.image_path3="KivyApp/resultimage/result3.jpg"
                        self.ids.imagethree.source=self.image_path3
               
                   
    def on_pre_enter(self, *args):
        # print(self.image_finalpath)
        self.get_result()
      
    def show_up (self):
        show=PopupLayout()
        popupWindow=Popup(title='  ',content=show,size_hint=(0.8,0.3))
        popupWindow.open()
    # 这里定义一个函数将识别出的三个结果复制在三个卡片当中，
    # 定义popshow函数展示内容
    
class ReminderScreen(Screen):
    def __init__(self, **kwargs):
      super().__init__(**kwargs)
      # 创建药物列表
      self.table_rows = [] #存放添加提醒的列表
      self.time_list=[] #存放添加提醒的时间，均具有增删功能
      self.text=''
      self.index=1
    def on_pre_enter(self, *args):
        global reminderflag
        global reminderflagdouble
        if reminderflag==True:
            textnum=self.manager.get_screen("resultscreen").IDnum1[4:]
            self.ids.medicine_reminder.text=textnum
            reminderflag=False
        if reminderflagdouble==True:
            textnum=self.manager.get_screen("searchmedicine").number[4:]
            self.ids.medicine_reminder.text=textnum
            reminderflagdouble=False
    def get_text(self,text):
      functions.get_text(self,text)
    def set_reminder(self, instance):
      functions.set_reminder(self,instance)
    def create_timetable(self,hour:str,minute:str,medince_name:str):
      functions.create_timetable(self,hour,minute,medince_name)
    def get_time(self, instance, time):
      functions.get_time(self, instance, time)
    def make_table(self):
      functions.make_table(self)
    def delete_selected_rows(self):
      functions.delete_selected_rows(self)
    def get_new_time(self, instance, time):
        functions.get_new_time(self, instance, time)
    def on_row_press(self, instance_table, instance_row):
        # 获取点击行的列索引
        self.index = instance_row.index
        if self.index %4 == 1:  # 批准文号列的索引为1
            new_time=MDTimePicker()
            new_time.open()       
            new_time.bind(on_save=self.get_new_time)
            
class VideoScreendouble(Screen):
    reminderID=''
    def on_pre_enter(self, *args):
        self.reminderID=self.manager.get_screen("searchmedicine").number
        # print(self.reminderID)
        mydb = pymysql.connect(
            host=ip, # mySQL 数据库的主机名
            user="app_data", # mySQL 数据库的用户名
            password="Wbx20030206@", # mySQL 数据库的密码
            database="name" # mySQL 数据库的名称
        )

    # 创建一个游标对象
        cursor = mydb.cursor()

    # 执行 SQL 查询
        search_term = self.reminderID  # 搜索的关键词
        sql = "SELECT * FROM 药品说明 WHERE 批准文号 LIKE %s"  # 使用 LIKE 进行模糊搜索
        cursor.execute(sql, (f'%{search_term}%', ))
        # 获取查询结果
        results = cursor.fetchall()

        cursor.close()
        mydb.close()

        engine = pyttsx3.init()

        # 设置语音合成属性（可选）
        engine.setProperty('rate', 150)  # 设置语速，默认为 200
        engine.setProperty('volume', 0.8)  # 设置音量，默认为 1

        # 设置中文语音
        engine.setProperty('voice', 'zh')
        # 播放中文文本
        text = str(results)
        engine.say(text)
        engine.runAndWait()
        MDApp.get_running_app().root.current='searchmedicine'                
            
class VideoScreen(Screen):
    reminderID=''
    def on_pre_enter(self, *args):
        self.reminderID=self.manager.get_screen("resultscreen").IDnum1
        mydb = pymysql.connect(
            host=ip, # mySQL 数据库的主机名
            user="app_data", # mySQL 数据库的用户名
            password="Wbx20030206@", # mySQL 数据库的密码
            database="name" # mySQL 数据库的名称
        )

    # 创建一个游标对象
        cursor = mydb.cursor()

    # 执行 SQL 查询
        search_term = self.reminderID  # 搜索的关键词
        sql = "SELECT * FROM 药品说明 WHERE 批准文号 LIKE %s"  # 使用 LIKE 进行模糊搜索
        cursor.execute(sql, (f'%{search_term}%', ))
        # 获取查询结果
        results = cursor.fetchall()

        cursor.close()
        mydb.close()

        engine = pyttsx3.init()

        # 设置语音合成属性（可选）
        engine.setProperty('rate', 150)  # 设置语速，默认为 200
        engine.setProperty('volume', 0.8)  # 设置音量，默认为 1

        # 设置中文语音
        engine.setProperty('voice', 'zh')
        # 播放中文文本
        text = str(results)
        engine.say(text)
        engine.runAndWait()
        MDApp.get_running_app().root.current='resultscreen'

class CheckScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name_list = {}
    def on_pre_enter(self, *args):
        self.check_list=self.manager.get_screen('reminderscreen').table_rows
        from kivy.core.text import LabelBase
        LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")
        self.data_tables = MDDataTable(
            size_hint = (1.0, None),
            height= 680,
            pos_hint = {"center_x": 0.5, "center_y": 0.35},
            use_pagination = True,
            check=True,
            column_data=[
                ("[font=my_font]" + "序号" + "[/font]", dp(25)),
                ("[font=my_font]" + "提醒时间" + "[/font]", dp(30)),
                ("[font=my_font]" + "提醒次数" + "[/font]", dp(30)),
                ("[font=my_font]" + "药品名称" + "[/font]", dp(30)),
            ],
            row_data=self.check_list,
        ) 
        self.ids.show_check.clear_widgets()
        self.ids.show_check.add_widget(self.data_tables)
    def make_new_history(self):
        self.name_list_tuples = list(self.name_list.items())
        histtor_screen=self.manager.get_screen("checkhistoryscreen")
        histtor_screen.ids.check_history.clear_widgets()
        from kivy.core.text import LabelBase
        LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")
        # 创建新的 MDDataTable
        self.table = MDDataTable(
            size_hint=(1.0, .8),
            height=500,
            check=False,
            pos_hint={"center_x": 0.5, "center_y": 0.38},
            use_pagination=True,
            column_data=[
                ("[font=my_font]" + "药品名称" + "[/font]", dp(50)),
                ("[font=my_font]" + "打卡次数            最近打卡时间" + "[/font]", dp(70)),


            ],
            row_data=self.name_list_tuples
        )
        # 清除旧表格并添加新表格

        histtor_screen.ids.check_history.add_widget(self.table)
    def check_history(self):
        popup = Popup(title=' ',
                      content=Label(text='打卡成功！！！',
                                    font_size=20,
                                    font_name='Chinesebold.ttf'), 
                      size_hint=(.4, .4)
                      )
        popup.open()
        ids = self.data_tables.get_row_checks()
        for id in ids:
            if id[3] in self.name_list:
                self.name_list[id[3]] = f"      {str(int(self.name_list[id[3]][6]) + 1)}                             {str(datetime.now())[:16]}"
            else:
                self.name_list[id[3]] = f"      1                             {str(datetime.now())[:16]}"
        self.make_new_history()
    def on_leave(self):
        now_time=str(datetime.now())[11:16]
        if now_time == "00:00":
            self.name_list={}
            histtor_screen=self.manager.get_screen("checkhistoryscreen")
            histtor_screen.ids.check_history.clear_widgets()
            

      
class SetupScreen(Screen):
  pass

class SearchHistyoryScreen(Screen):
    def on_pre_enter(self):
        self.manager.get_screen('searchmedicine').SearchHistyoryScreen_on_pre_enter()
        self.get_history=self.manager.get_screen('searchmedicine').history
    def delete_history(self):
        ids = self.get_history.get_row_checks()

        for id in ids:
            temp = id[0][0]
            for i, row in enumerate(self.manager.get_screen('searchmedicine').search_list):
                if int(temp) == int(row[0]):
                    self.manager.get_screen('searchmedicine').search_list.pop(i)
                    break
        self.make_new_history()
    def make_new_history(self):
        self.new_table = [(i + 1, row[1], row[2])
                    for i, row in enumerate(self.manager.get_screen('searchmedicine').search_list)]
        self.manager.get_screen('searchmedicine').search_list=self.new_table
        #清除子组件
        self.ids.search_history.clear_widgets()
        from kivy.core.text import LabelBase
        LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")
        # 创建新的 MDDataTable
        self.table = MDDataTable(
            size_hint=(1.0, None),
            height=635,
            check=True,
            pos_hint={"center_x": 0.5},
            use_pagination=True,
            column_data=[
                ("[font=my_font]" + "序号" + "[/font]", dp(25)),
                ("[font=my_font]" + "批准文号" + "[/font]", dp(35)),
                ("[font=my_font]" + "药品种类" + "[/font]", dp(50)),
            ],
            row_data=self.new_table
        )
        # 清除旧表格并添加新表格
        self.ids.search_history.add_widget(self.table)
class CheckHistoryScreen(Screen):
    pass
        
screen.add_widget(SplashScreen(name='splash'))
screen.add_widget(LoginScreen(name='login'))
screen.add_widget(RegisterScreen(name='register'))
screen.add_widget(DashboardScreen(name='dashboard'))
screen.add_widget(DashboardScreen(name='capturescreen'))
screen.add_widget(SearchMedicineScreen(name="searchmedicine"))
screen.add_widget(ReminderScreen(name="reminder")) 
screen.add_widget(SetupScreen(name="setup"))
screen.add_widget(SearchHistyoryScreen(name="search_history"))
screen.add_widget(VideoScreendouble(name="videoscreendouble"))
screen.add_widget(CheckScreen(name="checkscreen"))
screen.add_widget(CheckHistoryScreen(name="checkhistoryscreen"))

class MyApp(MDApp):

  def build(self):
      return Builder.load_file("my.kv")

if __name__ == "__main__":
    MyApp().run()