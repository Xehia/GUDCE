from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,  ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler

import sqlite3
import json
import random
import ast
from datetime import datetime

conn = sqlite3.connect('database.db')
cursor = conn.cursor()


# Crea una tabella per i partecipanti
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lobbies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        players JSON,
        object STRING,
        status INTEGER
    )
''')


# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"**Gioco ufficiale di ciao eccoci** ✨\n\n➤ Usa il comando /help per capire come si gioca", parse_mode='MarkdownV2')
start_handler = CommandHandler('start', start)


# Help command handler
async def help(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"➤ **Crea una lobby**\nUsa il comando /create\n\n➤ **Unisciti alla lobby**\nClicca su gioca e aspetta che venga avviata la partita", parse_mode='MarkdownV2')
help_handler = CommandHandler('help', help)


# Create command handler
async def create(update, context):

    cursor.execute("INSERT INTO lobbies (players, object, status) VALUES (?, ?, ?)", (json.dumps([]), "not-set", 0))
    conn.commit()

    keyboard = [[InlineKeyboardButton("Unisciti 🫂", callback_data='{"target": "join", "lobbyId": '+ str(cursor.lastrowid) +'}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text=f'**Gioco Ufficiale di Ciao eccoci ✨**', parse_mode='MarkdownV2', reply_markup=reply_markup)
create_handler = CommandHandler('create', create)

# Handle the buttons
async def button(update, context):
    """Handle the button press."""
    query = update.callback_query
    await query.answer()

    try:
        query_data_dict = json.loads(query.data)
    except json.decoder.JSONDecodeError:
        print("JSON conversion failed.")
        query_data_dict = {"type": "default"}

    if 'target' in query_data_dict:


        if query_data_dict['target'] == 'join':

            lobbyId = query_data_dict['lobbyId']
            cursor.execute(f"SELECT players FROM lobbies WHERE id = {lobbyId}")
            result = cursor.fetchone()

            try:
                current_players = json.loads(str(result[0]))
                new_players = current_players + [update.effective_user.id]
            except:
                new_players = [update.effective_user.id]

            cursor.execute("UPDATE lobbies SET players = ? WHERE id = ?", (json.dumps(new_players), lobbyId))
            conn.commit()


            if len(new_players) == 1:
                pluralText = "giocatore"
            else:
                pluralText = "giocatori"

            usernames = f"🕹️ *{len(new_players)}* {pluralText} \n\n"


            if len(new_players) < 1:
                keyboard = [[InlineKeyboardButton("Unisciti 🫂", callback_data='{"target": "join", "lobbyId": '+ str(cursor.lastrowid) +'}')]]
            else:
                keyboard = [[InlineKeyboardButton("Unisciti 🫂", callback_data='{"target": "join", "lobbyId": '+ str(cursor.lastrowid) +'}'),
                             InlineKeyboardButton("Avvia 🎲", callback_data='{"target": "forceStart", "lobbyId": '+ str(cursor.lastrowid) +'}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text=f'*Sta inziando una partita\!* ✨\n\n'+usernames, parse_mode='MarkdownV2', reply_markup=reply_markup)

        elif query_data_dict['target'] == 'forceStart':
            lobbyId = query_data_dict['lobbyId']
            cursor.execute(f"SELECT players FROM lobbies WHERE id = {lobbyId}")
            result = cursor.fetchall()


            allPlayersList = ast.literal_eval(result[0][0])
            impostor = random.choice(allPlayersList)
            
            allPlayersList.remove(impostor)

            f = open('list.json')
            data = (json.load(f))

            object = get_random_object(data)
            
            try:
                await context.bot.send_message(chat_id=impostor, text="Sei l'*impostore*\!", parse_mode='MarkdownV2')
            except Exception as e:
                print('ERROR:', e)

            try:
                for user in allPlayersList:
                    await context.bot.send_message(chat_id=user, text=f"*Oggetto:* {object}", parse_mode='MarkdownV2')
            except Exception as e:
                print('ERROR:', e)


def get_random_object(data):
    try:
        return random.choice(data['objects'])
    except Exception as e:
        print(e)
