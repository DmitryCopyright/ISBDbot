from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from Configuration.localization import MESSAGES
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
        await message.answer(MESSAGES["already_logged_in"])
    else:
        await ask_question(message, state, MESSAGES["enter_staff_name"], StaffLogin.waiting_for_staff_name)

@router.message(StaffLogin.waiting_for_staff_name)
async def staff_login_name_entered(message: types.Message, state: FSMContext):
    staff_name, error = validate_text_input(message.text, MESSAGES["staff_name"])

    if error:
        await message.answer(error)
        return

    staff_id = log_in_staff(staff_name)

    if staff_id:
        await state.update_data(staff_logged_in=True, staff_id=staff_id)
        await state.set_state(StaffLoggedIn.active)
        await message.answer(MESSAGES["staff_login_success"].format(staff_name=staff_name))
    else:
        await message.answer(MESSAGES["staff_login_failed"])
        await state.set_state(None)

# Валидация текстового ввода
def validate_text_input(input_text: str, field_name: str):
    """
    Проверяет корректность текстового ввода.

    :param input_text: Текст для проверки
    :param field_name: Название поля для отображения в сообщении об ошибке
    :return: (str, str) - Возвращает кортеж, где первый элемент — очищенный текст, второй — сообщение об ошибке (если есть)
    """
    cleaned_text = input_text.strip()

    if not cleaned_text:
        return None, MESSAGES["empty_field_error"].format(field_name=field_name)

    return cleaned_text, None