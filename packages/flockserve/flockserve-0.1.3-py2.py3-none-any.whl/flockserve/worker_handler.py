"""Module for Individual Workers."""
import os
import subprocess
import sky
import aiohttp
from dataclasses import dataclass


@dataclass
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
