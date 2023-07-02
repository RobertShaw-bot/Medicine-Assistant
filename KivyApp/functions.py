import contextlib
import pymysql
from kivy.clock import Clock, mainthread
from kivymd.app import MDApp
from kivy.core.window import Window
import re
import pymysql
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.pickers import MDTimePicker
from kivy.metrics import dp

ip= "db4free.net"
use="mediciner"
passd="wbx20030206@"
data="project_medicine"
# ip= "192.168.2.111"
# use="app_data"
# passd="Wbx20030206@"
# data="name"

mydb = pymysql.connect(
        host=ip,  # mySQL 数据库的主机名
        user=use,  # mySQL 数据库的用户名
        password=passd,  # mySQL 数据库的密码
        database=data  # mySQL 数据库的名称
)


# 创建游标对象
mycursor = mydb.cursor()
mycursor = mydb.cursor()


def callbackregister(self, *args):
  MDApp.get_running_app().root.current = 'login'

def create_post(self, name, cpf, password):
  from kivy.core.text import LabelBase
  LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")
  try:
    # 检查用户信息是否完整，如果不完整，则显示相应的错误消息
    if name == "":
      self.ids.lbregister.text = "insert name"

    elif cpf == "":
      self.ids.lbregister.text = "insert IDnum"

    elif password == "":
      self.ids.lbregister.text = "insert password"  

    else:
      # 将用户信息插入 mySQL 数据库
      sql = "INSERT INTO users (name, cpf, password) VALUES (%s, %s, %s)"
      val = (name, cpf, password)
      mycursor.execute(sql, val)
      mydb.commit()

      self.ids.lbregister.text = "恭喜！正在跳转..."
      Clock.schedule_once(self.callbackregister, 3) # 回调函数，在 3 秒后切换屏幕

      # 将用户信息写入以 CPF 为名称的文本文件
      global user_info
      user_info = [name, cpf, password]
      with open(f'{cpf}.txt',"w") as a:
        a.write(str(user_info[0]))
        a.write("\n")
        a.write(str(user_info[1]))
        a.write("\n")
        a.write(str(user_info[2]))
    
  except ValueError:
    pass           


# TODO Rename this here and in `create_post`
def _extracted_from_create_post_(self, name, cpf, password):
  # 将用户信息插入 mySQL 数据库
  sql = "INSERT INTO users (name, cpf, password) VALUES (%s, %s, %s)"
  val = (name, cpf, password)
  mycursor.execute(sql, val)
  mydb.commit()

  self.ids.lbregister.text = "恭喜！正在跳转..."
  Clock.schedule_once(self.callbackregister, 3) # 回调函数，在 3 秒后切换屏幕

  # 将用户信息写入以 CPF 为名称的文本文件
  global user_info
  user_info = [name, cpf, password]
  with open(f'{cpf}.txt',"w") as a:
    a.write(str(user_info[0]))
    a.write("\n")
    a.write(str(user_info[1]))
    a.write("\n")
    a.write(str(user_info[2]))        

def get_post(self,cpf,senha):
  from kivy.core.text import LabelBase
  LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")
  config={

    'user':use,
    'password':passd,
    'host':ip,
    'database':data
  }

  cnx=pymysql.connect(**config)

  cursor = cnx.cursor()
  query = ("SELECT * FROM users WHERE cpf = %s AND password = %s")
  cursor.execute(query, (cpf, senha))
  IDnum=cursor.fetchone()

  cursor.close()
  cnx.close()

  if IDnum is None:
    self.ids.lblogin.text = "请输入账号" if IDnum=="" else "账号不存在"
  elif IDnum[3]!=senha:
    self.ids.lblogin.text="错误密码！"
  else:
    self.ids.lblogin.text="登录成功！"
    Clock.schedule_once(self.callbacklogin,1)
  
def callbacklogin(self, *args):
  MDApp.get_running_app().root.current = 'dashboard'

def ocr_img(self,img_path):
  import cv2
  import base64
  import requests
  import json
  def cv2_to_base64(image):
      data = cv2.imencode('.jpg', image)[1]
      return base64.b64encode(data.tostring()).decode('utf8')

# 发送HTTP请求
  data = {'images':[cv2_to_base64(cv2.imread(img_path))]}
  headers = {"Content-type": "application/json"}
  url = "http://127.0.0.1:8866/predict/chinese_ocr_db_crnn_server"
  r = requests.post(url=url, headers=headers, data=json.dumps(data))

# 打印预测结果
  result=r.json()["results"]
  text_list = [item['text'] for item in result[0]['data']]
  text = ' '.join(text_list)
  text=text.replace(" ","")
  text_results = [text]
  
  text_results[0] = re.sub("[^\u4e00-\u9fff0-9]", "", text_results[0])
  return text_results

def search_name(self,element:list):
    id_result=[]
    ix = open_dir("KivyApp/indexdir")
    with ix.searcher() as searcher:
      query = QueryParser("product_name", ix.schema).parse(element[0])
      results = searcher.search(query,limit=3)
      id_result.extend(i.get("id") for i in results)
    print(id_result)
    return id_result

def search_in_database1(self, results: list):
  result_name_list = []
  try:
    # 远程连接Windows主机上的MySQL服务器
    config = {
        'user': use,
        'password': passd,
        'host': ip,
        'database': data
    }
    conn = pymysql.connect(**config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = "SELECT * FROM 查询 WHERE ID=%s"

    for result_id in results:
            # id = result.get('\ufeffID')
      try:
        cursor.execute(query, (result_id,))
        if result_from_db := cursor.fetchone():
          result_name = result_from_db.get("产品名称")
          approval_number = result_from_db.get("批准文号")
          result_name_list.append((result_name, approval_number))
        else:
          raise ValueError(f"未查询到ID: {id}")
      except pymysql.Error as e:
          print(f"未在数据库中查询到结果: {e}")
          return None
    cursor.close()
    conn.close()
  except pymysql.Error as e:
      raise ConnectionError("Failed to connect to the database.")

  return result_name_list
def search_in_database(self, medicine_name):
    db_name = pymysql.connect(
        host=ip,  # mySQL 数据库的主机名
        user=use,  # mySQL 数据库的用户名
        password=passd,  # mySQL 数据库的密码
        database=data  # mySQL 数据库的名称
    )
    self.mycursor = db_name.cursor()
    query = f"SELECT * FROM 查询 WHERE 批准文号 LIKE '%{medicine_name}%'OR 产品名称 LIKE '%{medicine_name}%'"

    self.mycursor.execute(query)
    rows = self.mycursor.fetchall()

    #self.search_list.append((rows[0],"[font=my_font]"+rows[0][1]+"[/font]","[font=my_font]"+rows[0][2]+"[/font]"))
    from kivy.core.text import LabelBase
    LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")
    if len(rows) == 0:
      search_result_text = [("[font=my_font]" + "暂无" + "[/font]",
                            "[font=my_font]" + "暂无" + "[/font]",
                            "[font=my_font]" + "暂无" + "[/font]",
                            "[font=my_font]" + "暂无" + "[/font]",
                            "[font=my_font]" + "暂无" + "[/font]",
                            "[font=my_font]" + "暂无" + "[/font]")]
      self.search_list=search_result_text
    else:
      search_result_text = []
      for row in rows:
        self.search_list.append((
            len(self.search_list) + 1,
            f"[font=my_font]{row[1]}[/font]",
            f"[font=my_font]{row[2]}[/font]",
        ))
        search_result_text.append((
            len(search_result_text) + 1,
            f"[color=#ff0000][font=my_font]{row[1]}[/font]",
            f"[font=my_font]{row[2]}[/font]",
            f"[font=my_font]{row[3]}[/font]",
            f"[font=my_font]{row[4]}[/font]",
            f"[font=my_font]{row[5]}[/font]",
        ))

    # Create the data table with the search results

    data_tables = MDDataTable(
        size_hint = (1.0, None),
        height= 635,
        pos_hint = {"center_x": 0.5, "center_y": 0.35},
        use_pagination = True,
        column_data=[
            ("[font=my_font]" + "序号" + "[/font]", dp(10)),
            ("[font=my_font]" + "批准文号" + "[/font]", dp(30)),
            ("[font=my_font]" + "产品名称" + "[/font]", dp(35)),
            ("[font=my_font]" + "剂型" + "[/font]", dp(20)),
            ("[font=my_font]" + "规格" + "[/font]", dp(40)),
            ("[font=my_font]" + "生产单位" + "[/font]", dp(45)),
        ],
        row_data=search_result_text,
    )
    data_tables.bind(on_row_press=self.on_row_press)
    self.ids.search_result.clear_widgets()
    self.ids.search_result.add_widget(data_tables)
    if db_name:
        db_name.close()
def SearchHistyoryScreen_on_pre_enter(self):
    from kivy.core.text import LabelBase
    LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")
    self.history=MDDataTable(
        size_hint = (1.0, None),
        height= 635,
        pos_hint = {"center_x": 0.5},
        use_pagination = True,
        check=True,
        column_data=[
            ("[font=my_font]" + "序号" + "[/font]", dp(25)),
            ("[font=my_font]" + "批准文号" + "[/font]", dp(35)),
            ("[font=my_font]" + "产品名称" + "[/font]", dp(50)),
        ],
        row_data=self.search_list,
    )
    search_history_screen = self.manager.get_screen('search_history')
    search_history_screen.ids.search_history.clear_widgets()
    search_history_screen.ids.search_history.add_widget(self.history)


def get_text(self,text):
    self.text=text
    time_dialog =MDTimePicker()
    time_dialog.open()
    time_dialog.bind(on_save=self.get_time)

def get_time(self, instance, time):
  def search(number)->str:
    db_name = pymysql.connect(
      host=ip,  # mySQL 数据库的主机名
      user=use,  # mySQL 数据库的用户名
      password=passd,  # mySQL 数据库的密码
      database=data  # mySQL 数据库的名称
  )
    mycursor = db_name.cursor()
    try:
        number=int(number[1:])       
        query = f"SELECT * FROM 查询 WHERE 批准文号 LIKE '%{number}%'"
        mycursor.execute(query)
        rows = mycursor.fetchall()
        return rows[0][2]
    except ValueError:
        return number
  name = search(self.text)
  # # 获取时间并添加到表格行中
  reminder = time.strftime('%H:%M')
  # print(type(reminder)) 类型：str
  i=len(self.table_rows)
  self.table_rows.append((
      i + 1,
      (
          "checkbox-marked-circle",
          [39 / 256, 174 / 256, 96 / 256, 1],
          reminder,
      ),
      ("alert-circle", [1, 0, 0, 1], "[font=my_font]" + "每天" + "[/font]"),
      f"[font=my_font]{name}[/font]",
  ))
  self.time_list.append(reminder)

  # 创建字体格式
  from kivy.core.text import LabelBase
  LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")

  # 创建新的 MDDataTable
  self.table = MDDataTable(
      size_hint=(1.0, .74),
      height=400,
      check=True,
      pos_hint={"center_x": 0.5, "center_y": 0.38},
      use_pagination=True,
      column_data=[
          ("[font=my_font]" + "序号" + "[/font]", dp(30)),
          ("[font=my_font]" + "提醒时间" + "[/font]", dp(30)),
          ("[font=my_font]" + "重复次数" + "[/font]", dp(30)),
          ("[font=my_font]" + "药品名称" + "[/font]", dp(30)),
      ],
      row_data=self.table_rows
  )
  # 清除旧表格并添加新表格
  self.table.bind(on_row_press=self.on_row_press)
  self.ids.show_data.clear_widgets()
  self.ids.show_data.add_widget(self.table)

def get_new_time(self, instance, time):
    def map_to_sequence(number):
      return (number - 1) // 4 
    index=map_to_sequence(self.index)
    # print(self.table_rows[index])
    new_list=list(self.table_rows[index][1])
    new_time = time.strftime('%H:%M')
    new_list[2]=new_time
    now_list=list(self.table_rows[index])
    now_list[1]=tuple(new_list)
    self.table_rows[index]=tuple(now_list)
    self.make_table()
# 1 5 9 13
# 1 2 3 4

def delete_selected_rows(self):
    ids = self.table.get_row_checks()
   # print(ids) #测试用
    for id in ids:
        temp = id[0][0]
        for i, row in enumerate(self.table_rows):
            if int(temp) == int(row[0]):
                self.table_rows.pop(i)
                self.time_list.remove(row[1][2])
                break
    self.make_table()

def make_table(self):
  self.new_table = [(i + 1, row[1], row[2], row[3])
                    for i, row in enumerate(self.table_rows)]
  self.table_rows=self.new_table
  #清除子组件
  self.ids.show_data.clear_widgets()
  from kivy.core.text import LabelBase
  LabelBase.register(name="my_font", fn_regular="KivyApp/simhei.ttf")
  # 创建新的 MDDataTable
  self.table = MDDataTable(
      size_hint=(1.0, .74),
      height=400,
      check=True,
      pos_hint={"center_x": 0.5, "center_y": 0.38},
      use_pagination=True,
      column_data=[
          ("[font=my_font]" + "序号" + "[/font]", dp(30)),
          ("[font=my_font]" + "提醒时间" + "[/font]", dp(30)),
          ("[font=my_font]" + "重复次数" + "[/font]", dp(30)),
          ("[font=my_font]" + "药品名称" + "[/font]", dp(30)),
      ],
      row_data=self.new_table
  )
  # 清除旧表格并添加新表格
  self.table.bind(on_row_press=self.on_row_press)
  self.ids.show_data.add_widget(self.table)
