import os
import subprocess
from telegram import Bot, Update
from telegram.ext import Filters, MessageHandler, Updater
import re
import time

bot_token = "63xxxxx4:AAF_6l9-Hrxxxxxxxxxxxxxxxxxxxx5EGI"
chat_ids = ["-1001xxxxxxxxx696", "-1xxxxxxxx636", "-10019xxxxxxxxx12", "17xxxxxxx04"]
file_path_predictions = os.path.join(os.getcwd(), "./predictions.txt")
last_request_time = 0

def send_message(update, context):
    global last_request_time
    if update.effective_message.text.lower() == "zq" and str(update.effective_chat.id) in chat_ids:
        current_time = time.time()
        if current_time - last_request_time < 666:
            wait_time = 666 - int(current_time - last_request_time)
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"请等待 {wait_time} 秒后再请求... \n\n可发送 1 先玩会游戏后🦉再试")
            return

        last_request_time = current_time
        subprocess.run(["python", "1datamain.py"])
        result = subprocess.run(["python", "2data.py"], capture_output=True, text=True)
        if "此时没有中场休息的比赛" in result.stdout:
            context.bot.send_message(chat_id=update.effective_chat.id, text="此时没有中场休息的比赛")
            return

        subprocess.run(["python", "3ppo.py"])

        if os.path.exists(file_path_predictions) and os.path.getsize(file_path_predictions) > 0:
            with open(file_path_predictions, "r") as file:
                message = file.read()

            message = re.sub(r'(\.\d)\d+', r'\1', message)

            if len(message) <= 4096:
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            else:
                for i in range(0, len(message), 4096):
                    context.bot.send_message(chat_id=update.effective_chat.id, text=message[i:i+4096])

            os.remove(file_path_predictions)

def main():
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher
    handler = MessageHandler(Filters.text, send_message)
    dispatcher.add_handler(handler)
    updater.start_polling()

if __name__ == "__main__":
    main()
