import asyncio
import json
import os

from flockserve.flockserve import Flockserve
from flockserve.workermanager import WorkerManager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from flockserve.loadbalancer import LeastConnectionLoadBalancer
import uvicorn
import httpx

class Flockserve_app:
    def __init__(self, config):
        self.app = FastAPI()
        self.config = config
        self.worker_manager = WorkerManager([], self.config)
        self.server = Flockserve(self.worker_manager, config=self.config, load_balancer=LeastConnectionLoadBalancer(self.worker_manager, self.config))

        #FastAPIInstrumentor.instrument_app(self.app)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.SKYPILOT_SERVIC_ACC_KEYFILE

        self.worker_manager.start_skypilot_worker(worker_id=0, reinit=False)

        @self.app.on_event("startup")
        async def on_startup():
            await self.server.init_session()
            await self.worker_manager.start_skypilot_worker(worker_id=0, reinit=False)
            asyncio.create_task(self.server.set_queue_tracker())
            asyncio.create_task(self.server.run_periodic_load_check())
            asyncio.create_task(self.worker_manager.periodic_worker_check())

        @self.app.on_event("shutdown")
        async def on_shutdown():
            await self.server.close_session()
            for worker in self.worker_manager.worker_handlers:
                await self.worker_manager.terminate_worker(worker)

        @self.app.post("/generate", response_class=PlainTextResponse)
        async def generate_code(request: Request):
            data = await request.body()
            headers = request.headers
            stream = json.loads(data.decode('utf-8')).get('parameters', {}).get('stream', False)
            if stream:
                return StreamingResponse(self.server.handle_stream_request(data, headers), media_type="text/plain")
            else:
                try:
                    return await self.server.handle_inference_request(data, headers, "/generate")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error during processing: {e}")

        # @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        # async def forward_request(request: Request, full_path: str):
        #     method = request.method
        #     headers = request.headers
        #     body = await request.body()
        #
        #     # Determine the destination URL based on the request
        #     # For example, this could be based on the path, headers, etc.
        #     destination_url = f"http://destination-server/{full_path}"
        #
        #     # Forward the request to the destination server
        #     try:
        #         async with httpx.AsyncClient() as client:
        #             response = await client.request(method, destination_url, headers=headers, content=body)
        #             return response.content
        #     except httpx.HTTPError as exc:
        #         raise HTTPException(status_code=500, detail=f"Error during forwarding: {exc}")
    def run(self):
        uvicorn.run(self.app, host=self.config.HOST, port=self.config.PORT, timeout_keep_alive=5)

# Usage
if __name__ == "__main__":
    app = Flockserve_app()
    app.run()
