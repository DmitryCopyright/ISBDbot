from aiogram import types, Router, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from book_catalog import search_books, get_book_details, get_available_books, reserve_book, get_user_reservations
from user_management import register_user, log_in_user


class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact_data = State()
    waiting_for_reader_number = State()


# Определение состояний для входа
class Login(StatesGroup):
    waiting_for_name = State()
    waiting_for_reader_number = State()

class BookSearch(StatesGroup):
    waiting_for_query = State()

class BookDetails(StatesGroup):
    waiting_for_book_id = State()

class UserLoggedIn(StatesGroup):
    active = State()

class ReserveBook(StatesGroup):
    waiting_for_book_id = State()

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать в библиотечный бот!")

@router.message(Command(commands=["register"]))
async def cmd_register(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        await message.answer("Вы уже зарегистрированы и вошли в систему.")
    else:
        await message.answer("Введите ваше имя:")
        await state.set_state(Registration.waiting_for_name)

@router.message(Registration.waiting_for_name)
async def name_entered(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер/почту:")
    await state.set_state(Registration.waiting_for_contact_data)


@router.message(Registration.waiting_for_contact_data)
async def contact_data_entered(message: types.Message, state: FSMContext):
    await state.update_data(contact_data=message.text)
    await message.answer("Придумайте пароль:")
    await state.set_state(Registration.waiting_for_reader_number)


@router.message(Registration.waiting_for_reader_number)
async def reader_number_entered(message: types.Message, state: FSMContext):
    await state.update_data(reader_number=message.text)
    data = await state.get_data()
    register_user(data['name'], data['contact_data'], data['reader_number'])
    await message.answer("Вы успешно зарегистрированы!")
    await state.clear()


# Вход пользователя
@router.message(Command(commands=["login"]))
async def cmd_login(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        await message.answer("Вы уже вошли в систему.")
    else:
        await message.answer("Введите ваше имя:")
        await state.set_state(Login.waiting_for_name)


@router.message(Login.waiting_for_name)
async def login_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш пароль:")
    await state.set_state(Login.waiting_for_reader_number)


@router.message(Login.waiting_for_reader_number)
async def login_reader_number_entered(message: types.Message, state: FSMContext):
    await state.update_data(reader_number=message.text)
    data = await state.get_data()
    user_exists = log_in_user(data['name'], data['reader_number'])

    if user_exists:
        await state.update_data(logged_in=True, user_id=data['reader_number'])
        await state.set_state(UserLoggedIn.active)  # Переводим пользователя в состояние входа
        await message.answer("Вход выполнен. Добро пожаловать, " + data['name'] + "!")
    else:
        await message.answer("Пользователь с такими данными не найден.")
        await state.clear()


@router.message(Command(commands=["search"]))
async def cmd_search(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        await message.answer("Введите запрос для поиска:")
        await state.set_state(BookSearch.waiting_for_query)
    else:
        await message.answer("Пожалуйста, войдите в систему для использования этой команды.")


@router.message(BookSearch.waiting_for_query)
async def search_query_entered(message: types.Message, state: FSMContext):
    query = message.text
    results = search_books(query)
    if results:
        # Формирование списка найденных книг
        response = "\n".join([f"ID: {book['book_id']}, Название: {book['name']}, Автор: {book['author']}" for book in results])
    else:
        response = "По вашему запросу книги не найдены."
    await message.answer(response)
    await state.clear()



@router.message(Command(commands=["bookdetails"]))
async def cmd_book_details(message: types.Message, state: FSMContext):
    await message.answer("Введите ID книги для получения деталей:")
    await state.set_state(BookDetails.waiting_for_book_id)

@router.message(BookDetails.waiting_for_book_id)
async def book_id_entered(message: types.Message, state: FSMContext):
    book_id = message.text
    details = get_book_details(book_id)
    if details:
        # Формирование ответа с деталями книги
        response = f"Название: {details['name']}\nАвтор: {details['author']}\nISBN: {details['ISBN']}\nКоличество: {details['copies']}"
    else:
        response = "Книга с таким ID не найдена."
    await message.answer(response)
    await state.clear()

@router.message(Command(commands=["exit"]))
async def cmd_exit(message: types.Message, state: FSMContext):
    await state.clear()  # Очищаем все данные из состояния
    await message.answer("Вы вышли из системы.")

@router.message(Command(commands=["availablebooks"]))
async def cmd_available_books(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        books = get_available_books()
        if books:
            response = "\n".join([f"ID: {book['book_id']} Автор: {book['author']} Название: {book['name']}" for book in books])
        else:
            response = "Доступных книг для бронирования нет."
        await message.answer(response)
    else:
        await message.answer("Пожалуйста, войдите в систему для использования этой команды.")

@router.message(Command(commands=["reservebook"]))
async def cmd_reserve_book(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        await message.answer("Введите ID книги для бронирования:")
        await state.set_state(ReserveBook.waiting_for_book_id)
    else:
        await message.answer("Пожалуйста, войдите в систему для использования этой команды.")

@router.message(ReserveBook.waiting_for_book_id)
async def book_id_to_reserve_entered(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    book_id = message.text
    result = reserve_book(book_id, user_id)
    if result == "Вы уже забронировали эту книгу.":
        await message.answer(result)
    elif result:
        reservation_id, loan_id, return_date = result
        await message.answer(f"Книга успешно забронирована. Вам необходимо вернуть книгу до {return_date}.")
    else:
        await message.answer("Не удалось забронировать книгу.")
    await state.set_state(None)

@router.message(Command(commands=["myreservations"]))
async def cmd_my_reservations(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        user_id = user_data.get("user_id")
        reservations = get_user_reservations(user_id)
        if reservations:
            response = "\n".join([f"Бронирование ID: {res['reservation_id']} Книга: {res['book_name']} Дата: {res['reservation_date']}" for res in reservations])
        else:
            response = "У вас нет текущих бронирований."
        await message.answer(response)
    else:
        await message.answer("Пожалуйста, войдите в систему для использования этой команды.")



# Функция для регистрации всех обработчиков
def register_handlers(dp: Dispatcher):
    dp.include_router(router)