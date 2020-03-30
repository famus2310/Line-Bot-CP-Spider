# mybot/app.py
import os
import datetime
from decouple import config
from flask import (
    Flask, request, abort
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, JoinEvent, FollowEvent
)
app = Flask(__name__)
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
    
def credit():
    return "- Made by Komunitas CP TC with \u2764\n\n"

@app.route("/announce", methods=['POST'])
def announce():
    msg = "This contest will start in less than 2 Hour.\n"
    msg += "Make sure you already registered!\n\n"
    msg += request.form['text']

    with open("static_file/groups.txt", "r") as f:
        for line in f:
            try:
                line_bot_api.push_message(
                    line,
                    TextSendMessage(text=msg)
                )
            except:
                pass

    with open("static_file/users.txt", "r") as f:
        for line in f:
            try:
                line_bot_api.push_message(
                    line,
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


@handler.add(JoinEvent)
def handle_join(event):
    with open("static_file/groups.txt", "a") as f:
        f.write(event.source.group_id + '\n')

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
    print(event)
    if event.source.type == 'group':
        groupExist = False
        with open("static_file/groups.txt", "r") as f:
            for lines in f:
                if event.source.group_id in lines:
                    groupExist = True

        if not groupExist:
            with open("static_file/groups.txt", "a+") as f:
                f.write(event.source.group_id + '\n')

    if event.source.type == 'room':
        roomExist = False
        with open("static_file/rooms.txt", "r") as f:
            for lines in f:
                if event.source.room_id in lines:
                    roomExist = True
        
        if not roomExist:
            with open("static_file/rooms.txt", "a+") as f:
                f.write(event.source.room_id + '\n')

    if event.source.type == 'user':
        userExist = False
        with open("static_file/users.txt", "r") as f:
            for lines in f:
                if event.source.user_id in lines:
                    userExist = True
        
        if not userExist:
            with open("static_file/users.txt", "a+") as f:
                f.write(event.source.user_id + '\n')

    if event.message.text == '!help':
        msg =  "------------------------------------------\n"
        msg += "| Here's your command: |\n"
        msg += "------------------------------------------\n"
        msg += credit()
        msg += "1. !schedule\n[to see all upcoming contest]\n\n"
        msg += "2. !help\n[to see list of commands]"
        sendReplyMessage(event.reply_token, msg)

    if event.message.text == '!schedule':
        msg =  "-----------------------------------------------------\n"
        msg += "| Here's your Contest Schedule: |\n"
        msg += "-----------------------------------------------------\n"
        msg += credit()
        reply = True
        with open('tobeannounced.txt', 'r+') as announce:
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



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)