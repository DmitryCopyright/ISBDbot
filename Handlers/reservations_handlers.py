from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from DatabaseInteractions.admin_user_interaction import delete_user_reservation
from DatabaseInteractions.book_catalog import get_user_reservations
from Handlers.bot_handlers import router, ask_question
from Handlers.library_handlers import validate_int_input


class DeleteReservation(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_reservation_id = State()

# Command to initiate the process of deleting a user reservation
@router.message(Command(commands=["deletereservation"]))
async def cmd_delete_reservation(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    # Check if a staff member is logged in
    if user_data.get("staff_logged_in"):
        await ask_question(message, state, "Введите ID пользователя:", DeleteReservation.waiting_for_user_id)
    else:
        await message.answer("Пожалуйста, войдите в систему как персонал для использования этой команды.")

# Function to handle the entered user ID for reservation deletion
@router.message(DeleteReservation.waiting_for_user_id)
async def delete_reservation_user_id_entered(message: types.Message, state: FSMContext):
    user_id, error = validate_int_input(message.text, "ID пользователя")

    if error:
        await message.answer(error)
        return

    reservations = get_user_reservations(user_id)
    if reservations:
        response = "\n".join([f"Резервирование ID: {res['reservation_id']} Книга: {res['book_name']} Дата: {res['reservation_date']}" for res in reservations])
        await message.answer(response)
        await ask_question(message, state, "Введите ID резервирования, которое вы хотите удалить:",
                           DeleteReservation.waiting_for_reservation_id)
    else:
        await message.answer("У пользователя нет текущих резервирований.")
        await state.set_state(None)

# Function to handle the entered reservation ID for deletion
@router.message(DeleteReservation.waiting_for_reservation_id)
async def delete_reservation_id_entered(message: types.Message, state: FSMContext):
    reservation_id, error = validate_int_input(message.text, "ID резервирования")

    if error:
        await message.answer(error)
        return

    result = delete_user_reservation(reservation_id)
    await message.answer(f"Резервирование с ID {reservation_id} успешно удалено.")
    await state.set_state(None)
