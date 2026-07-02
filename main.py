import sqlite3
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Gold Price Calculator")
templates = Jinja2Templates(directory="templates")

DB_PATH = "gold.db"

TROY_OUNCE_GRAMS = 31.1035
KARAT_18_RATIO = 18 / 24  # 0.75


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at  TEXT    NOT NULL,
            ounce_usd   REAL    NOT NULL,
            usd_rial    REAL    NOT NULL,
            price_gram  REAL    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def calculate_gold_18k(ounce_usd: float, usd_rial: float) -> float:
    """
    قیمت هر گرم طلای ۱۸ عیار (ریال) =
        (قیمت اونس × ۱۸/۲۴) / ۳۱.۱۰۳۵ × نرخ دلار
    """
    return (ounce_usd * KARAT_18_RATIO / TROY_OUNCE_GRAMS) * usd_rial


def save_to_db(ounce_usd: float, usd_rial: float, price_gram: float):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO calculations (created_at, ounce_usd, usd_rial, price_gram) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ounce_usd, usd_rial, price_gram),
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM calculations ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    history = get_history()
    return templates.TemplateResponse("index.html", {"request": request, "history": history})


@app.post("/calculate")
async def calculate(
    ounce_usd: float = Form(...),
    usd_rial: float = Form(...),
):
    price_gram = calculate_gold_18k(ounce_usd, usd_rial)
    save_to_db(ounce_usd, usd_rial, price_gram)
    return JSONResponse({
        "ounce_usd": ounce_usd,
        "usd_rial": usd_rial,
        "price_gram": round(price_gram, 0),
    })


@app.get("/history")
async def history():
    return JSONResponse(get_history())
