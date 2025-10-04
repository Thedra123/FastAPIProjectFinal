from fastapi import FastAPI
from database import Base, engine
from auth_router import router as auth_router
from routers.products_router import router as products_router
from routers.customers_router import router as customers_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="MiniERP API")

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(customers_router)

