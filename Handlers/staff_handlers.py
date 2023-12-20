from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from DatabaseInteractions.user_management import log_in_staff
from Handlers.bot_handlers import router, ask_question

class StaffLogin(StatesGroup):
    waiting_for_staff_name = State()

class StaffLoggedIn(StatesGroup):
    active = State()

@router.message(Command(commands=["stafflogin"]))
async def cmd_staff_login(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("logged_in") or user_data.get("staff_logged_in"):
        await message.answer("You are already logged in.")
    else:
        await message.answer("Enter your staff name:")
        await state.set_state(StaffLogin.waiting_for_staff_name)

@router.message(StaffLogin.waiting_for_staff_name)
async def staff_login_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(staff_name=message.text)
    data = await state.get_data()
    staff_id = log_in_staff(data['staff_name'])

    if staff_id:
        await state.update_data(staff_logged_in=True, staff_id=staff_id)
        await state.set_state(StaffLoggedIn.active)
        await message.answer("Login successful. Welcome, " + data['staff_name'] + "!")
    else:
        await message.answer("Incorrect staff name.")
        await state.set_state(None)
