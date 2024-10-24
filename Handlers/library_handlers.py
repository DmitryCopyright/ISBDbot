from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from Configuration.db_operations import *
from Configuration.localization import MESSAGES
from DatabaseInteractions.admin_database_updates import delete_book, change_copies, add_book, add_genre, add_department, \
    add_publisher, add_author, delete_author, delete_department, delete_publisher
from Handlers.bot_handlers import router, async_ask_question


# region admin tools
class AddBookStates(StatesGroup):
    waiting_for_book_name = State()
    waiting_for_ISBN = State()
    waiting_for_author_id = State()
    waiting_for_publisher_id = State()
    waiting_for_genre_id = State()
    waiting_for_department_id = State()
    waiting_for_copies = State()


class AmountUpdateStates(StatesGroup):
    waiting_for_book_id = State()
    waiting_for_new_copies = State()


class DeleteBookStates(StatesGroup):
    waiting_for_book_id = State()


class AddGenreStates(StatesGroup):
    waiting_for_genre_name = State()


class DeleteGenreStates(StatesGroup):
    waiting_for_genre_id = State()


class AddAuthorStates(StatesGroup):
    waiting_for_author_name = State()


class DeleteAuthorStates(StatesGroup):
    waiting_for_author_id = State()


class AddPublisherStates(StatesGroup):
    waiting_for_publisher_name = State()


class DeletePublisherStates(StatesGroup):
    waiting_for_publisher_id = State()


class AddDepartmentStates(StatesGroup):
    waiting_for_department_name = State()


class DeleteDepartmentStates(StatesGroup):
    waiting_for_department_id = State()


def validate_int_input(input_data: str, field_name: str):
    """
    Валидация ввода данных для целочисленных значений.
    Возвращает кортеж (значение, None) в случае успеха или (None, сообщение об ошибке).
    """
    try:
        return int(input_data), None
    except ValueError:
        return None, MESSAGES["invalid_input"].format(field_name=field_name)


def validate_str_input(input_data: str, field_name: str):
    """
    Валидация строкового ввода.
    Возвращает кортеж (значение, None) в случае успеха или (None, сообщение об ошибке).
    """
    if len(input_data.strip()) == 0:
        return None, MESSAGES["empty_field"].format(field_name=field_name)
    return input_data.strip(), None


# region Add Book

@router.message(Command(commands=["addbook"]))
async def async_handle_add_book_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_book_name"], AddBookStates.waiting_for_book_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AddBookStates.waiting_for_book_name)
async def async_handle_book_name_input(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await async_ask_question(message, state, MESSAGES["enter_ISBN"], AddBookStates.waiting_for_ISBN)


@router.message(AddBookStates.waiting_for_ISBN)
async def async_handle_book_ISBN_input(message: types.Message, state: FSMContext):
    await state.update_data(ISBN=message.text)
    await async_ask_question(message, state, MESSAGES["enter_author_id"], AddBookStates.waiting_for_author_id)


@router.message(AddBookStates.waiting_for_author_id)
@handle_db_errors
async def async_handle_author_id_input(message: types.Message, state: FSMContext):
    author_id, error = validate_int_input(message.text, MESSAGES["author_id"])
    if error:
        await message.answer(error)
        return

    await state.update_data(author_id=author_id)
    await async_ask_question(message, state, MESSAGES["enter_publisher_id"], AddBookStates.waiting_for_publisher_id)


@router.message(AddBookStates.waiting_for_publisher_id)
@handle_db_errors
async def async_handle_publisher_id_input(message: types.Message, state: FSMContext):
    publisher_id, error = validate_int_input(message.text, MESSAGES["publisher_id"])
    if error:
        await message.answer(error)
        return

    await state.update_data(publisher_id=publisher_id)
    await async_ask_question(message, state, MESSAGES["enter_genre_id"], AddBookStates.waiting_for_genre_id)


@router.message(AddBookStates.waiting_for_genre_id)
@handle_db_errors
async def async_handle_genre_id_input(message: types.Message, state: FSMContext):
    genre_id, error = validate_int_input(message.text, MESSAGES["genre_id"])
    if error:
        await message.answer(error)
        return

    await state.update_data(genre_id=genre_id)
    await async_ask_question(message, state, MESSAGES["enter_department_id"], AddBookStates.waiting_for_department_id)


@router.message(AddBookStates.waiting_for_department_id)
@handle_db_errors
async def async_handle_department_id_input(message: types.Message, state: FSMContext):
    department_id, error = validate_int_input(message.text, MESSAGES["department_id"])
    if error:
        await message.answer(error)
        return

    await state.update_data(department_id=department_id)
    await async_ask_question(message, state, MESSAGES["enter_copies"], AddBookStates.waiting_for_copies)


@router.message(AddBookStates.waiting_for_copies)
@handle_db_errors
async def async_handle_copies_input(message: types.Message, state: FSMContext):
    copies, error = validate_int_input(message.text, MESSAGES["copies"])
    if error:
        await message.answer(error)
        return

    data = await state.get_data()
    result = add_book(data['name'], data['ISBN'], data['author_id'], data['publisher_id'], data['genre_id'],
                      data['department_id'], copies)

    if isinstance(result, int):
        await message.answer(MESSAGES["book_added_successfully"].format(book_name=data['name']))
    else:
        await message.answer(result)

    await state.set_state(None)

# endregion

# region Update Amount

@router.message(Command(commands=["changecopies"]))
async def async_handle_change_copies_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_book_id"], AmountUpdateStates.waiting_for_book_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AmountUpdateStates.waiting_for_book_id)
async def async_handle_change_copies_book_id_input(message: types.Message, state: FSMContext):
    book_id, error = validate_int_input(message.text, MESSAGES["book_id"])
    if error:
        await async_ask_question(message, state, error, AmountUpdateStates.waiting_for_book_id)
        return

    await state.update_data(book_id=book_id)
    await async_ask_question(message, state, MESSAGES["enter_new_copies"], AmountUpdateStates.waiting_for_new_copies)


@router.message(AmountUpdateStates.waiting_for_new_copies)
async def async_handle_new_copies_input(message: types.Message, state: FSMContext):
    new_copies, error = validate_int_input(message.text, MESSAGES["copies"])
    if error:
        await async_ask_question(message, state, error, AmountUpdateStates.waiting_for_new_copies)
        return

    data = await state.get_data()
    book_id = data['book_id']
    result = change_copies(book_id, new_copies)

    if result:
        await message.answer(MESSAGES["copies_updated_successfully"].format(book_id=book_id, new_copies=new_copies))
    else:
        await message.answer(MESSAGES["copies_update_failed"].format(book_id=book_id))

    await state.set_state(None)

# endregion

# region Delete Book

@router.message(Command(commands=["deletebook"]))
async def async_handle_delete_book_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_book_id_to_delete"], DeleteBookStates.waiting_for_book_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(DeleteBookStates.waiting_for_book_id)
@handle_db_errors
async def async_handle_delete_book_id_input(message: types.Message, state: FSMContext):
    book_id, error = validate_int_input(message.text, MESSAGES["book_id"])
    if error:
        await async_ask_question(message, state, error, DeleteBookStates.waiting_for_book_id)
        return

    result = delete_book(book_id)
    await message.answer(MESSAGES["book_deleted_successfully"].format(book_id=book_id))
    await state.set_state(None)

# endregion

# region Genres Management

@router.message(Command(commands=["addgenre"]))
async def async_handle_add_genre_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_genre_name"], AddGenreStates.waiting_for_genre_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AddGenreStates.waiting_for_genre_name)
async def async_handle_genre_name_input(message: types.Message, state: FSMContext):
    genre_name = message.text
    result = add_genre(genre_name)

    if result:
        await message.answer(MESSAGES["genre_added_successfully"].format(genre_name=genre_name, genre_id=result))
    else:
        await message.answer(MESSAGES["genre_add_failed"].format(genre_name=genre_name))

    await state.set_state(None)


@router.message(Command(commands=["deletegenre"]))
async def async_handle_delete_genre_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_genre_id_to_delete"], DeleteGenreStates.waiting_for_genre_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])

@router.message(DeleteAuthorStates.waiting_for_author_id)
@handle_db_errors
async def delete_author_id_entered(message: types.Message, state: FSMContext):
    try:
        author_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID автора (число).")
        return

    result = delete_author(author_id)
    await message.answer(f"Автор с ID {author_id} успешно удален.")
    await state.set_state(None)
# endregion

# region authors
@router.message(Command(commands=["addauthor"]))
async def async_handle_add_author_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_author_name"], AddAuthorStates.waiting_for_author_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AddAuthorStates.waiting_for_author_name)
async def async_handle_author_name_input(message: types.Message, state: FSMContext):
    author_name = message.text
    result = add_author(author_name)

    if isinstance(result, int):
        await message.answer(MESSAGES["author_added_successfully"].format(author_name=author_name, author_id=result))
    else:
        await message.answer(result)

    await state.set_state(None)


@router.message(Command(commands=["deleteauthor"]))
async def async_handle_delete_author_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_author_id_to_delete"], DeleteAuthorStates.waiting_for_author_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(DeleteAuthorStates.waiting_for_author_id)
async def async_handle_author_id_input(message: types.Message, state: FSMContext):
    try:
        author_id = int(message.text)
    except ValueError:
        await message.answer(MESSAGES["invalid_author_id"])
        return

    result = delete_author(author_id)
    await message.answer(MESSAGES["author_deleted_successfully"].format(author_id=author_id))
    await state.set_state(None)

# endregion

# region Publishers Management

@router.message(Command(commands=["addpublisher"]))
async def async_handle_add_publisher_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_publisher_name"], AddPublisherStates.waiting_for_publisher_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AddPublisherStates.waiting_for_publisher_name)
async def async_handle_publisher_name_input(message: types.Message, state: FSMContext):
    publisher_name = message.text
    result = add_publisher(publisher_name)

    if isinstance(result, int):
        await message.answer(MESSAGES["publisher_added_successfully"].format(publisher_name=publisher_name, publisher_id=result))
    else:
        await message.answer(result)

    await state.set_state(None)


@router.message(Command(commands=["deletepublisher"]))
async def async_handle_delete_publisher_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_publisher_id_to_delete"], DeletePublisherStates.waiting_for_publisher_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(DeletePublisherStates.waiting_for_publisher_id)
@handle_db_errors
async def async_handle_publisher_id_input(message: types.Message, state: FSMContext):
    try:
        publisher_id = int(message.text)
    except ValueError:
        await message.answer(MESSAGES["invalid_publisher_id"])
        return

    result = delete_publisher(publisher_id)
    await message.answer(MESSAGES["publisher_deleted_successfully"].format(publisher_id=publisher_id))
    await state.set_state(None)



# endregion

# region departments
# Function to initiate the process of adding a department
@router.message(Command(commands=["adddepartment"]))
async def async_handle_add_department_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_department_name"], AddDepartmentStates.waiting_for_department_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AddDepartmentStates.waiting_for_department_name)
async def async_handle_department_name_input(message: types.Message, state: FSMContext):
    department_name = message.text
    result = add_department(department_name)

    if isinstance(result, int):
        await message.answer(MESSAGES["department_added_successfully"].format(department_name=department_name, department_id=result))
    else:
        await message.answer(result)

    await state.set_state(None)


@router.message(Command(commands=["deletedepartment"]))
async def async_handle_delete_department_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await async_ask_question(message, state, MESSAGES["enter_department_id_to_delete"], DeleteDepartmentStates.waiting_for_department_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(DeleteDepartmentStates.waiting_for_department_id)
@handle_db_errors
async def async_handle_department_id_input(message: types.Message, state: FSMContext):
    try:
        department_id = int(message.text)
    except ValueError:
        await message.answer(MESSAGES["invalid_department_id"])
        return

    result = delete_department(department_id)
    await message.answer(MESSAGES["department_deleted_successfully"].format(department_id=department_id))
    await state.set_state(None)
# endregion

# endregion
