import os
import datetime
from decouple import config
from flask import (
    Flask, request, abort
)
from flask_sqlalchemy import SQLAlchemy

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, JoinEvent, FollowEvent
)
app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Contest
from models import Notify


# get LINE_CHANNEL_ACCESS_TOKEN from your environment variable
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
# get LINE_CHANNEL_SECRET from your environment variable
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

def sendPushMessage(event, msg):
    if event.source.type == 'group':
        line_bot_api.push_message(
            event.source.group_id,
            TextSendMessage(text=msg)
        )
    elif event.source.type == 'user':
        line_bot_api.push_message(
            event.source.user_id,
            TextSendMessage(text=msg)
        )
    elif  event.source.type == 'room':
        line_bot_api.push_message(
            event.source.room_id,
            TextSendMessage(text=msg)
        )

def sendReplyMessage(token, msg):
    line_bot_api.reply_message(
        token,
        TextSendMessage(text=msg)
    )

def updateNotify(event, action):
    source_type, source_id = "", ""
    if event.source.type == 'group':
        source_type = 'group'
        source_id = event.source.group_id
    elif event.source.type == 'user':
        source_type = 'user'
        source_id = event.source.user_id
    elif  event.source.type == 'room':
        source_type = 'room'
        source_id = event.source.room_id

    notify = Notify(
        source_type = source_type,
        source_id = source_id
    )

    obj = Notify.query.filter(Notify.source_id == source_id, Notify.source_type == source_type)
    print(obj)
    is_exist = obj.scalar()
    if action == 'add':
        if is_exist is None:
            try:
                db.session.add(notify)
                db.session.commit()
                msg =  "---------------------------------------\n"
                msg += "| Notifier: |\n"
                msg += "---------------------------------------\n"
                msg += credit()
                msg += "You will be notified for upcoming contest that have less than 2 hours left for registration :)"
                sendReplyMessage(event.reply_token, msg)
                return 'OK'
            except:
                db.session.rollback()
                return 'DB ERROR'
        else:
            msg =  "---------------------------------------\n"
            msg += "| Notifier: |\n"
            msg += "---------------------------------------\n"
            msg += credit()
            msg += "You already registered with Notifier :)"
            sendReplyMessage(event.reply_token, msg)
            return 'OK'
    elif action == 'delete':
        if is_exist is None:
            msg =  "---------------------------------------\n"
            msg += "| Notifier: |\n"
            msg += "---------------------------------------\n"
            msg += credit()
            msg += "You are not registered with Notifier :("
            sendReplyMessage(event.reply_token, msg)
            return 'OK'
        else:
            try:
                print(obj.first())
                db.session.delete(obj.first())
                db.session.commit()
                msg =  "---------------------------------------\n"
                msg += "| Notifier: |\n"
                msg += "---------------------------------------\n"
                msg += credit()
                msg += "You will be unnotified by Notifier :("
                sendReplyMessage(event.reply_token, msg)
                return 'OK'
            except:
                db.session.rollback()
                return 'DB ERROR'
    

def check_secret_key(key):
    return key == app.config['SECRET_KEY']

def get_all_contest():
    contests = [x.serialize() for x in Contest.query.all()]
   
    list_of_contest = []
    for contest in contests:
        list_of_contest.append(str(contest["title"]) + " (" + str(contest["link"]) + ")\n")
    
    return list_of_contest

def get_all_notify():
    notifies = [x.serialize() for x in Notify.query.all()]
    return notifies
    
def credit():
    return "- Made by Komunitas CP TC with \u2764\n\n"

@app.route("/announce", methods=['POST'])
def announce():
    key = request.form['secret_key']
    if not check_secret_key(key):
        return "Key doesnt match"
    msg = "This contest will start in less than 2 Hour.\n"
    msg += "Make sure you already registered!\n\n"
    msg += request.form['text']

    list_of_notify = get_all_notify()
    
    for notify in list_of_notify:
        try:
            line_bot_api.push_message(
                str(notify['source_id']),
                TextSendMessage(text=msg)
            )
        except:
            pass

    return 'OK'

@app.route("/callback", methods=['POST'])
def callback():
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

@app.route('/refresh_contest', methods=['POST'])
def refresh_contest():
    key = request.json["secret_key"]
    if not check_secret_key(key):
        return "Key doesnt match"
    list_of_contest = request.json['contests']
    try:
        num_rows_deleted = db.session.query(Contest).delete()
        for contest in list_of_contest:
            new_contest = Contest(
                title = contest['title'],
                link = contest['link']
            )
            db.session.add(new_contest)
        db.session.commit()
        return 'OK'
    except:
        db.session.rollback()
        return 'ERROR DB'
    


@handler.add(JoinEvent)
def handle_join(event):
    welcome = "Hello, we hope you enjoy using this\n"
    welcome += "bot. Type !help for list of command :)\n\n"
    welcome += credit()
    welcome += "- Credit by:\n\u2022 famus231\n\u2022 minumcoklatpanas"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome)
    )

@handler.add(FollowEvent)
def handle_follow(event):
    welcome = "Hello, we hope you enjoy using this\n"
    welcome += "bot. Type !help for list of command :)\n\n"
    welcome += credit()
    welcome += "- Credit by:\n\u2022 famus231\n\u2022 minumcoklatpanas"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome)
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if event.message.text == '!help':
        msg =  "------------------------------------------\n"
        msg += "| Here's your command: |\n"
        msg += "------------------------------------------\n"
        msg += credit()
        msg += "1. !schedule\n[to see all upcoming contest]\n\n"
        msg += "2. !notify\n[to get notified for upcoming contest]\n\n"
        msg += "3. !unnotify\n[to disable notifier for upcoming contest]\n\n"
        msg += "4. !help\n[to see list of commands]"
        sendReplyMessage(event.reply_token, msg)

    if event.message.text == '!schedule':
        msg =  "-----------------------------------------------------\n"
        msg += "| Here's your Contest Schedule: |\n"
        msg += "-----------------------------------------------------\n"
        msg += credit()
        reply = True
        announce = get_all_contest()
        for lines in announce:
            cur = '*' + lines + '\n'
            if (len(msg) + len(cur) < 1000):
                msg += cur
            else:
                if reply:
                    sendReplyMessage(event.reply_token, msg)
                else:
                    sendPushMessage(event, msg)
                reply = False
                msg = cur
        
        if len(msg) != 0:
            if reply:
                sendReplyMessage(event.reply_token, msg)
            else:
                sendPushMessage(event, msg)

    if event.message.text == '!notify':
        updateNotify(event, 'add')
    
    if event.message.text == '!unnotify':
        updateNotify(event, 'delete')

if __name__ == "__main__":
    app.run()