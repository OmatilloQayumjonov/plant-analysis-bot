import numpy as np
from typing import List, Dict, Tuple, Optional, Any


TIMES = [5, 10, 15, 20, 25, 30]
VOLUMES = [25, 50, 75, 100]

SAMPLE_EXAMPLE_TEXT = """1.048
0.816
0.601
0.539
0.454
0.675
0.302
0.236
0.261
0.614
0.253
0.225
0.263
0.584
0.237
0.219
0.260
0.558
0.225
0.215
0.258
0.540
0.218
0.213
0.259"""


def parse_absorbance_values(raw_text: str) -> List[float]:
    """
    Foydalanuvchi kiritgan matndan barcha raqamlarni (float) ajratib oladi.
    Vergul, nuqta, bo'shliq, probel, yangi qator, tabulyatsiya va boshqa ajratgichlarni qo'llab-quvvatlaydi.
    """
    if not raw_text:
        return []

    raw = raw_text.strip().replace(",", ".")
    for sep in ["\t", ";", "\n", "\r", " "]:
        raw = raw.replace(sep, " ")

    tokens = raw.split()
    values: List[float] = []

    for token in tokens:
        try:
            val = float(token)
            values.append(val)
        except ValueError:
            pass

    return values


def calculate_dpph(
    values: List[float],
    control: Optional[float] = None,
    selected_time: int = 30
) -> Dict[str, Any]:
    """
    DPPH va IC50 tahlilini hisoblaydi.
    24 ta qiymat (agar control alohida berilgan bo'lsa) yoki
    25 ta qiymat (1-qiymat control, qolgan 24 tasi sample) qabul qiladi.
    """
    if len(values) == 25:
        control = values[0]
        sample_values = values[1:]
    elif len(values) == 24:
        if control is None or control <= 0:
            raise ValueError("Control qiymati kiritilmagan yoki noto'g'ri!")
        sample_values = values
    else:
        raise ValueError(
            f"{len(values)} ta qiymat topildi. 24 ta sample Abs yoki 25 ta (1 control + 24 sample) kerak."
        )

    if control <= 0:
        raise ValueError("DPPH Control Abs qiymati 0 dan katta bo'lishi kerak!")

    rows: List[Dict[str, Any]] = []

    # Spektrofotometr natijalari vaqt bo'yicha ketma-ket joylashgan:
    # 5 min  -> 25, 50, 75, 100 µL
    # 10 min -> 25, 50, 75, 100 µL
    # 15 min -> 25, 50, 75, 100 µL
    # 20 min -> 25, 50, 75, 100 µL
    # 25 min -> 25, 50, 75, 100 µL
    # 30 min -> 25, 50, 75, 100 µL
    for time_index, minute in enumerate(TIMES):
        for volume_index, volume in enumerate(VOLUMES):
            index = time_index * len(VOLUMES) + volume_index
            absorbance = sample_values[index]
            activity = ((control - absorbance) / control) * 100.0

            rows.append({
                "Minute": minute,
                "DPPH": control,
                "Volume": volume,
                "Abs": absorbance,
                "Antiradical Activity (%)": activity
            })

    # Tanlangan vaqt bo'yicha IC50 chiziqli regressiyasi
    selected_rows = [r for r in rows if r["Minute"] == selected_time]
    if not selected_rows:
        selected_time = 30
        selected_rows = [r for r in rows if r["Minute"] == selected_time]

    y_activities = [r["Antiradical Activity (%)"] for r in selected_rows]

    # Regressiyaga (0 µL -> 0%) nuqta ham qo'shiladi
    regression_x = np.array([0.0, 25.0, 50.0, 75.0, 100.0], dtype=float)
    regression_y = np.array([0.0] + y_activities, dtype=float)

    # Chiziqli regressiya (Ordinary least-squares linear regression: y = slope * x + intercept)
    slope, intercept = np.polyfit(regression_x, regression_y, 1)

    predicted = slope * regression_x + intercept
    ss_res = np.sum((regression_y - predicted) ** 2)
    ss_tot = np.sum((regression_y - np.mean(regression_y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

    # IC50: y = 50 bo'lgandagi x qiymati (x = (50 - intercept) / slope)
    if slope != 0:
        ic50 = (50.0 - intercept) / slope
    else:
        ic50 = None

    return {
        "control": control,
        "sample_values": sample_values,
        "selected_time": selected_time,
        "rows": rows,
        "selected_rows": selected_rows,
        "slope": float(slope),
        "intercept": float(intercept),
        "r2": float(r2),
        "ic50": float(ic50) if ic50 is not None else None,
        "regression_x": regression_x.tolist(),
        "regression_y": regression_y.tolist()
    }
