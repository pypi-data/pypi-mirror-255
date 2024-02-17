from aiohttp import web
import aiohttp_cors
from redlite.server import res
from redlite.util import redlite_data_dir
from ..util import read_data, read_meta, read_runs

__docformat__ = "google"


class RunReader:
    def __init__(self, base: str):
        self.base = base

    async def runs(self) -> list[dict]:
        return list(read_runs(self.base))

    async def data(self, name: str) -> list[dict]:
        return list(read_data(self.base, name))

    async def meta(self, name: str) -> dict:
        return read_meta(self.base, name)


class Service:
    def __init__(self, reader: RunReader):
        self.reader = reader

    async def runs(self, request):
        runs = await self.reader.runs()
        return web.json_response(runs)

    async def data(self, request):
        name = request.match_info["name"]
        data = await self.reader.data(name)
        return web.json_response(data)

    async def meta(self, request):
        name = request.match_info["name"]
        meta = await self.reader.meta(name)
        return web.json_response(meta)


async def index(request):
    return web.FileResponse(res("build", "index.html"))


@web.middleware
async def handle_404(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as ex:
        if ex.status == 404:
            return await index(request)
        raise


def get_app(reader: RunReader):
    app = web.Application()
    service = Service(reader)
    app.add_routes(
        [
            web.get("/api/runs", service.runs),
            web.get("/api/runs/{name}/meta", service.meta),
            web.get("/api/runs/{name}/data", service.data),
            web.get("/", index),
            web.static("/", res("build")),
            web.get("", index),
        ]
    )

    cors = aiohttp_cors.setup(
        app,
        defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")},
    )
    for route in list(app.router.routes()):
        cors.add(route)

    app.middlewares.append(handle_404)

    return app


def main(port: int = 8000):
    base = redlite_data_dir()

    app = get_app(RunReader(base))

    web.run_app(app, port=port)


if __name__ == "__main__":
    main()
