"""Module for monitoring and managing worker processes."""
import asyncio
from typing import List
import sky
import aiohttp
import multiprocessing
import logging

class Worker_handler:
	worker_name: str
	worker_type: str # local, skypilot
	capacity: int
	queue: int
	is_initializing: bool
	healthy: bool
	session = aiohttp.ClientSession
	base_url= None
	handle = None # Only applicable for local workers

class Worker_manager():
	def __init__(self, worker_handlers: List[Worker_handler], flockserve, logger):
		self.worker_lock = asyncio.Lock()
		self.worker_handlers = worker_handlers
		self.flockserve = flockserve
		self.logger = logger

	async def start_skypilot_worker(self, worker_id, worker_type='skypilot', reinit=False):
		worker_name = self.flockserve.worker_name_prefix + '-' + str(worker_id)
		self.launcher_sub_process = multiprocessing.Process(target=Worker_manager.launch_task_process, args=(
			worker_name, self.flockserve.skypilot_job_file, reinit))
		self.worker_handlers.append(
			Worker_handler(worker_name, worker_type, self.flockserve.worker_capacity, queue=0, is_initializing=True,
						   healthy=False))
		return self.launcher_sub_process.start()

	@staticmethod
	def launch_task_process(worker_name, skypilot_job_file, reinit):
		if reinit:
			sky.cancel(cluster_name=worker_name, all=True)
		# try:
		task = sky.Task.from_yaml(skypilot_job_file)
		print("TASK", task)
		if Worker_manager.is_any_running_jobs(worker_name):
			# self.logger.info("Job already running, skipping launch.")
			pass
		else:
			print(task)
			sky.launch(task, cluster_name=worker_name, retry_until_up=False)
			print("SKY LAUNCH DONE!")
		# except Exception as e:
		#     #pass
		#     self.logger.info("Error:", e)

	async def terminate_worker(self, worker_handler: Worker_handler):
		self.logger.info(f"Terminating worker at {worker_handler.base_url}")

		if worker_handler.worker_type == 'local' and hasattr(worker_handler, 'handle'):
			worker_handler.handle.terminate()
			worker_handler.handle.wait()
		elif worker_handler.worker_type == 'skypilot':
			sky.down(cluster_name=worker_handler.worker_name, purge=True)

	@staticmethod
	async def is_finished_initializing(worker_handler: Worker_handler):
		cluster_statuses = sky.status(cluster_names=None, refresh=False)
		cluster_status = next((x for x in cluster_statuses if x['name'] == worker_handler.worker_name), None)
		print('='*50)
		print("cluster_status")
		print('='*50)
		print(cluster_status)

		# Head IP only exists for the workers that have initialization completed.
		if cluster_status and isinstance(cluster_status.get('handle', {}).head_ip, str):
			return True
		else:
			return False

	@staticmethod
	async def is_worker_healthy(worker_handler: Worker_handler):
		if worker_handler.base_url is None:
			return False

		async with worker_handler.session.get(f"{worker_handler.base_url}/health") as response:
			if response.status != 200:
				return False

		return True

	@staticmethod
	def is_worker_exists(worker_name):
		return len(sky.status(cluster_names=worker_name, refresh=False)) != 0

	@staticmethod
	def is_worker_available(worker:Worker_handler):
		return worker.capacity - worker.queue > 0 and not worker.is_initializing and worker.healthy

	@staticmethod
	def is_any_running_jobs(worker_name):
		if not Worker_manager.is_worker_exists(worker_name):
			return False
		else:
			skypilot_job_queue = sky.queue(cluster_name=worker_name)
			return next((True for job in skypilot_job_queue if job.get('status').value == 'RUNNING'), False)

	@staticmethod
	async def setup_initialized_worker(worker_handler: Worker_handler, port):
		if await Worker_manager.is_finished_initializing(worker_handler):
			# Set base_url
			cluster_statuses = sky.status(cluster_names=None, refresh=False)
			cluster_status = next((x for x in cluster_statuses if x['name'] == worker_handler.worker_name), None)
			worker_handler.base_url = "http://" + cluster_status['handle'].head_ip + f":{port}"

			# Setup session
			worker_handler.session = aiohttp.ClientSession()


	async def periodic_load_check(self, queue_length_running_mean):
		try:
			worker_load = sum([w.queue for w in self.worker_handlers])
			live_worker_count = sum([(not w.is_initializing) and (w.healthy) for w in self.worker_handlers])
			self.logger.info(f"Workers: {len(self.worker_handlers)}, "
							 f"Workers Live & Healthy: {live_worker_count}, "
							 f"Worker Load: {worker_load}, "
							 f"QLRM: {round(queue_length_running_mean,2)}")

			if queue_length_running_mean > 7 and len(self.worker_handlers) < self.flockserve.max_workers and live_worker_count == len(self.worker_handlers):  # If any worker is initializing, don't add a new worker.
				self.logger.warning("High load detected, creating worker...")
				await self.start_skypilot_worker(worker_id=self.get_next_worker_id(), reinit=False)

			elif queue_length_running_mean < 4 and live_worker_count > 1 and live_worker_count == len(self.worker_handlers):
				self.logger.warning("Low load detected, deleting worker...")
				await self.delete_worker(min([worker for worker in self.worker_handlers if not worker.is_initializing],
											 key=lambda w: w.queue))

		except Exception as e:
			self.logger.info("Error below in periodic_load_check;")
			self.logger.info(e)

	async def periodic_worker_check(self):
		while True:
			for worker in list(self.worker_handlers):
				print('Checking worker: ', worker.worker_name)
				print('is_initializing: ', worker.is_initializing)
				print('is_healthy: ', worker.healthy)

				if worker.is_initializing:
					if await Worker_manager.is_finished_initializing(worker):
						try:
							await Worker_manager.setup_initialized_worker(worker, self.flockserve.port)
							worker.is_initializing = False
							self.logger.info(f"Worker: {worker.worker_name} , initialization and setup completed: {worker.base_url}")
						except Exception as e:
							worker.is_initializing = True
							self.logger.info(f"Error during initializing : {e}")

				else:
					try:
						if await Worker_manager.is_worker_healthy(worker):
							self.logger.info(f"Healthy Worker: {worker.worker_name} ")
							worker.healthy = True
						else:
							self.logger.info(f"!!UNHEALTHY!! Worker: {worker.worker_name} ")
							worker.healthy = False
					except Exception as e:
						self.logger.info(f"Error during health check : {e}")
						worker.healthy = False

				await asyncio.sleep(20)

	def get_next_worker_id(self):
		existing_worker_names = [w.worker_name for w in self.worker_handlers]
		worker_id = 0
		while self.flockserve.worker_name_prefix + "-" + str(worker_id) in existing_worker_names:
			worker_id += 1

		return worker_id

	async def delete_worker(self, worker: Worker_handler) -> None:
		self.logger.info(f"Initiating deletion for worker: {worker.base_url}")
		async with self.worker_lock:
			i = 0
			while worker.queue > 0 and i < 20:
				i += 1
				await asyncio.sleep(6)
			if worker in self.worker_handlers:
				sky.down(cluster_name=worker.worker_name, purge=True)
				# worker.terminate()
				self.worker_handlers.remove(worker)

