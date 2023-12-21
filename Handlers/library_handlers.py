from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from DatabaseInteractions.admin_database_updates import delete_book, change_copies, add_book, delete_genre, add_genre, add_department, \
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


# region Add Book
@router.message(Command(commands=["addbook"]))
async def cmd_add_book(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите название книги:", AddBook.waiting_for_name)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


@router.message(AddBook.waiting_for_name)
async def book_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await ask_question(message, state, "Введите ISBN книги:", AddBook.waiting_for_ISBN)


@router.message(AddBook.waiting_for_ISBN)
async def book_ISBN_entered(message: types.Message, state: FSMContext):
    await state.update_data(ISBN=message.text)
    await ask_question(message, state, "Введите ID автора книги:", AddBook.waiting_for_author_id)


@router.message(AddBook.waiting_for_author_id)
async def author_id_entered(message: types.Message, state: FSMContext):
    try:
        author_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID автора (число).")
        return

    await state.update_data(author_id=author_id)
    await ask_question(message, state, "Введите ID издателя книги:", AddBook.waiting_for_publisher_id)


@router.message(AddBook.waiting_for_publisher_id)
async def publisher_id_entered(message: types.Message, state: FSMContext):
    try:
        publisher_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID издателя (число).")
        return

    await state.update_data(publisher_id=publisher_id)
    await ask_question(message, state, "Введите ID жанра книги:", AddBook.waiting_for_genre_id)


@router.message(AddBook.waiting_for_genre_id)
async def genre_id_entered(message: types.Message, state: FSMContext):
    try:
        genre_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID жанра (число).")
        return

    await state.update_data(genre_id=genre_id)
    await ask_question(message, state, "Введите ID отдела библиотеки для книги:", AddBook.waiting_for_department_id)


@router.message(AddBook.waiting_for_department_id)
async def department_id_entered(message: types.Message, state: FSMContext):
    try:
        department_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID отдела (число).")
        return

    await state.update_data(department_id=department_id)
    await ask_question(message, state, "Введите количество копий книги:", AddBook.waiting_for_copies)


@router.message(AddBook.waiting_for_copies)
async def copies_entered(message: types.Message, state: FSMContext):
    try:
        copies = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество копий (число).")
        return

    data = await state.get_data()
    result = add_book(data['name'], data['ISBN'], data['author_id'], data['publisher_id'], data['genre_id'],
                      data['department_id'], copies)

    if isinstance(result, int):
        await message.answer(f"Книга {data['name']} успешно добавлена")
    else:
        await message.answer(result)

    await state.set_state(None)


# endregion

# region update amount
# Command for changing the number of copies of a book
@router.message(Command(commands=["changecopies"]))
async def cmd_change_copies(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    # Check if a staff member is logged in
    if user_data.get("staff_logged_in"):
        # Staff member is logged in, proceed with adding a book
        await ask_question(message, state, "Введите ID книги, у которой нужно изменить количество копий:",
                           AmountUpdate.waiting_for_book_id)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


# Function to handle the entered book ID for changing copies
@router.message(AmountUpdate.waiting_for_book_id)
async def change_copies_book_id_entered(message: types.Message, state: FSMContext):
    try:
        book_id = int(message.text)
    except ValueError:
        await ask_question(message, state, "Пожалуйста, введите корректный ID книги (число).",
                           AmountUpdate.waiting_for_book_id)
        return

    await state.update_data(book_id=book_id)
    await ask_question(message, state, "Введите новое количество копий:", AmountUpdate.waiting_for_new_copies)


# Function to handle the entered new copies value
@router.message(AmountUpdate.waiting_for_new_copies)
async def change_copies_new_copies_entered(message: types.Message, state: FSMContext):
    try:
        new_copies = int(message.text)
    except ValueError:
        await ask_question(message, state, "Пожалуйста, введите корректное количество копий (число).",
                           AmountUpdate.waiting_for_new_copies)
        return

    data = await state.get_data()
    book_id = data['book_id']
    result = change_copies(book_id, new_copies)

    if result:
        await message.answer(f"Количество копий книги с ID {book_id} успешно изменено на {new_copies}.")
    else:
        await message.answer(f"Не удалось изменить количество копий книги с ID {book_id}.")

    await state.set_state(None)


# endregion

# region delete books
# Command for deleting a book
@router.message(Command(commands=["deletebook"]))
async def cmd_delete_book(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    # Check if a staff member is logged in
    if user_data.get("staff_logged_in"):
        # Staff member is logged in, proceed with adding a book
        await ask_question(message, state, "Введите ID книги, которую нужно удалить:", DeleteBook.waiting_for_book_id)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


# Function to handle the entered book ID for deletion
@router.message(DeleteBook.waiting_for_book_id)
async def delete_book_id_entered(message: types.Message, state: FSMContext):
    try:
        book_id = int(message.text)
    except ValueError:
        await ask_question(message, state, "Пожалуйста, введите корректный ID книги (число).",
                           DeleteBook.waiting_for_book_id)
        return

    result = delete_book(book_id)

    await message.answer(f"Книга с ID {book_id} успешно удалена.")
    await state.set_state(None)


# endregion

# region genres management
# Command for adding a new genre
@router.message(Command(commands=["addgenre"]))
async def cmd_add_genre(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите название нового жанра:", AddGenre.waiting_for_genre_name)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


# Function to handle the entered genre name
@router.message(AddGenre.waiting_for_genre_name)
async def add_genre_name_entered(message: types.Message, state: FSMContext):
    genre_name = message.text
    result = add_genre(genre_name)

    if result:
        await message.answer(f"Жанр '{genre_name}' успешно добавлен с ID {result}.")
    else:
        await message.answer(f"Не удалось добавить жанр '{genre_name}'.")

    await state.set_state(None)


# Command for deleting a genre
@router.message(Command(commands=["deletegenre"]))
async def cmd_delete_genre(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите ID жанра, который нужно удалить:", DeleteGenre.waiting_for_genre_id)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")



# Function to handle the entered genre ID for deletion
@router.message(DeleteGenre.waiting_for_genre_id)
async def delete_genre_id_entered(message: types.Message, state: FSMContext):
    try:
        genre_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID жанра (число).")
        return

    result = delete_genre(genre_id)

    await message.answer(f"Жанр с ID {genre_id} успешно удален.")
    await state.set_state(None)
# endregion

# region authors
@router.message(Command(commands=["addauthor"]))
async def cmd_add_author(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите ФИО автора:", AddAuthor.waiting_for_author_id)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


@router.message(AddAuthor.waiting_for_author_id)
async def add_author_name_entered(message: types.Message, state: FSMContext):
    author_name = message.text
    result = add_author(author_name)

    if isinstance(result, int):
        await message.answer(f"Автор с ID {result} успешно добавлен!")
    else:
        await message.answer(result)

    await state.set_state(None)


@router.message(Command(commands=["deleteauthor"]))
async def cmd_delete_author(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите ID автора, которого нужно удалить:", DeleteAuthor.waiting_for_author_id)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


@router.message(DeleteAuthor.waiting_for_author_id)
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

# region publishers
@router.message(Command(commands=["addpublisher"]))
async def cmd_add_publisher(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите название издателя:", AddPublisher.waiting_for_publisher_name)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


# Function to handle the entered publisher name
@router.message(AddPublisher.waiting_for_publisher_name)
async def add_publisher_name_entered(message: types.Message, state: FSMContext):
    publisher_name = message.text
    result = add_publisher(publisher_name)

    if isinstance(result, int):
        await message.answer(f"Издатель с ID {result} успешно добавлен!")
    else:
        await message.answer(result)

    await state.set_state(None)


# Command for deleting a publisher
@router.message(Command(commands=["deletepublisher"]))
async def cmd_delete_publisher(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите ID издателя, который нужно удалить:",
                           DeletePublishers.waiting_for_publisher_id)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")



# Function to handle the entered publisher ID for deletion
@router.message(DeletePublishers.waiting_for_publisher_id)
async def delete_publisher_id_entered(message: types.Message, state: FSMContext):
    try:
        publisher_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID издателя (число).")
        return

    result = delete_publisher(publisher_id)
    await message.answer(f"Издатель с ID {publisher_id} успешно удален.")
    await state.set_state(None)


# endregion

# region departments
# Function to initiate the process of adding a department
@router.message(Command(commands=["adddepartment"]))
async def cmd_add_department(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите название отдела:", AddDepartment.waiting_for_department_name)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


# Function to handle the entered department name
@router.message(AddDepartment.waiting_for_department_name)
async def add_department_name_entered(message: types.Message, state: FSMContext):
    department_name = message.text
    result = add_department(department_name)

    if isinstance(result, int):
        await message.answer(f"Отдел с ID {result} успешно добавлен!")
    else:
        await message.answer(result)

    await state.set_state(None)


# Command for deleting a department
@router.message(Command(commands=["deletedepartment"]))
async def cmd_delete_department(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите ID отдела, который нужно удалить:",
                           DeleteDepartments.waiting_for_department_id)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")


# Function to handle the entered department ID for deletion
@router.message(DeleteDepartments.waiting_for_department_id)
async def delete_department_id_entered(message: types.Message, state: FSMContext):
    try:
        department_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID отдела (число).")
        return

    result = delete_department(department_id)
    await message.answer(f"Отдел с ID {department_id} успешно удален.")
    await state.set_state(None)
# endregion

# endregion
