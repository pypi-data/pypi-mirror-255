"""Main module."""

import asyncio
import json
from typing import List
import time
import aiohttp
from flockserve.config import Config
import logging
import pandas as pd
from flockserve.workermanager import WorkerManager
from flockserve.loadbalancer import Load_balancer


def time_weighted_mean(queue_tracker):
	"""
	Calculate the time weighted mean of the queue length.
	:param queue_tracker:
	:return:
	"""
	weights = pd.Series(sorted(queue_tracker)).diff().shift(-1) # time difference between two consecutive timestamps
	weights = weights / weights.sum() # normalize the weights
	weights = weights[:-1] # remove the last weight as it is NaN
	queue_lengths = pd.Series(queue_tracker.values())
	return (weights * queue_lengths).sum() # calculate the weighted mean


class Flockserve:
    """Main class."""

    def __init__(self, worker_manager: WorkerManager, config: Config, load_balancer:Load_balancer):
        """Constructor."""
        self.queue_length = 0
        self.queue_tracker = {time.time(): 0}  # {timestemp: queuelength at that time}
        self.queue_length_running_mean = 0
        self.worker_manager = worker_manager
        self.config = config
        self.load_balancer = load_balancer

        if hasattr(config, 'LOG_FILE'):
            logging.basicConfig(level=logging.INFO, filename=config.LOG_FILE)
        else:
            logging.basicConfig(level=logging.INFO)

        self.logger = logging.getLogger(__name__)

    async def init_session(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def set_queue_tracker(self):
        while True:
            self.queue_tracker[time.time()] = self.queue_length
            self.queue_tracker = {k: v for k, v in self.queue_tracker.items() if time.time() - k < 60 * 10}  # keep only the last 10 minutes of data
            self.queue_length_running_mean = time_weighted_mean(self.queue_tracker)
            await asyncio.sleep(10)

    async def run_periodic_load_check(self):
        while True:
            await self.worker_manager.periodic_load_check(self.queue_length_running_mean)
            await asyncio.sleep(20)

    async def handle_inference_request(self, data: bytes, headers, endpoint_path) -> str:
        self.queue_length += 1
        selected_worker = await self.load_balancer.select_worker()
        print(endpoint_path)
        try:
            if (endpoint_path == "/generate" or endpoint_path == "/v1/completions/" or
                    endpoint_path == "/v1/chat/completions"):
                # Add to queue only for the requests coming to /generate
                selected_worker.queue += 1

                start = time.perf_counter()
                #async with self.session.post(f"{selected_worker.base_url}/generate", data=data, headers=headers) as response:
                async with self.session.post(f"{selected_worker.base_url}{endpoint_path}", data=data,
                                             headers=headers) as response:
                    result = await response.text()
                    end = time.perf_counter()
                    if end - start > 30:
                        self.logger.warning(f"Time taken for inference: {end - start}"
                                       f"Input: {data.decode('utf-8')}"
                                       f"Output: {result}")
            elif endpoint_path == "/":
                async with self.session.get(f"{selected_worker.base_url}/", headers=headers) as response:
                    result = await response.text()
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error handling request for worker {selected_worker.base_url}: {e}")
            raise
        finally:
            self.queue_length -= 1
            selected_worker.queue -= 1
        return result

    # async def handle_stream_request(self, data: bytes, headers, endpoint_path: str):
    #     selected_worker = await self.load_balancer.select_worker()
    #
    #     async with self.session.post(f"{selected_worker.base_url}{endpoint_path}", json=json.loads(data.decode('utf-8')),
    #                                  headers=headers, timeout=None) as response:
    #         # Check if the response status is OK
    #         if response.status == 200:
    #             # Process the streamed data line by line
    #             async for line in response.content:
    #                 decoded_line = line.decode('utf-8').strip()
    #                 self.logger.info(f"decoded_line: {decoded_line}")
    #                 # Yield each line
    #                 yield decoded_line
