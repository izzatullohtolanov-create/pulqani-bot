
import os, re, sqlite3, requests
from flask import Flask, request, jsonify, send_from_directory

app=Flask(__name__, static_folder="static")
DB="data.db"
TOKEN=os.environ.get("BOT_TOKEN","").strip()
ALLOWED_CHAT_ID=os.environ.get("ALLOWED_CHAT_ID","").strip()

def db():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS tx(
      id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, amount REAL,
      kind TEXT, category TEXT, note TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.commit()
    return c

def send(chat_id,text):
    if not TOKEN: return
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  json={"chat_id":chat_id,"text":text},timeout=15)

def parse(text):
    m=re.search(r'(\d+(?:[.,]\d+)?)',text.replace(" ",""))
    if not m: return None
    amount=float(m.group(1).replace(",",".")); low=text.lower()
    kind="income" if any(x in low for x in ["daromad","kirim","oylik","maosh","+"]) else "expense"
    cats={"ovqat":"Oziq-ovqat","oziq":"Oziq-ovqat","transport":"Transport",
          "oqish":"O‘qish","o‘qish":"O‘qish","kiyim":"Kiyim","uy":"Uy",
          "internet":"Telefon/Internet","telefon":"Telefon/Internet",
          "koch":"Ko‘ngilochar","ko‘ngil":"Ko‘ngilochar"}
    category="Boshqa"
    for k,v in cats.items():
        if k in low: category=v; break
    note=re.sub(r'\d+(?:[.,]\d+)?',"",text).strip(" -:") or category
    return amount,kind,category,note

@app.get("/")
def home(): return send_from_directory("static","index.html")

@app.post("/api/telegram")
def telegram():
    u=request.get_json(silent=True) or {}
    msg=u.get("message") or {}
    chat=msg.get("chat",{}).get("id")
    text=msg.get("text","").strip()
    if not chat: return jsonify(ok=True)
    if ALLOWED_CHAT_ID and str(chat)!=ALLOWED_CHAT_ID: return jsonify(ok=True)
    if text.startswith("/start"):
        send(chat,"Assalomu alaykum! Pulqani botiga xush kelibsiz.\n\nMasalan:\n25000 ovqat\n100000 transport\n1000000 oylik\n\n/balans — balans\n/hisobot — hisobot")
        return jsonify(ok=True)
    c=db()
    if text=="/balans":
        inc=c.execute("SELECT COALESCE(SUM(amount),0) FROM tx WHERE chat_id=? AND kind='income'",(str(chat),)).fetchone()[0]
        exp=c.execute("SELECT COALESCE(SUM(amount),0) FROM tx WHERE chat_id=? AND kind='expense'",(str(chat),)).fetchone()[0]
        send(chat,f"💰 Balans: {inc-exp:,.0f} so‘m\n\nDaromad: {inc:,.0f} so‘m\nXarajat: {exp:,.0f} so‘m")
        return jsonify(ok=True)
    if text=="/hisobot":
        rows=c.execute("SELECT category,SUM(amount) FROM tx WHERE chat_id=? AND kind='expense' GROUP BY category ORDER BY 2 DESC",(str(chat),)).fetchall()
        if not rows: send(chat,"Hali xarajatlar yo‘q."); return jsonify(ok=True)
        s="📊 Xarajatlar hisoboti\n\n"+"".join(f"• {a}: {b:,.0f} so‘m\n" for a,b in rows)
        send(chat,s); return jsonify(ok=True)
    p=parse(text)
    if not p:
        send(chat,"Tushunmadim. Masalan: 25000 ovqat yoki 1000000 oylik deb yozing.")
        return jsonify(ok=True)
    amount,kind,cat,note=p
    c.execute("INSERT INTO tx(chat_id,amount,kind,category,note) VALUES(?,?,?,?,?)",(str(chat),amount,kind,cat,note))
    c.commit(); c.close()
    send(chat,("💰 Daromad" if kind=="income" else "💸 Xarajat")+f" qo‘shildi: {amount:,.0f} so‘m\nKategoriya: {cat}")
    return jsonify(ok=True)

@app.get("/api/transactions")
def transactions():
    c=db()
    rows=c.execute("SELECT id,amount,kind,category,note,created_at FROM tx ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify([dict(id=r[0],amount=r[1],kind=r[2],category=r[3],note=r[4],created_at=r[5]) for r in rows])

@app.post("/api/transactions")
def add():
    x=request.get_json() or {}
    c=db(); c.execute("INSERT INTO tx(chat_id,amount,kind,category,note) VALUES(?,?,?,?,?)",
      ("web",float(x["amount"]),x["kind"],x["category"],x.get("note","Izohsiz"))); c.commit(); c.close()
    return jsonify(ok=True)

@app.get("/health")
def health(): return "ok"

if __name__=="__main__":
    db()
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
