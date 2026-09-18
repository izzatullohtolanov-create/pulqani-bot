PULQANI TELEGRAM BOT + WEB APP
1) GitHub repo yarating va shu fayllarni yuklang.
2) Render -> New -> Web Service -> GitHub repo.
3) Build Command: pip install -r requirements.txt
4) Start Command: gunicorn app:app
5) Free plan tanlash mumkin (test uchun).
6) Environment Variables:
   BOT_TOKEN = BotFather bergan YANGI token (uni chatga yubormang)
   ALLOWED_CHAT_ID = ixtiyoriy, botni faqat o'zingiz ishlatishingiz uchun Telegram chat ID.
7) Deploy bo'lgach Render URL olinadi, masalan https://pulqani.onrender.com
8) Webhookni bir marta quyidagicha o'rnating:
   https://api.telegram.org/botBOT_TOKEN/setWebhook?url=https://SIZNING-URL.onrender.com/api/telegram
   Brauzerda ochilganda {"ok":true} chiqishi kerak.
9) Botga /start yuboring.
Telegram komandalar: /start, /balans, /hisobot
Oddiy yozuvlar: 25000 ovqat; 100000 transport; 1000000 oylik.

MUHIM: Render Free servis 15 daqiqa trafik bo'lmasa uxlaydi va local fayllar qayta ishga tushganda yo'qolishi mumkin. Shu sabab bu versiya test/prototip uchun. Keyingi bosqichda doimiy database ulash mumkin.
