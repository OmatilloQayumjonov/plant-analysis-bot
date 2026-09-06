# Plant Chemical Analysis — DPPH / IC₅₀ Telegram Boti

Ushbu bot **"Plant Chemical Analysis"** dasturidagi **DPPH / IC₅₀ (Antiradikal faollik)** bo'limining Telegram bot versiyasidir.

## Imkoniyatlari:
1. **Spektrofotometr ma'lumotlarini qabul qilish:**
   - 25 ta (1 ta Control + 24 ta Sample) yoki 24 ta Absorbance qiymatlarini oddiy matn sifatida qabul qiladi.
   - Vergul, nuqta, bo'shliq, probel va yangi qatorlarni avtomatik tozalaydi.
2. **Matematik tahlil:**
   - Antiradikal faollik: $\text{Activity (\%)} = \frac{\text{Control} - \text{Abs}}{\text{Control}} \times 100$
   - Tanlangan vaqt (5, 10, 15, 20, 25 yoki 30 min) bo'yicha chiziqli regressiya: $y = mx + b$
   - Determinatsiya koeffitsiyenti ($R^2$)
   - $y = 50\%$ bo'lgandagi $\text{IC}_{50}$ ($\mu\text{L}$) ko'rsatkichi.
3. **Grafiklar:**
   - 📈 Antiradikal faollikning vaqt bo'yicha dinamikasi grafigi (25, 50, 75, 100 µL).
   - 📉 IC₅₀ chiziqli regressiya grafigi (Tajriba nuqtalari, regressiya to'g'ri chizig'i, 50% ingibitsiya belgisi va hisoblangan IC₅₀ nuqtasi).
4. **Excel hisoboti:**
   - `DPPH_template.xlsx` shabloniga barcha daqiqalar va hajmlar bo'yicha formulalar hamda natijalarni kiritadi va tayyor `.xlsx` faylni foydalanuvchiga yuboradi.
5. **Demo / Namuna rejimi:**
   - Bir tugma orqali namunaviy qiymatlarni darhol hisoblab ko'rish imkoniyati.

---

## O'rnatish va Ishga tushirish

### 1. Bot tokenini kiritish
1. Telegramda [@BotFather](https://t.me/BotFather) orqali yangi bot oching va token oling.
2. Loyiha papkasidagi `.env` faylini oching.
3. Quyidagi qatorga bot tokeningizni yozing va saqlang:
   ```env
   BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ```

### 2. Botni ishga tushirish
Windowsda `run_bot.bat` faylini ikki marta bosing yoki terminalda quyidagi buyruqni bajaring:

```cmd
C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe main.py
```
yoki:
```cmd
py -3 main.py
```
