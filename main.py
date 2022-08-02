from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.dispatcher.filters import Text
import re


TOKEN = ''  # Токен Телеграм-бота
OWNER = ''  # ID чата администратора бота (кто будет видеть запросы от пользователей)

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


# Создание кнопок для меню
def get_menu(menu_name):
	match menu_name:  # match работает в Python начиная с версии 3.10. Если у вас версия старее, замените на if-else
		case 'startmenu':
			buttons = [
				types.InlineKeyboardButton(text='Наш сайт', url='https://ya.ru'),
				types.InlineKeyboardButton(text='Разработчик', url='t.me/zakart83'),
				types.InlineKeyboardButton(text='Новое меню', callback_data='btn_submenu'),
			]
		case 'submenu':
			buttons = [
				types.InlineKeyboardButton(text='Кнопка 1', callback_data='btn_back'),
				types.InlineKeyboardButton(text='Кнопка 2', callback_data='btn_back'),
				types.InlineKeyboardButton(text='Назад', callback_data='btn_back'),
			]
		case _:
			buttons = [
				types.InlineKeyboardButton(text='Назад', callback_data='btn_back'),
			]

	keyboard = types.InlineKeyboardMarkup(row_width=2)
	keyboard.add(*buttons)
	return keyboard


# Обработчик команды Start и вывод главного меню
@dp.message_handler(commands='start')
async def process_start(message: types.Message):
	if str(message.chat.id) == OWNER:
		try:
			await message.answer('Привет! Здесь будут сообщения от пользователей.')
		except Exception as ex:
			print(ex)
	else:
		try:
			await message.answer('Отправьте Ваше сообщение или воспользуйтесь меню', reply_markup=get_menu('startmenu'))
		except Exception as ex:
			print(ex)


# Обработчик нажатий кнопок
@dp.callback_query_handler(Text(startswith='btn'))
async def callbacks(call: types.CallbackQuery):
	match call.data:  # match работает в Python начиная с версии 3.10. Если у вас версия старее, замените на if-else
		case 'btn_submenu':
			await call.message.edit_text('Новое меню', reply_markup=get_menu('submenu'))
		case 'btn_back':
			await call.message.edit_text('Главное меню', reply_markup=get_menu('startmenu'))
		case _:
			await call.message.edit_text('Главное меню', reply_markup=get_menu('startmenu'))


# Обработчик сообщений
@dp.message_handler()
async def messages(message: types.Message):
	if str(message.chat.id) == OWNER:
		if message.reply_to_message:
			try:
				message_data = message.reply_to_message.text
				original_user_id = re.findall('UID: [0-9]+', message_data)[0].replace('UID: ', '').strip()
				original_message_id = re.findall('MID: [0-9]+', message_data)[0].replace('MID: ', '').strip()
				await bot.send_message(original_user_id, message.text, reply_to_message_id=original_message_id, allow_sending_without_reply=True)
				text = f'Сообщение было отправлено пользователю с ID: {original_user_id}'
				await bot.send_message(OWNER, text)
			except Exception as ex:
				print(ex)
	else:
		try:
			await bot.send_message(OWNER, f'<b>Сообщение от {hlink(message.from_user.first_name, "tg://user?id=" + str(message.from_user.id))} (UID: {message.from_user.id}, MID: {message.message_id})</b> \n {message.text}')
			await bot.send_message(message.chat.id, f'{message.from_user.first_name}, ваше сообщение получено.')
		except Exception as ex:
			print(ex)


if __name__ == '__main__':
	executor.start_polling(dp)
