import telegram.ext
import logging

from telegram.ext import CommandHandler

from bot_handlers import start, search, book_details
from user_management import register_user, log_in_user, get_user_profile, update_user_profile
from book_catalog import get_available_books, reserve_book, get_user_reservations, book_available
from config import TELEGRAM_TOKEN
from utils import setup_logging

# Настраиваем логирование
setup_logging()

# Создаем экземпляр Updater и передаем ему токен нашего бота
updater = telegram.ext.Updater(token=TELEGRAM_TOKEN, use_context=True)

# Получаем диспетчера для регистрации обработчиков
dispatcher = updater.dispatcher

# Регистрируем обработчики команд
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('search', search))
dispatcher.add_handler(CommandHandler('bookdetails', book_details))

# Команды для управления пользователями
dispatcher.add_handler(CommandHandler('register', register_user))
dispatcher.add_handler(CommandHandler('login', log_in_user))
dispatcher.add_handler(CommandHandler('viewprofile', get_user_profile))
dispatcher.add_handler(CommandHandler('editprofile', update_user_profile))

# Команды для работы с каталогом книг
dispatcher.add_handler(CommandHandler('availablebooks', book_available))
dispatcher.add_handler(CommandHandler('reservebook', reserve_book))
dispatcher.add_handler(CommandHandler('myreservations', get_user_reservations))

# Запускаем бота
updater.start_polling()

# Бот будет работать до тех пор, пока не будет остановлен принудительно
updater.idle()
