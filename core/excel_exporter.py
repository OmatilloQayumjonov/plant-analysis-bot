import os
import shutil
from typing import Dict, Any, List
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill


def export_dpph_excel(
    plant_name: str,
    calc_result: Dict[str, Any],
    template_path: str,
    output_path: str
) -> str:
    """
    DPPH_template.xlsx shablonini tahlil natijalari bilan to'ldirib, output_path ga saqlaydi.
    Hujjat 100% tahrirlanadigan (dinamik formulalar bilan) bo'ladi:
    - Jadvaldagi ixtiyoriy Abs o'zgarganda AA% avtomatik qayta hisoblanadi.
    - K va L ustunlari formulalar orqali bog'langan bo'lib, grafiklar va IC50 darhol yangilanadi.
    - SLOPE, INTERCEPT va (y-b)/m formulalari faol, IC50 katagi qizil qalin shriftda ko'rsatiladi.
    """
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"DPPH shablon fayli topilmadi: {template_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    shutil.copy2(template_path, output_path)

    wb = load_workbook(output_path)
    ws = wb.active

    # O'simlik / namuna nomi
    if not plant_name:
        plant_name = "Noma'lum o'simlik"

    ws["A1"] = plant_name
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws["A1"].font = Font(name="Calibri", bold=True, size=13)
    ws.row_dimensions[1].height = 32

    # Grafik sarlavhalarini yangilash
    try:
        if hasattr(ws, "_charts"):
            if len(ws._charts) >= 1:
                ws._charts[0].title = plant_name
            if len(ws._charts) >= 2:
                ws._charts[1].title = plant_name
    except Exception:
        pass

    try:
        wb.calculation.fullCalcOnLoad = True
        wb.calculation.forceFullCalc = True
        wb.calculation.calcMode = "auto"
    except Exception:
        pass

    control = float(calc_result["control"])
    rows = calc_result["rows"]
    selected_time = int(calc_result.get("selected_time", 30))

    times = [0, 5, 10, 15, 20, 25, 30]
    volumes = [25, 50, 75, 100]

    # Stillar
    font_bold = Font(name="Calibri", bold=True, size=11)
    font_regular = Font(name="Calibri", bold=False, size=11)
    font_red_bold = Font(name="Calibri", bold=True, size=11, color="FF0000")
    
    align_center = Alignment(horizontal="center", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    thin_border = Border(
        left=Side(style="thin", color="BFBFBF"),
        right=Side(style="thin", color="BFBFBF"),
        top=Side(style="thin", color="BFBFBF"),
        bottom=Side(style="thin", color="BFBFBF")
    )

    # 1. Sarlavhalar (Row 2)
    headers = {
        "A2": "Daqiqa",
        "B2": "DPPH",
        "C2": "25 mkl",
        "D2": None,
        "E2": "50 mkl",
        "F2": None,
        "G2": "75 mkl",
        "H2": None,
        "I2": "100 mkl",
        "J2": None
    }
    for coord, text in headers.items():
        ws[coord] = text
        ws[coord].font = font_bold
        ws[coord].alignment = align_center
        ws[coord].border = thin_border

    # 2. 0-30 daqiqalar va DPPH ustunlari
    for excel_row, minute in enumerate(times, start=3):
        # Daqiqa
        c_min = ws.cell(excel_row, 1, minute)
        c_min.font = font_bold if minute == selected_time else font_regular
        c_min.alignment = align_center
        c_min.border = thin_border

        # DPPH (Control)
        if excel_row == 3:
            c_ctrl = ws.cell(excel_row, 2, control)
        else:
            # Pastki qatorlar 1-katakdagi Control ga bog'lanadi: =$B$3
            c_ctrl = ws.cell(excel_row, 2, "=$B$3")

        c_ctrl.font = font_regular
        c_ctrl.alignment = align_center
        c_ctrl.number_format = "0.000"
        c_ctrl.border = thin_border

    # 3. 0 daqiqa (Row 3: Barcha namunalar 0 daqiqada Control ga teng, AA% = 0)
    for col_idx, form_col in [(3, 4), (5, 6), (7, 8), (9, 10)]:
        # Abs = Control
        c_abs = ws.cell(3, col_idx, "=$B$3")
        c_abs.font = font_regular
        c_abs.alignment = align_center
        c_abs.number_format = "0.000"
        c_abs.border = thin_border

        # AA% = 0.00 formulasi
        abs_letter = {3: "C", 5: "E", 7: "G", 9: "I"}[col_idx]
        c_aa = ws.cell(3, form_col, f"=(B3-{abs_letter}3)/B3*100")
        c_aa.font = font_bold
        c_aa.alignment = align_right
        c_aa.number_format = "0.00"
        c_aa.border = thin_border

    # 4. 5-30 daqiqalar bo'yicha qiymatlar va formulalar
    column_map = {
        25: (3, 4),
        50: (5, 6),
        75: (7, 8),
        100: (9, 10)
    }

    for excel_row, minute in zip(range(4, 10), [5, 10, 15, 20, 25, 30]):
        is_target_row = (minute == selected_time)

        for volume in volumes:
            matching = [
                r for r in rows
                if r["Volume"] == volume and r["Minute"] == minute
            ]
            if not matching:
                continue

            data = matching[0]
            abs_col, aa_col = column_map[volume]

            # Spektrofotometr Abs qiymati
            c_abs = ws.cell(excel_row, abs_col, data["Abs"])
            c_abs.font = font_regular
            c_abs.alignment = align_center
            c_abs.number_format = "0.000" if len(str(data["Abs"]).split(".")[-1]) > 2 else "0.00"
            c_abs.border = thin_border

            # AA% formulasi: =(B{row} - Abs{row}) / B{row} * 100
            abs_letter = {3: "C", 5: "E", 7: "G", 9: "I"}[abs_col]
            c_aa = ws.cell(
                excel_row,
                aa_col,
                f"=(B{excel_row}-{abs_letter}{excel_row})/B{excel_row}*100"
            )
            c_aa.font = font_bold
            c_aa.alignment = align_right
            c_aa.number_format = "0.00"
            c_aa.border = thin_border

    # 5. IC50 va Grafik uchun ma'lumotlar (K va L ustunlari)
    # Tanlangan vaqt qatori: 5 min -> row 4, 10 min -> row 5, ..., 30 min -> row 9
    target_row = 3 + (selected_time // 5)
    if target_row < 4 or target_row > 9:
        target_row = 9

    ws["K2"] = None
    ws["L2"] = None

    # (0 µL -> 0.00%)
    c_k5 = ws["K5"]
    c_k5.value = 0
    c_k5.font = font_regular
    c_k5.alignment = align_center
    c_k5.border = thin_border

    c_l5 = ws["L5"]
    c_l5.value = 0.0
    c_l5.font = font_bold
    c_l5.alignment = align_right
    c_l5.number_format = "0.00"
    c_l5.border = thin_border

    # 25, 50, 75, 100 µL hajmlar uchun formulalar (tanlangan daqiqadagi AA% kataklariga bog'lanadi)
    regression_links = [
        (6, 25, f"=D{target_row}"),
        (7, 50, f"=F{target_row}"),
        (8, 75, f"=H{target_row}"),
        (9, 100, f"=J{target_row}")
    ]

    for excel_row, volume, formula in regression_links:
        # K (Volume)
        c_k = ws.cell(excel_row, 11, volume)
        c_k.font = font_regular
        c_k.alignment = align_center
        c_k.border = thin_border

        # L (AA% formula)
        c_l = ws.cell(excel_row, 12, formula)
        c_l.font = font_bold
        c_l.alignment = align_right
        c_l.number_format = "0.00"
        c_l.border = thin_border

    # 6. m, b, y, x=(y-b)/m (N va O ustunlari)
    # N5: m, O5: =SLOPE(L5:L9, K5:K9)
    ws["N5"] = "m"
    ws["N5"].font = font_bold
    ws["N5"].alignment = align_center
    ws["N5"].border = thin_border

    ws["O5"] = "=SLOPE(L5:L9,K5:K9)"
    ws["O5"].font = font_regular
    ws["O5"].alignment = align_right
    ws["O5"].number_format = "0.0000"
    ws["O5"].border = thin_border

    # N6: b, O6: =INTERCEPT(L5:L9, K5:K9)
    ws["N6"] = "b"
    ws["N6"].font = font_bold
    ws["N6"].alignment = align_center
    ws["N6"].border = thin_border

    ws["O6"] = "=INTERCEPT(L5:L9,K5:K9)"
    ws["O6"].font = font_regular
    ws["O6"].alignment = align_right
    ws["O6"].number_format = "0.0000"
    ws["O6"].border = thin_border

    # N7: y, O7: 50
    ws["N7"] = "y"
    ws["N7"].font = font_bold
    ws["N7"].alignment = align_center
    ws["N7"].border = thin_border

    ws["O7"] = 50
    ws["O7"].font = font_bold
    ws["O7"].alignment = align_right
    ws["O7"].border = thin_border

    # N8: x=(y-b)/m, O8: =(O7-O6)/O5  <-- QIZIL QALIN SHRIFTDA
    ws["N8"] = "x=(y-b)/m"
    ws["N8"].font = font_bold
    ws["N8"].alignment = align_center
    ws["N8"].border = thin_border

    ws["O8"] = "=(O7-O6)/O5"
    ws["O8"].font = font_red_bold
    ws["O8"].alignment = align_right
    ws["O8"].number_format = "0.00"
    ws["O8"].border = thin_border

    # N10: IC50 time, O10: selected_time
    ws["N10"] = "IC₅₀ time"
    ws["N10"].font = font_bold
    ws["N10"].alignment = align_center
    ws["N10"].border = thin_border

    ws["O10"] = selected_time
    ws["O10"].font = font_bold
    ws["O10"].alignment = align_center
    ws["O10"].border = thin_border

    # Ustun kengliklarini sozlash
    col_widths = {
        "A": 8,
        "B": 9,
        "C": 8,
        "D": 8,
        "E": 8,
        "F": 8,
        "G": 8,
        "H": 8,
        "I": 8,
        "J": 8,
        "K": 8,
        "L": 9,
        "M": 3,
        "N": 12,
        "O": 10
    }
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    wb.save(output_path)
    return output_path
