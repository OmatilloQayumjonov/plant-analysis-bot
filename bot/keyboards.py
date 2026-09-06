from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    kb = [
        [KeyboardButton(text="🧬 Yangi DPPH tahlili")],
        [KeyboardButton(text="📋 Namuna bilan sinash (Demo)")],
        [KeyboardButton(text="ℹ️ Yo'riqnoma va Ma'lumot")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish klaviaturasi"""
    kb = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_skip_or_cancel_keyboard() -> ReplyKeyboardMarkup:
    """O'tkazib yuborish yoki bekor qilish klaviaturasi"""
    kb = [
        [KeyboardButton(text="⏭ O'tkazib yuborish")],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_time_selection_inline_keyboard(current_time: int = 30) -> InlineKeyboardMarkup:
    """IC50 vaqtini tanlash uchun inline tugmalar"""
    times = [5, 10, 15, 20, 25, 30]
    buttons = []
    row = []

    for t in times:
        prefix = "✅ " if t == current_time else ""
        row.append(
            InlineKeyboardButton(
                text=f"{prefix}{t} min",
                callback_data=f"set_time:{t}"
            )
        )
        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(
            text="Davom etish ➡️",
            callback_data="confirm_time"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_example_fill_inline_keyboard() -> InlineKeyboardMarkup:
    """Namuna Abs qiymatlarini avtomatik kiritish inline tugmasi"""
    buttons = [
        [
            InlineKeyboardButton(
                text="📋 Namunaviy qiymatlar bilan to'ldirish",
                callback_data="fill_example_abs"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
