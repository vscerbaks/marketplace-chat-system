from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import executor
import asyncio
from colorama import Fore, Style,init

from onlineChat import OnlineChat, MessageListenerError
from config import BOT_TOKEN

init()

bot = Bot(token=BOT_TOKEN,parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage(),)

botId, chatId = 0, 0
onlineChat = OnlineChat()

@dp.message_handler(commands='start')
async def handleStartCommand(message: types.Message):
    global botId,chatId

    botId = (await bot.get_me()).id
    chatId = message.chat.id

    msg = await message.reply('Starting chat⏳...')

    if await onlineChat.initializeBrowser():
        
        loop = asyncio.get_running_loop()
        loop.create_task(chatMessageHandler())

        await message.answer('Chat started!✅')

    else: await msg.edit_text('An error occurred while starting the chat!❌')

@dp.message_handler(commands='link')
async def handleLinkCommand(message: types.Message):
    await message.reply(f'Chat link 👉🏻 <a href="{await onlineChat.getChatLink()}">here</a>')

@dp.message_handler(commands='send')
async def handleSendCommand(message: types.Message):
    await sendUserMessage(message,message.get_args())

@dp.message_handler(lambda message: message.reply_to_message)
async def handleReplyMessage(message: types.Message):
    if message.reply_to_message.from_user.id == botId:
        await sendUserMessage(message,message.text)

async def sendUserMessage(message,text):
    if await onlineChat.sendMessage(text):
        await message.reply('Message sent!')
    else:
        await message.reply('Error❌\n Could not send the message!')

async def chatMessageHandler():
    try:
        async for message in onlineChat.getMessages():
                if message:
                    await bot.send_message(chatId,f'<b>New message 📩</b>: {message}')
                else:
                    return await bot.send_message(chatId,'<b>Chat session ended</b>❌ Press /start to continue')

    except MessageListenerError:
        return await bot.send_message(chatId,'New messages from the chat are no longer available❌') 
        
if __name__ == '__main__':
    executor.start_polling(dp)

        
                