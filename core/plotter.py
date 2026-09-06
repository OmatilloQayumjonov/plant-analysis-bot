import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Optional


def generate_activity_vs_time_chart(rows: List[Dict[str, Any]], plant_name: str = "Namuna") -> io.BytesIO:
    """
    Antiradikal faollikning vaqtga bog'liqlik grafigini hosil qiladi.
    BytesIO obyekti (PNG rasm) qaytaradi.
    """
    volumes = [25, 50, 75, 100]

    plt.figure(figsize=(9, 5.5), dpi=150)

    colors = ["#2563EB", "#16A34A", "#EA580C", "#DC2626"]
    markers = ["o", "s", "^", "D"]

    for idx, volume in enumerate(volumes):
        data = [r for r in rows if r["Volume"] == volume]
        x = [r["Minute"] for r in data]
        y = [r["Antiradical Activity (%)"] for r in data]

        plt.plot(
            x,
            y,
            marker=markers[idx % len(markers)],
            color=colors[idx % len(colors)],
            linewidth=2,
            markersize=6,
            label=f"{volume} µL"
        )

    plt.xlabel("Time (min)", fontsize=11, fontweight="bold")
    plt.ylabel("Antiradical activity (%)", fontsize=11, fontweight="bold")
    plt.title(f"DPPH Antiradical Activity vs Time\n({plant_name})", fontsize=12, fontweight="bold", pad=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150)
    plt.close()
    buf.seek(0)
    return buf


def generate_ic50_regression_chart(
    selected_rows: List[Dict[str, Any]],
    slope: float,
    intercept: float,
    ic50: Optional[float],
    selected_time: int = 30,
    plant_name: str = "Namuna"
) -> io.BytesIO:
    """
    IC50 Chiziqli regressiya grafigini hosil qiladi.
    BytesIO obyekti (PNG rasm) qaytaradi.
    """
    x = np.array([0.0] + [r["Volume"] for r in selected_rows], dtype=float)
    y = np.array([0.0] + [r["Antiradical Activity (%)"] for r in selected_rows], dtype=float)

    max_x = max(max(x), (ic50 * 1.1) if (ic50 and ic50 > 0 and ic50 < 300) else 100.0)
    x_line = np.linspace(0.0, max_x, 150)
    y_line = slope * x_line + intercept

    plt.figure(figsize=(9, 5.5), dpi=150)

    # Tajriba nuqtalari
    plt.scatter(
        x,
        y,
        color="#1E40AF",
        s=80,
        zorder=5,
        label="Experimental data"
    )

    # Regressiya to'g'ri chizig'i
    eq_label = f"Linear regression (y = {slope:.4f}x + {intercept:.4f})"
    plt.plot(
        x_line,
        y_line,
        color="#2563EB",
        linewidth=2,
        label=eq_label
    )

    # 50% ingibitsiya chizig'i
    plt.axhline(
        50,
        color="#DC2626",
        linestyle="--",
        linewidth=1.5,
        label="50% inhibition"
    )

    # IC50 vertikal chizig'i
    if ic50 is not None and ic50 > 0:
        plt.axvline(
            ic50,
            color="#16A34A",
            linestyle="--",
            linewidth=1.5,
            label=f"IC₅₀ = {ic50:.2f} µL"
        )
        plt.scatter([ic50], [50], color="#DC2626", s=100, zorder=6)

    plt.xlabel("Volume (µL)", fontsize=11, fontweight="bold")
    plt.ylabel("Antiradical activity (%)", fontsize=11, fontweight="bold")
    plt.title(
        f"IC₅₀ Determination at {selected_time} min\n({plant_name})",
        fontsize=12,
        fontweight="bold",
        pad=12
    )
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150)
    plt.close()
    buf.seek(0)
    return buf
