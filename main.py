from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from auth_router import router as auth_router
from routers.products_router import router as products_router
from routers.customers_router import router as customers_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="MiniERP API")

# ---------------- CORS Middleware ----------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # izin verilen frontend originleri
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE vs.
    allow_headers=["*"],          # tüm header’lar
)
# -------------------------------------------------

# Router'ları ekle
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(customers_router)
