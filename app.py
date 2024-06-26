import psycopg2

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


#======這裡是呼叫的檔案內容=====
from message import *
from new import *
from Function import *
#======這裡是呼叫的檔案內容=====

#======python的函數庫==========
import tempfile, os
import datetime
import time
#======python的函數庫==========
#---------------------------------------------------------------------------------------------------------------------
app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi('hi6hwoyDgSvIO7Z2Ymms71tDmKdqRTk53DCUTwVJU+fzcD3VPbRYz2Vm6oqG7Av1ybOfzy55J2N++elx6HoBzLHqr7BrasOWuthq1yr0mt4KATlvCnzSDiKFXjB4WtRN1OADFJZc1FY2EcGwjDZwuwdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('b5cbd67950dc5c0c1e9e007e736355c1')

# 設置連線PostgreSQL時所需參數
db_name="janfanchallenge"
db_user="fanfan"
db_password="5zzyVXNUBQqA9SgxgT3faewT8bpTJbP2"
db_host="dpg-cof2ft8cmk4c73fusrm0-a.singapore-postgres.render.com"
db_port=5432
#---------------------------------------------------------------------------------------------------------------------
#建立連線函式庫(CREATE, INSERT, UPDATE, DELETE用)
def postgreSQLConnect(command):
  #建立連接
  with psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port) as conn:
    with conn.cursor() as cur:
      #建立游標
      cur=conn.cursor()

      #建立SQL指令
      sql_command=command

      #執行指令
      cur.execute(sql_command)

    #提交
    conn.commit()
#---------------------------------------------------------------------------------------------------------------------
def postgreSQLSelect(command):
  #建立連接
  with psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port) as conn:
    with conn.cursor() as cur:
      #建立游標
      cur=conn.cursor()

      #建立SQL指令
      sql_command=command

      #執行指令
      cur.execute(sql_command)

      #將查詢結果儲存
      row = cur.fetchall()

  #回傳查詢結果
  return row
#---------------------------------------------------------------------------------------------------------------------
# 監聽所有來自 /callback 的 Post Request    
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
#---------------------------------------------------------------------------------------------------------------------

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    uid = str(event.source.user_id)
    if '出題' in msg:
        sql_select_ans_table='''
        SELECT * FROM album_list as al, song_list as sl
        WHERE al.album_no=sl.album_no
        ORDER BY RANDOM()
        LIMIT 1
        '''
        #執行
        x=postgreSQLSelect(sql_select_ans_table)
        ansab=x[0][0]
        anssgno=x[0][5]
        qname=x[0][6]
        # print(qname)
        # print(ansab)
        # print(anssgno)
        # print(x)


        sql_update_answer_list=f'''
        UPDATE answer_list SET answer_album='{ansab}',answer_song={anssgno} WHERE userid='{uid}'
        '''
        postgreSQLConnect(sql_update_answer_list)
        message = TextSendMessage(text=qname)
        line_bot_api.reply_message(event.reply_token, message)

    elif '不知道，正解?' in msg:
        sql_user_noidea=f'''
        select * 
        from album_list as a, answer_list as b 
        where a.album_no=b.answer_album 
        and userid='{uid}'
        '''
        #執行
        usernoidealist=postgreSQLSelect(sql_user_noidea)
        usernoideaalbum=usernoidealist[0][2]
        usernoideasongno=usernoidealist[0][6]
        noideastr=f"{usernoideaalbum} {usernoideasongno}"
        message = TextSendMessage(text=noideastr)
        line_bot_api.reply_message(event.reply_token, message)
    elif '開發人員' in msg:
        edveloper='''發起人:FanFan
程式開發:FanFan
技術總監:KaiN
參與人員:FanFan KaiN Eating WeiWei Turtle Chien Fish Xuan
場地提供(自費):客美多咖啡
快來看:Jay Chou
玩玩看:各大資深杰倫粉
        '''
        btMsg=TextSendMessage(text=edveloper)   
        line_bot_api.reply_message(event.reply_token, btMsg)
    elif '開始遊戲' in msg:
        sql_user_query=f'''
        select * 
        from answer_list where userid='{uid}'
        '''
        usercheck=postgreSQLSelect(sql_user_query)
        if len(usercheck)==0 :
            answer_album='df'
            song_order=0
            sql_insert_answer_list_table=f"INSERT INTO answer_list VALUES('{uid}','{answer_album}',{song_order});"
            #執行
            postgreSQLConnect(sql_insert_answer_list_table)
        message = TextSendMessage(text="點擊出題開始")
        line_bot_api.reply_message(event.reply_token, message)
    else:
        try:
            y=msg.split(' ')
            ansalb=y[0]
            ansno=y[1]
            sql_select_ans_table=f'''
            select * 
            from album_list as a, song_list as b 
            where a.album_no=b.album_no 
            and a.album_order={ansalb} 
            and b.song_order={ansno}
            '''
            #執行
            x=postgreSQLSelect(sql_select_ans_table)
            if len(x) != 0 :
                trueansalbum=x[0][0]
                trueansalbumname=x[0][2]
                trueansalbumpic=x[0][3]

                sql_user_table=f'''
                SELECT * FROM answer_list
                WHERE userid='{uid}'
                '''
                #執行
                useranslist=postgreSQLSelect(sql_user_table)
                useransalb=useranslist[0][1]
                useranssongno=str(useranslist[0][2])
                if (useransalb==trueansalbum) and (useranssongno==ansno) :
                    btMsg=TemplateSendMessage(
                        alt_text='ButtonsTemplate',
                        template=ButtonsTemplate(
                            thumbnail_image_url=trueansalbumpic,
                            title='回答正確！',
                            text=trueansalbumname+' '+useranssongno,
                            actions=[MessageAction(
                                    label='下一題',
                                    text='出題'
                                )]
                        )
                    )
                else:
                    btMsg=TextSendMessage(text="回答錯誤，請重新輸入!")     

                line_bot_api.reply_message(event.reply_token, btMsg)
            else:
                btMsg=TextSendMessage(text="回答錯誤，請重新輸入!")   
                line_bot_api.reply_message(event.reply_token, btMsg)
        except:       
            btMsg=TextSendMessage(text="請按照格式回答:專輯序 曲序 \n例:2 8\n或者請點選圖文選單\"不知道，正解?\"")   
            line_bot_api.reply_message(event.reply_token, btMsg)
        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
