import telegram.ext

from book_catalog import search_books, get_book_details
from user_management import register_user, log_in_user
from config import TELEGRAM_TOKEN

# Инициализируем Updater с использованием токена бота
updater = telegram.ext.Updater(token=TELEGRAM_TOKEN, use_context=True)

# Получаем диспетчера для регистрации обработчиков
dispatcher = updater.dispatcher

# Функция обработчика команды старта
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Добро пожаловать в библиотечный бот!")

# Функция обработчика регистрации пользователя
def register(update, context):
    register_user(update.message.from_user)
    update.message.reply_text("Вы успешно зарегистрированы!")

# Функция обработчика входа пользователя
def login(update, context):
    log_in_user(update.message.from_user)
    update.message.reply_text("Вы вошли в систему!")

# Обработчик команды /search
def search(update, context):
    # Пользователь ввел команду /search <запрос>
    query = ' '.join(context.args)
    results = search_books(query)
    if results:
        reply = '\n'.join([f"{book['name']} - {book['author']}" for book in results])
    else:
        reply = "Книги не найдены."
    update.message.reply_text(reply)

# Обработчик команды /bookdetails
def book_details(update, context):
    # Пользователь ввел команду /bookdetails <id книги>
    book_id = ' '.join(context.args)
    details = get_book_details(book_id)
    if details:
        reply = f"Название: {details['name']}\nАвтор: {details['author']}\nISBN: {details['ISBN']}\nКоличество: {details['copies']}"
    else:
        reply = "Детали книги не найдены."
    update.message.reply_text(reply)

# Добавляем обработчики команд
dispatcher.add_handler(telegram.ext.CommandHandler('start', start))
dispatcher.add_handler(telegram.ext.CommandHandler('register', register))
dispatcher.add_handler(telegram.ext.CommandHandler('login', login))
dispatcher.add_handler(telegram.ext.CommandHandler('search', search))
dispatcher.add_handler(telegram.ext.CommandHandler('bookdetails', book_details))

# Начинаем поиск обновлений
updater.start_polling()

# Запускаем бота, пока не будет получен сигнал остановки
updater.idle()
