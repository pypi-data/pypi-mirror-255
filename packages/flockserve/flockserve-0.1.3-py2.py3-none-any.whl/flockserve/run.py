# import asyncio
# import json
# from flockserve import Flockserver
# from worker_manager import Worker_manager
# from fastapi import FastAPI, HTTPException, Request
# from config import Config
# from fastapi.responses import PlainTextResponse, StreamingResponse
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from loadbalancer import Standard_LB
#
# app = FastAPI()
# config = Config()
# worker_manager = Worker_manager([], config)
# server = Flockserve(load_balancer=Standard_LB([],config), config=config)
#
#
#
# @app.on_event("startup")
# async def on_startup():
# 	await server.init_session()
# 	await worker_manager.start_skypilot_worker(worker_id=0, reinit=False)
# 	asyncio.create_task(worker_manager.periodic_load_check())
# 	asyncio.create_task(worker_manager.periodic_worker_check())
#
#
# @app.on_event("shutdown")
# async def on_shutdown():
# 	await server.close_session()
#
# 	for worker in worker_manager.worker_handlers:
# 		await worker_manager.terminate_worker(worker)
#
#
# @app.post("/generate", response_class=PlainTextResponse)
# async def generate_code(request: Request):
# 	data = await request.body()
# 	headers = request.headers
# 	stream = json.loads(data.decode('utf-8')).get('parameters',{}).get('stream', False)
# 	if stream:
# 		return StreamingResponse(server.handle_stream_request(data, headers), media_type="text/plain")
# 	else:
# 		try:
# 			return await server.handle_inference_request(data, headers, "/generate")
# 		except Exception as e:
# 			raise HTTPException(status_code=500, detail=f"Error during processing: {e}")
#
#
#
#
# FastAPIInstrumentor.instrument_app(app)
#
# if __name__ == "__main__":
# 	import uvicorn
# 	uvicorn.run(app, host=config.HOST, port=config.PORT, timeout_keep_alive=5)
