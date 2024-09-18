from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .store import (
    PlacedItemTable,
    PlacementTable,
    ProductTable,
    startup_and_shutdown_db,
)
from .env import DEBUG
from .routers import ordered_products, orders, placements
from .templates import templates


# https://stackoverflow.com/a/65270864
# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(_: FastAPI):
    startup_db, shutdown_db = startup_and_shutdown_db
    await startup_db()
    yield
    await shutdown_db()


app = FastAPI(debug=DEBUG, lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(ordered_products.router)
app.include_router(orders.router)
app.include_router(placements.router)


@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse(request, "index.html")


if DEBUG:

    @app.get("/test")
    async def test():
        return {
            "product_table": await ProductTable.select_all(),
            "order_sessions": orders.order_sessions,
            "placed_item_table": await PlacedItemTable.select_all(),
            "placement_table": await PlacementTable.select_all(),
        }
