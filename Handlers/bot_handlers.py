from aiogram import types, Router, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from Configuration.localization import MESSAGES
from DatabaseInteractions.book_catalog import search_books, get_book_details, get_available_books, reserve_book, get_user_reservations
from DatabaseInteractions.user_management import register_user, log_in_user



class UserRegistrationStates(StatesGroup):
    waiting_for_user_name = State()
    waiting_for_contact_info = State()
    waiting_for_reader_number = State()



class UserLoginStates(StatesGroup):
    waiting_for_user_name = State()
    waiting_for_reader_number = State()

class BookSearchStates(StatesGroup):
    waiting_for_search_query = State()

class BookDetailsStates(StatesGroup):
    waiting_for_book_id = State()

class UserSessionState(StatesGroup):
    active_session = State()

class BookReservationStates(StatesGroup):
    waiting_for_book_id = State()

router = Router()

@router.message(Command(commands=["start"]))
async def async_handle_start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(MESSAGES["start"])

@router.message(Command(commands=["register"]))
async def async_handle_register_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        await message.answer(MESSAGES["already_registered"])
    else:
        await async_ask_question(message, state, MESSAGES["enter_name"], UserRegistrationStates.waiting_for_user_name)

@router.message(UserRegistrationStates.waiting_for_user_name)
async def async_handle_user_name_input(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await async_ask_question(message, state, MESSAGES["enter_contact_data"], UserRegistrationStates.waiting_for_contact_info)

@router.message(UserRegistrationStates.waiting_for_contact_info)
async def async_handle_contact_info_input(message: types.Message, state: FSMContext):
    await state.update_data(contact_data=message.text)
    await async_ask_question(message, state, MESSAGES["enter_reader_number"], UserRegistrationStates.waiting_for_reader_number)

@router.message(UserRegistrationStates.waiting_for_reader_number)
async def async_handle_reader_number_input(message: types.Message, state: FSMContext):
    await state.update_data(reader_number=message.text)
    data = await state.get_data()
    registration_result = register_user(data['name'], data['contact_data'], data['reader_number'])

    if registration_result == MESSAGES["already_registered"]:
        await message.answer(registration_result)
        await message.answer(MESSAGES["try_again"])
        await state.set_state(None)
    else:
        await message.answer(MESSAGES["registration_success"])
        await state.set_state(None)

@router.message(Command(commands=["login"]))
async def async_handle_login_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in") or user_data.get("staff_logged_in"):
        await message.answer(MESSAGES["already_logged_in"])
    else:
        await async_ask_question(message, state, MESSAGES["enter_name"], UserLoginStates.waiting_for_user_name)

@router.message(UserLoginStates.waiting_for_user_name)
async def async_handle_login_name_input(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await async_ask_question(message, state, MESSAGES["enter_reader_number"], UserLoginStates.waiting_for_reader_number)

@router.message(UserLoginStates.waiting_for_reader_number)
async def async_handle_login_reader_number_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    reader_number = message.text

    (valid_data, error) = validate_login(name, reader_number)
    if error:
        await message.answer(error)
        return

    reader_id = log_in_user(valid_data[0], valid_data[1])
    if reader_id:
        await state.update_data(logged_in=True, reader_id=reader_id)
        await async_ask_question(message, state, MESSAGES["user_logged_in"].format(name=name), UserSessionState.active_session)
    else:
        await message.answer(MESSAGES["login_failed"])
        await state.set_state(None)

@router.message(Command(commands=["search"]))
async def async_handle_search_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in") or user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_search_query"], BookSearchStates.waiting_for_search_query)
    else:
        await message.answer(MESSAGES["login_required"])

@router.message(BookSearchStates.waiting_for_search_query)
async def async_handle_search_query_input(message: types.Message, state: FSMContext):
    query = message.text
    results = search_books(query)
    if results:
        response = "\n".join([f"ID: {book['book_id']}, {MESSAGES['book_title']}: {book['name']}, {MESSAGES['author']}: {book['author']}" for book in results])
    else:
        response = MESSAGES["no_books_found"]
    await message.answer(response)
    await state.set_state(None)

@router.message(Command(commands=["bookdetails"]))
async def cmd_book_details(message: types.Message, state: FSMContext):
    await async_ask_question(message, state, "Введите ID книги для получения деталей:", BookDetailsStates.waiting_for_book_id)

@router.message(BookDetailsStates.waiting_for_book_id)
async def book_id_entered(message: types.Message, state: FSMContext):
    try:
        book_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID книги (число).")
        return
    details = get_book_details(book_id)
    if details:
        # Формирование ответа с деталями книги
        response = f"Название: {details['name']}\nАвтор: {details['author']}\nISBN: {details['ISBN']}\nЖанр: {details['genre']}\nКоличество: {details['copies']}"
    else:
        response = "Книга с таким ID не найдена."
    await message.answer(response)
    await state.set_state(None)

@router.message(Command(commands=["exit"]))
async def async_handle_exit_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(MESSAGES["logged_out"])

@router.message(Command(commands=["availablebooks"]))
async def async_handle_available_books_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in") or user_data.get("staff_logged_in"):
        books = get_available_books()
        if books:
            response = "\n".join([f"ID: {book['book_id']}, {MESSAGES['author']}: {book['author']}, {MESSAGES['book_title']}: {book['name']}" for book in books])
        else:
            response = MESSAGES["no_available_books"]
        await message.answer(response)
    else:
        await message.answer(MESSAGES["login_required"])

@router.message(Command(commands=["reservebook"]))
async def async_handle_reserve_book_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_book_id_for_reservation"], BookReservationStates.waiting_for_book_id)
    else:
        await message.answer(MESSAGES["login_required"])

@router.message(BookReservationStates.waiting_for_book_id)
async def async_handle_book_id_for_reservation_input(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    reader_id = user_data.get("reader_id")

    book_id, error = validate_book_id(message.text)
    if error:
        await message.answer(error)
        return

    result = reserve_book(book_id, reader_id)
    if isinstance(result, str):
        await message.answer(result)
    elif result:
        reservation_id, loan_id, return_date = result
        await message.answer(MESSAGES["book_reserved_successfully"].format(return_date=return_date))
    else:
        await message.answer(MESSAGES["reservation_failed"])
    await state.set_state(None)

@router.message(Command(commands=["myreservations"]))
async def async_handle_my_reservations_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        reader_id = user_data.get("reader_id")
        reservations = get_user_reservations(reader_id)
        if reservations:
            response = "\n".join([f"Бронирование ID: {res['reservation_id']}, {MESSAGES['book_title']}: {res['book_name']}, {MESSAGES['date']}: {res['reservation_date']}" for res in reservations])
        else:
            response = MESSAGES["no_active_reservations"]
        await message.answer(response)
    else:
        await message.answer(MESSAGES["login_required"])

async def async_ask_question(message: types.Message, state: FSMContext, question: str, next_state: State):
    await state.set_state(None)
    await message.answer(question)
    await state.set_state(next_state)

# Do not delete, here we connect methods to the rout.
# We cannot do that earlier because smth was not completed yet
import Handlers.library_handlers
import Handlers.staff_handlers
import Handlers.reservations_handlers

# Функция для регистрации всех обработчиков
def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)

def validate_book_id(book_id: str):
    try:
        return int(book_id), None
    except ValueError:
        return None, MESSAGES["invalid_book_id"]

def validate_user_input(data: str, field_name: str):
    if len(data.strip()) < 2:
        return None, MESSAGES["min_length_error"].format(field_name=field_name)
    return data, None

def validate_login(name: str, reader_number: str):
    name_valid, error = validate_user_input(name, MESSAGES["username"])
    if error:
        return None, error

    if len(reader_number) < 2:
        return None, MESSAGES["invalid_reader_number"]

    return (name_valid, reader_number), None