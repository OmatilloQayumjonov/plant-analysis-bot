# 🌐 Botni 24/7 Doimiy Ishlaydigan Qilish Qo'llanmasi (Render.com orqali)

Ushbu qo'llanma orqali kompyuteringiz o'chiq bo'lganda ham botingiz bulutli serverda 24 soat to'xtovsiz ishlashi uchun uni **Render.com** platformasiga bepul joylaysiz.

Loyiha allaqachon Git va server uchun to'liq tayyorlangan (`requirements.txt`, `Procfile`, `render.yaml`, web server ping integratsiyasi qo'shilgan).

---

## 1-QADAM: GitHub ga loyihani yuklash

1. Brauzeringizda **[github.com](https://github.com)** ga kiring.
2. O'ng yuqori burchakdagi **`+`** tugmasini bosib, **"New repository"** ni tanlang.
3. Sozlamalar:
   - **Repository name:** `plant-analysis-bot`
   - **Private** (shaxsiy) qilib qo'yishingiz mumkin.
   - Hech qanday README yoki boshqa katakchalarga belgi qo'ymang.
   - **"Create repository"** tugmasini bosing.
4. Ochilgan sahifadagi havolani oling (masalan: `https://github.com/SIZNING_USERNAME/plant-analysis-bot.git`).
5. `D:\dars prog\plant analys` papkasida terminal (yoki CMD) ochib, quyidagi 3 ta buyruqni bering:
   ```bash
   git branch -M main
   git remote add origin https://github.com/SIZNING_USERNAME/plant-analysis-bot.git
   git push -u origin main
   ```
   *(Eslatma: `SIZNING_USERNAME` o'rniga o'z GitHub nomingizni yozing)*.

---

## 2-QADAM: Render.com da bepul ishga tushirish

1. **[render.com](https://render.com)** saytiga kiring va GitHub orqali kiring (*Sign in with GitHub*).
2. **"New +"** tugmasini bosing va **"Web Service"** ni tanlang.
3. Yangi yuklagan `plant-analysis-bot` repozitoriyangiz yonidagi **"Connect"** tugmasini bosing.
4. Sozlamalarni tekshiring:
   - **Name:** `plant-analysis-bot`
   - **Region:** `Frankfurt (EU Central)` yoki `Singapore`
   - **Branch:** `main`
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** **Free ($0/month)**
5. **"Environment Variables"** bo'limida **"Add Environment Variable"** tugmasini bosib, quyidagini qo'shing:
   - **Key:** `BOT_TOKEN`
   - **Value:** `8939401003:AAGO2fMFsR489ZisMQO4DGZBETAt6W478ag`
   - **Key:** `PYTHON_VERSION`
   - **Value:** `3.11.8`
6. Sahifa pastidagi **"Deploy Web Service"** tugmasini bosing!

---

## 3-QADAM: Server uxlab qolmasligi uchun (24/7 uyg'oq tutish)

Render bepul tarifida 15 daqiqa murojaat bo'lmasa, serverni uxlab qolishdan asrash uchun:
1. Render sizga bergan URL manzilni nusxalang (masalan: `https://plant-analysis-bot.onrender.com`).
2. **[cron-job.org](https://cron-job.org)** yoki **[uptimerobot.com](https://uptimerobot.com)** saytida bepul monitor qo'shing:
   - URL: `https://plant-analysis-bot.onrender.com/`
   - Interval: Har **10 daqiqada** (*Every 10 minutes*).

---

🎉 **Tamom!** Endi kompyuteringizni butunlay o'chirib qo'ysangiz ham, botingiz doimo 24/7 internetda ishlab turadi va foydalanuvchilar har qanday vaqtda tahlil qila oladi!
