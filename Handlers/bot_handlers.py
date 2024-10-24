from aiogram import types, Router, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from Configuration.localization import MESSAGES
from DatabaseInteractions.book_catalog import search_books, get_book_details, get_available_books, reserve_book, get_user_reservations
from DatabaseInteractions.user_management import register_user, log_in_user


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
    await message.answer(MESSAGES["start"])

@router.message(Command(commands=["register"]))
async def cmd_register(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        await message.answer(MESSAGES["already_registered"])
    else:
        await ask_question(message, state, MESSAGES["enter_name"], Registration.waiting_for_name)

@router.message(Registration.waiting_for_name)
async def name_entered(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await ask_question(message, state, MESSAGES["enter_contact_data"], Registration.waiting_for_contact_data)

@router.message(Registration.waiting_for_contact_data)
async def contact_data_entered(message: types.Message, state: FSMContext):
    await state.update_data(contact_data=message.text)
    await ask_question(message, state, MESSAGES["enter_reader_number"], Registration.waiting_for_reader_number)

@router.message(Registration.waiting_for_reader_number)
async def reader_number_entered(message: types.Message, state: FSMContext):
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
async def cmd_login(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in") or user_data.get("staff_logged_in"):
        await message.answer(MESSAGES["already_logged_in"])
    else:
        await ask_question(message, state, MESSAGES["enter_name"], Login.waiting_for_name)

@router.message(Login.waiting_for_name)
async def login_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await ask_question(message, state, MESSAGES["enter_reader_number"], Login.waiting_for_reader_number)

@router.message(Login.waiting_for_reader_number)
async def login_reader_number_entered(message: types.Message, state: FSMContext):
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
        await ask_question(message, state, MESSAGES["user_logged_in"].format(name=name), UserLoggedIn.active)
    else:
        await message.answer(MESSAGES["login_failed"])
        await state.set_state(None)

@router.message(Command(commands=["search"]))
async def cmd_search(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in") or user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_search_query"], BookSearch.waiting_for_query)
    else:
        await message.answer(MESSAGES["login_required"])

@router.message(BookSearch.waiting_for_query)
async def search_query_entered(message: types.Message, state: FSMContext):
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
    await ask_question(message, state, MESSAGES["enter_book_id"], BookDetails.waiting_for_book_id)

@router.message(BookDetails.waiting_for_book_id)
async def book_id_entered(message: types.Message, state: FSMContext):
    try:
        book_id = int(message.text)
    except ValueError:
        await message.answer(MESSAGES["invalid_book_id"])
        return
    details = get_book_details(book_id)
    if details:
        response = f"{MESSAGES['book_title']}: {details['name']}\n{MESSAGES['author']}: {details['author']}\nISBN: {details['ISBN']}\n{MESSAGES['genre']}: {details['genre']}\n{MESSAGES['copies']}: {details['copies']}"
    else:
        response = MESSAGES["book_not_found"]
    await message.answer(response)
    await state.set_state(None)

@router.message(Command(commands=["exit"]))
async def cmd_exit(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(MESSAGES["logged_out"])

@router.message(Command(commands=["availablebooks"]))
async def cmd_available_books(message: types.Message, state: FSMContext):
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
async def cmd_reserve_book(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in"):
        await ask_question(message, state, MESSAGES["enter_book_id_for_reservation"], ReserveBook.waiting_for_book_id)
    else:
        await message.answer(MESSAGES["login_required"])

@router.message(ReserveBook.waiting_for_book_id)
async def book_id_to_reserve_entered(message: types.Message, state: FSMContext):
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
async def cmd_my_reservations(message: types.Message, state: FSMContext):
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

async def ask_question(message: types.Message, state: FSMContext, question: str, state_name: State):
    await state.set_state(None)
    await message.answer(question)
    await state.set_state(state_name)

# Do not delete, here we connect methods to the rout.
# We cannot do that earlier because smth was not completed yet
import Handlers.library_handlers
import Handlers.staff_handlers
import Handlers.reservations_handlers

# Функция для регистрации всех обработчиков
def register_handlers(dp: Dispatcher):
    dp.include_router(router)

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