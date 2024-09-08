from dataclasses import dataclass
from typing import List

@dataclass
class Mining_data():
    job_ID: str
    prev_HASH: str
    gen_tranx_1: str
    gen_tranx_2: str
    merkle_branches: List[str]
    btc_block_version: str
    nBits: str
    nTime: str
    clean_jobs: bool


