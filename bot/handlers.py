import os
import io
from datetime import datetime
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile,
    FSInputFile
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from bot.states import DPPHStates
from bot.keyboards import (
    get_main_keyboard,
    get_cancel_keyboard,
    get_skip_or_cancel_keyboard,
    get_time_selection_inline_keyboard,
    get_example_fill_inline_keyboard
)
from bot.config import TEMPLATE_PATH, OUTPUT_DIR
from core.calculator import (
    parse_absorbance_values,
    calculate_dpph,
    SAMPLE_EXAMPLE_TEXT
)
from core.plotter import (
    generate_activity_vs_time_chart,
    generate_ic50_regression_chart
)
from core.excel_exporter import export_dpph_excel


router = Router()


# =========================================================
# ASOSIY BUYRUQLAR VA BEKOR QILISH
# =========================================================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    welcome_text = (
        "👋 **Assalomu alaykum!**\n\n"
        "🌱 **Plant Chemical Analysis — DPPH / IC₅₀ Tahlil Botiga xush kelibsiz!**\n\n"
        "Ushbu bot yordamida spektrofotometr ma'lumotlari asosida "
        "o'simliklarning **antiradikal faolligi** va **IC₅₀** ko'rsatkichini "
        "avtomatik hisoblab, grafiklar va tayyor Excel hisobotini olishingiz mumkin.\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang 👇"
    )
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text == "❌ Bekor qilish")
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Amaliyot bekor qilindi. Bosh menyudasiz.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "ℹ️ Yo'riqnoma va Ma'lumot")
async def cmd_info(message: Message):
    info_text = (
        "📖 **DPPH / IC₅₀ Botidan foydalanish bo'yicha yo'riqnoma:**\n\n"
        "1️⃣ **Namuna nomi:** O'simlik yoki ekstrakt nomini kiriting (masalan: *Curcuma longa L.*).\n"
        "2️⃣ **IC₅₀ vaqti:** Regressiya hisoblanadigan vaqtni tanlang (standart: **30 min**).\n"
        "3️⃣ **Spektrofotometr ABS qiymatlari:**\n"
        "   • Hammasi bo'lib **25 ta** (1 ta Control + 24 ta Sample) yoki **24 ta** qiymat kiritiladi.\n"
        "   • Tartib: 5, 10, 15, 20, 25, 30 daqiqa uchun har 4 tadan (25, 50, 75, 100 µL).\n"
        "   • Qiymatlarni shunchaki bo'shliq yoki yangi qator bilan nusxalab yuborish kifoya.\n\n"
        "📊 **Natijada nima olasiz?**\n"
        "   ✅ Chiziqli regressiya formulasi (y = mx + b) va R²\n"
        "   ✅ Hisoblangan IC₅₀ (µL)\n"
        "   ✅ 2 ta sifatli grafik (Faollik dinamikasi va IC₅₀ regressiyasi)\n"
        "   ✅ To'liq rasmiylashtirilgan Excel (.xlsx) hisoboti"
    )
    await message.answer(
        info_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


# =========================================================
# 1-QADAM: YANGI TAHLILNI BOSHLASH (O'SIMLIK NOMI)
# =========================================================

@router.message(F.text == "🧬 Yangi DPPH tahlili")
async def start_dpph_analysis(message: Message, state: FSMContext):
    await state.set_state(DPPHStates.waiting_plant_name)
    await message.answer(
        "🌿 **1-qadam:** O'simlik / namuna nomini kiriting:\n\n"
        "*(Masalan: Curcuma longa L. (kurkuma))*\n\n"
        "Agar nom kiritishni xohlamasangiz, pastdagi **'⏭ O'tkazib yuborish'** tugmasini bosing.",
        reply_markup=get_skip_or_cancel_keyboard(),
        parse_mode="Markdown"
    )


@router.message(DPPHStates.waiting_plant_name)
async def process_plant_name(message: Message, state: FSMContext):
    if message.text == "⏭ O'tkazib yuborish":
        plant_name = "Noma'lum o'simlik"
    else:
        plant_name = message.text.strip()

    await state.update_data(plant_name=plant_name, selected_time=30)
    await state.set_state(DPPHStates.waiting_time)

    await message.answer(
        f"✅ O'simlik nomi: **{plant_name}**\n\n"
        "⏱ **2-qadam:** IC₅₀ hisoblash uchun vaqtni tanlang (standart: **30 min**):",
        reply_markup=get_time_selection_inline_keyboard(30),
        parse_mode="Markdown"
    )


# =========================================================
# 2-QADAM: VAQTNI TANLASH (INLINE)
# =========================================================

@router.callback_query(DPPHStates.waiting_time, F.data.startswith("set_time:"))
async def callback_set_time(callback: CallbackQuery, state: FSMContext):
    selected = int(callback.data.split(":")[1])
    await state.update_data(selected_time=selected)

    await callback.message.edit_reply_markup(
        reply_markup=get_time_selection_inline_keyboard(selected)
    )
    await callback.answer(f"Tanlandi: {selected} min")


@router.callback_query(DPPHStates.waiting_time, F.data == "confirm_time")
async def callback_confirm_time(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_time = data.get("selected_time", 30)

    await state.set_state(DPPHStates.waiting_abs_values)
    await callback.message.delete()

    prompt_text = (
        f"⏱ Tanlangan vaqt: **{selected_time} min**\n\n"
        "🧪 **3-qadam: Spektrofotometr ABS qiymatlarini yuboring.**\n\n"
        "Spektrofotometrdan **25 ta qiymat** (1-chi Control + 24 ta Sample) "
        "yoki 24 ta Sample qiymatlarini nusxalab, shu yerga xabar qilib yuboring.\n\n"
        "*(Tartib: 5, 10, 15, 20, 25, 30 minutlar uchun har 4 tadan: "
        "25 µL, 50 µL, 75 µL, 100 µL)*\n\n"
        "Agar test qilib ko'rmoqchi bo'lsangiz, pastdagi tugmani bosing 👇"
    )
    await callback.message.answer(
        prompt_text,
        reply_markup=get_example_fill_inline_keyboard(),
        parse_mode="Markdown"
    )


# =========================================================
# 3-QADAM: ABS QIYMATLARINI QABUL QILISH VA HISOBLASH
# =========================================================

@router.callback_query(DPPHStates.waiting_abs_values, F.data == "fill_example_abs")
async def callback_fill_example(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Namunaviy qiymatlar yuklanmoqda...")
    await execute_calculation(callback.message, state, SAMPLE_EXAMPLE_TEXT)


@router.message(DPPHStates.waiting_abs_values, F.text)
async def process_abs_input(message: Message, state: FSMContext):
    await execute_calculation(message, state, message.text)


# =========================================================
# NAMUNA BILAN SINASH (BIR BOSISHDA DEMO)
# =========================================================

@router.message(F.text == "📋 Namuna bilan sinash (Demo)")
async def run_demo_analysis(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(plant_name="Curcuma longa L. (Demo)", selected_time=30)
    await message.answer(
        "🚀 **Demo rejim:** Namunaviy ma'lumotlar bilan hisob-kitob bajarilmoqda...",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    await execute_calculation(message, state, SAMPLE_EXAMPLE_TEXT)


# =========================================================
# ASOSIY HISOBLASH VA NATIJALARNI YUBORISH FUNKSIYASI
# =========================================================

async def execute_calculation(message: Message, state: FSMContext, raw_text: str):
    data = await state.get_data()
    plant_name = data.get("plant_name", "Curcuma longa L.")
    selected_time = data.get("selected_time", 30)

    # Qiymatlarni o'qib olish
    values = parse_absorbance_values(raw_text)

    if not values:
        await message.answer(
            "⚠️ Hech qanday raqam aniqlanmadi. Iltimos, spektrofotometr Abs qiymatlarini to'g'ri kiriting.",
            reply_markup=get_cancel_keyboard()
        )
        return

    if len(values) not in (24, 25):
        await message.answer(
            f"⚠️ **{len(values)} ta** qiymat topildi.\n\n"
            f"Tahlil uchun **25 ta** (1-chi Control + 24 ta Sample) yoki **24 ta** qiymat bo'lishi kerak.\n"
            f"Iltimos, qaytadan tekshirib nusxa ko'chiring.",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        return

    # Jarayon xabari
    status_msg = await message.answer("⏳ **Hisoblash va grafiklar tayyorlanmoqda...**", parse_mode="Markdown")

    try:
        # Hisob-kitob
        calc_result = calculate_dpph(values, selected_time=selected_time)

        control = calc_result["control"]
        slope = calc_result["slope"]
        intercept = calc_result["intercept"]
        r2 = calc_result["r2"]
        ic50 = calc_result["ic50"]

        ic50_str = f"{ic50:.4f} µL" if ic50 is not None else "Hisoblanmadi"

        # Matnli xulosa
        report_text = (
            f"✅ **DPPH / IC₅₀ Tahlil Natijalari**\n\n"
            f"🌿 **O'simlik / Namuna:** `{plant_name}`\n"
            f"🧪 **DPPH Control Abs:** `{control:.4f}`\n"
            f"⏱ **IC₅₀ hisoblangan vaqt:** `{selected_time} min`\n\n"
            f"📊 **Chiziqli Regressiya (Linear Regression):**\n"
            f"• Tenglama: `y = {slope:.6f}x + {intercept:.6f}`\n"
            f"• Qiyalik (m / slope): `{slope:.6f}`\n"
            f"• Siljish (b / intercept): `{intercept:.6f}`\n"
            f"• Determinatsiya koeffitsiyenti (R²): `{r2:.6f}`\n\n"
            f"🎯 **IC₅₀ (50% ingibitsiya konsentratsiyasi):**\n"
            f"👉 **{ic50_str}**\n\n"
            f"Grafiklar va Excel hisoboti quyida yuklanmoqda 👇"
        )

        await status_msg.edit_text(report_text, parse_mode="Markdown")

        # 1. Grafik — Antiradikal faollik dinamikasi
        chart1_buf = generate_activity_vs_time_chart(calc_result["rows"], plant_name)
        photo1 = BufferedInputFile(
            chart1_buf.read(),
            filename=f"dpph_activity_{selected_time}min.png"
        )
        await message.answer_photo(
            photo1,
            caption=f"📈 **Antiradikal faollik dinamikasi (Vaqt bo'yicha)**\nNamuna: {plant_name}",
            parse_mode="Markdown"
        )

        # 2. Grafik — IC50 Regressiya
        chart2_buf = generate_ic50_regression_chart(
            calc_result["selected_rows"],
            slope,
            intercept,
            ic50,
            selected_time,
            plant_name
        )
        photo2 = BufferedInputFile(
            chart2_buf.read(),
            filename=f"ic50_regression_{selected_time}min.png"
        )
        await message.answer_photo(
            photo2,
            caption=f"📉 **IC₅₀ Chiziqli Regressiya Grafigi**\nIC₅₀ = {ic50_str} (R² = {r2:.4f})",
            parse_mode="Markdown"
        )

        # 3. Excel hisobotini shakllantirish va yuborish
        safe_name = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in plant_name).strip() or "Sample"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"DPPH_{safe_name}_{timestamp}.xlsx"
        excel_path = os.path.join(OUTPUT_DIR, excel_filename)

        export_dpph_excel(
            plant_name=plant_name,
            calc_result=calc_result,
            template_path=str(TEMPLATE_PATH),
            output_path=excel_path
        )

        excel_doc = FSInputFile(excel_path, filename=excel_filename)
        await message.answer_document(
            excel_doc,
            caption="📑 **Tayyor Excel hisoboti (`.xlsx`)**\nBarcha hisob-kitob va jadvallar kiritilgan.",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

        # Holatni tozalash
        await state.clear()

    except Exception as e:
        await message.answer(
            f"❌ Hisoblash jarayonida xatolik yuz berdi: `{str(e)}`",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        await state.clear()
