import logging

from aiogram import Bot, Dispatcher, executor, types
from database import initialize_db
initialize_db()

from models.user import User

API_TOKEN = '6066037597:AAGVuYIkXZYm7Bx_a5GzVpQCmd2mtYcqFZ0'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    User.first_or_create(telegram_id=message.chat.id)
    await message.reply(
        "Привет! Используй команду /help, чтобы узнать список доступных команд!"
    )

@dp.message_handler(commands=['user'])
async def echo(message: types.Message):
    user = User.first_or_create(telegram_id=message.chat.id)
    await message.answer(f'Ваш telegram_id = {user.telegram_id}, status = {user.status}')

@dp.message_handler(commands=['set_age'])
async def set_age(message: types.Message):
    user = User.first_or_create(telegram_id=message.chat.id)
    user.status = 'setting_age'
    user.save()
    await message.answer(f'Введите ваш возраст')

@dp.message_handler(commands=['find_an_interlocutor'])
async def set_age(message: types.Message):
    user = User.first_or_create(telegram_id=message.chat.id)
    if user.age == None:
      await message.answer(f'Нужно указать возраст чтобы воспользоваться данной функцией')
      return

    user.status = 'finding'
    user.save()
    await message.answer(f'Мы начали искать вам собеседника')
    opponent = User.where(
        'status', '=', 'finding'
        ).where(
          'telegram_id', '!=', user.telegram_id
        ).where(
          'age', '=', user.age
        ).order_by('random()').first()

    if opponent != None:
        user.opponent_id = opponent.telegram_id
        user.save()
        opponent.opponent_id = user.telegram_id
        opponent.save()
        await message.answer(f'Мы нашли вам собеседника, перейдите в /chat')
        await bot.send_message(opponent.telegram_id, 'Мы нашли вам собеседника, перейдите в /chat')

@dp.message_handler(commands=['chat'])
async def set_chatting(message: types.Message):
    user = User.first_or_create(telegram_id=message.chat.id)
    user.status = 'chatting'
    user.save()

@dp.message_handler(commands=['stop'])
async def set_age(message: types.Message):
    user = User.first_or_create(telegram_id=message.chat.id)
    user.status = None
    user.save()

@dp.message_handler()
async def message_handl(message: types.Message):
      user = User.first_or_create(telegram_id=message.chat.id)
      if user.status == 'setting_age':
          user.age = int(message.text)
          user.save()
          await message.answer(f'Возраст проставлен в {user.age}')
      if user.status == 'chatting':
          await bot.send_message(user.opponent_id, message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
