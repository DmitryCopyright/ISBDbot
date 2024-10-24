from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from Configuration.localization import MESSAGES
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
        await ask_question(message, state, MESSAGES["enter_user_id"], DeleteReservation.waiting_for_user_id)
    else:
        await message.answer(MESSAGES["staff_login_required"])

# Function to handle the entered user ID for reservation deletion
@router.message(DeleteReservation.waiting_for_user_id)
async def delete_reservation_user_id_entered(message: types.Message, state: FSMContext):
    user_id, error = validate_int_input(message.text, MESSAGES["user_id"])

    if error:
        await message.answer(error)
        return

    reservations = get_user_reservations(user_id)
    if reservations:
        response = "\n".join([f"{MESSAGES['reservation_id']}: {res['reservation_id']} {MESSAGES['book_name']}: {res['book_name']} {MESSAGES['date']}: {res['reservation_date']}" for res in reservations])
        await message.answer(response)
        await ask_question(message, state, MESSAGES["enter_reservation_id"], DeleteReservation.waiting_for_reservation_id)
    else:
        await message.answer(MESSAGES["no_active_reservations"])
        await state.set_state(None)

# Function to handle the entered reservation ID for deletion
@router.message(DeleteReservation.waiting_for_reservation_id)
async def delete_reservation_id_entered(message: types.Message, state: FSMContext):
    reservation_id, error = validate_int_input(message.text, MESSAGES["reservation_id"])

    if error:
        await message.answer(error)
        return

    result = delete_user_reservation(reservation_id)
    await message.answer(MESSAGES["reservation_deleted_successfully"].format(reservation_id=reservation_id))
    await state.set_state(None)