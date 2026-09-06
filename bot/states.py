from aiogram.fsm.state import State, StatesGroup


class DPPHStates(StatesGroup):
    waiting_plant_name = State()
    waiting_time = State()
    waiting_abs_values = State()
