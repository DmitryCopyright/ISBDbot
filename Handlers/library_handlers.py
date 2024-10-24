from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from Configuration.db_operations import *
from Configuration.localization import MESSAGES
from DatabaseInteractions.admin_database_updates import delete_book, change_copies, add_book, add_genre, add_department, \
    add_publisher, add_author, delete_author, delete_department, delete_publisher
from Handlers.bot_handlers import router, ask_question


# region admin tools
class AddBook(StatesGroup):
    waiting_for_name = State()
    waiting_for_ISBN = State()
    waiting_for_author_id = State()
    waiting_for_publisher_id = State()
    waiting_for_genre_id = State()
    waiting_for_department_id = State()
    waiting_for_copies = State()


class AmountUpdate(StatesGroup):
    waiting_for_book_id = State()
    waiting_for_new_copies = State()


class DeleteBook(StatesGroup):
    waiting_for_book_id = State()


class AddGenre(StatesGroup):
    waiting_for_genre_name = State()


class DeleteGenre(StatesGroup):
    waiting_for_genre_id = State()


class AddAuthor(StatesGroup):
    waiting_for_author_id = State()


class DeleteAuthor(StatesGroup):
    waiting_for_author_id = State()


class AddPublisher(StatesGroup):
    waiting_for_publisher_name = State()


class DeletePublishers(StatesGroup):
    waiting_for_publisher_id = State()


class AddDepartment(StatesGroup):
    waiting_for_department_name = State()


class DeleteDepartments(StatesGroup):
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
async def cmd_add_book(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_book_name"], AddBook.waiting_for_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AddBook.waiting_for_name)
async def book_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await ask_question(message, state, MESSAGES["enter_ISBN"], AddBook.waiting_for_ISBN)


@router.message(AddBook.waiting_for_ISBN)
async def book_ISBN_entered(message: types.Message, state: FSMContext):
    await state.update_data(ISBN=message.text)
    await ask_question(message, state, MESSAGES["enter_author_id"], AddBook.waiting_for_author_id)


@router.message(AddBook.waiting_for_author_id)
@handle_db_errors
async def author_id_entered(message: types.Message, state: FSMContext):
    author_id, error = validate_int_input(message.text, MESSAGES["author_id"])
    if error:
        await message.answer(error)
        return

    await state.update_data(author_id=author_id)
    await ask_question(message, state, MESSAGES["enter_publisher_id"], AddBook.waiting_for_publisher_id)


@router.message(AddBook.waiting_for_publisher_id)
@handle_db_errors
async def publisher_id_entered(message: types.Message, state: FSMContext):
    publisher_id, error = validate_int_input(message.text, MESSAGES["publisher_id"])
    if error:
        await message.answer(error)
        return

    await state.update_data(publisher_id=publisher_id)
    await ask_question(message, state, MESSAGES["enter_genre_id"], AddBook.waiting_for_genre_id)


@router.message(AddBook.waiting_for_genre_id)
@handle_db_errors
async def genre_id_entered(message: types.Message, state: FSMContext):
    genre_id, error = validate_int_input(message.text, MESSAGES["genre_id"])
    if error:
        await message.answer(error)
        return

    await state.update_data(genre_id=genre_id)
    await ask_question(message, state, MESSAGES["enter_department_id"], AddBook.waiting_for_department_id)


@router.message(AddBook.waiting_for_department_id)
@handle_db_errors
async def department_id_entered(message: types.Message, state: FSMContext):
    department_id, error = validate_int_input(message.text, MESSAGES["department_id"])
    if error:
        await message.answer(error)
        return

    await state.update_data(department_id=department_id)
    await ask_question(message, state, MESSAGES["enter_copies"], AddBook.waiting_for_copies)


@router.message(AddBook.waiting_for_copies)
@handle_db_errors
async def copies_entered(message: types.Message, state: FSMContext):
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

# region update amount
@router.message(Command(commands=["changecopies"]))
async def cmd_change_copies(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_book_id"], AmountUpdate.waiting_for_book_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AmountUpdate.waiting_for_book_id)
async def change_copies_book_id_entered(message: types.Message, state: FSMContext):
    book_id, error = validate_int_input(message.text, MESSAGES["book_id"])
    if error:
        await ask_question(message, state, error, AmountUpdate.waiting_for_book_id)
        return

    await state.update_data(book_id=book_id)
    await ask_question(message, state, MESSAGES["enter_new_copies"], AmountUpdate.waiting_for_new_copies)


@router.message(AmountUpdate.waiting_for_new_copies)
async def change_copies_new_copies_entered(message: types.Message, state: FSMContext):
    new_copies, error = validate_int_input(message.text, MESSAGES["copies"])
    if error:
        await ask_question(message, state, error, AmountUpdate.waiting_for_new_copies)
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

# region delete books
@router.message(Command(commands=["deletebook"]))
async def cmd_delete_book(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_book_id_to_delete"], DeleteBook.waiting_for_book_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(DeleteBook.waiting_for_book_id)
@handle_db_errors
async def delete_book_id_entered(message: types.Message, state: FSMContext):
    book_id, error = validate_int_input(message.text, MESSAGES["book_id"])
    if error:
        await ask_question(message, state, error, DeleteBook.waiting_for_book_id)
        return

    result = delete_book(book_id)
    await message.answer(MESSAGES["book_deleted_successfully"].format(book_id=book_id))
    await state.set_state(None)


# endregion

# region genres management
# Command for adding a new genre
@router.message(Command(commands=["addgenre"]))
async def cmd_add_genre(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_genre_name"], AddGenre.waiting_for_genre_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])

@router.message(AddGenre.waiting_for_genre_name)
async def add_genre_name_entered(message: types.Message, state: FSMContext):
    genre_name = message.text
    result = add_genre(genre_name)

    if result:
        await message.answer(MESSAGES["genre_added_successfully"].format(genre_name=genre_name, genre_id=result))
    else:
        await message.answer(MESSAGES["genre_add_failed"].format(genre_name=genre_name))

    await state.set_state(None)

@router.message(Command(commands=["deletegenre"]))
async def cmd_delete_genre(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_genre_id_to_delete"], DeleteGenre.waiting_for_genre_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(DeleteAuthor.waiting_for_author_id)
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
async def cmd_add_author(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_author_name"], AddAuthor.waiting_for_author_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(AddAuthor.waiting_for_author_id)
async def add_author_name_entered(message: types.Message, state: FSMContext):
    author_name = message.text
    result = add_author(author_name)

    if isinstance(result, int):
        await message.answer(MESSAGES["author_added_successfully"].format(author_name=author_name, author_id=result))
    else:
        await message.answer(result)

    await state.set_state(None)


@router.message(Command(commands=["deleteauthor"]))
async def cmd_delete_author(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_author_id_to_delete"], DeleteAuthor.waiting_for_author_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])


@router.message(DeleteAuthor.waiting_for_author_id)
async def delete_author_id_entered(message: types.Message, state: FSMContext):
    try:
        author_id = int(message.text)
    except ValueError:
        await message.answer(MESSAGES["invalid_author_id"])
        return

    result = delete_author(author_id)
    await message.answer(MESSAGES["author_deleted_successfully"].format(author_id=author_id))
    await state.set_state(None)

# endregion

# region publishers
@router.message(Command(commands=["addpublisher"]))
async def cmd_add_publisher(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_publisher_name"], AddPublisher.waiting_for_publisher_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])

@router.message(AddPublisher.waiting_for_publisher_name)
async def add_publisher_name_entered(message: types.Message, state: FSMContext):
    publisher_name = message.text
    result = add_publisher(publisher_name)

    if isinstance(result, int):
        await message.answer(MESSAGES["publisher_added_successfully"].format(publisher_name=publisher_name, publisher_id=result))
    else:
        await message.answer(result)

    await state.set_state(None)

@router.message(Command(commands=["deletepublisher"]))
async def cmd_delete_publisher(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_publisher_id_to_delete"], DeletePublishers.waiting_for_publisher_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])

@router.message(DeletePublishers.waiting_for_publisher_id)
@handle_db_errors
async def delete_publisher_id_entered(message: types.Message, state: FSMContext):
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
async def cmd_add_department(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_department_name"], AddDepartment.waiting_for_department_name)
    else:
        await message.answer(MESSAGES["staff_login_required"])

@router.message(AddDepartment.waiting_for_department_name)
async def add_department_name_entered(message: types.Message, state: FSMContext):
    department_name = message.text
    result = add_department(department_name)

    if isinstance(result, int):
        await message.answer(MESSAGES["department_added_successfully"].format(department_name=department_name, department_id=result))
    else:
        await message.answer(result)

    await state.set_state(None)

@router.message(Command(commands=["deletedepartment"]))
async def cmd_delete_department(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, MESSAGES["enter_department_id_to_delete"], DeleteDepartments.waiting_for_department_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])

@router.message(DeleteDepartments.waiting_for_department_id)
@handle_db_errors
async def delete_department_id_entered(message: types.Message, state: FSMContext):
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
