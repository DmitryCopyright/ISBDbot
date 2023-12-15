import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot_handlers import router


# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token="6595158179:AAErWoB6AsyO7aais0qI3R5V0kwl-mb6Yn0")

# Инициализация диспетчера с хранилищем в памяти
dp = Dispatcher(storage=MemoryStorage())

# Привязываем роутер к диспетчеру
dp.include_router(router)

# Запуск бота
async def main():
    # Запуск опроса сервера Telegram
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())