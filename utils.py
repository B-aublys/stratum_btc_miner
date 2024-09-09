from dataclasses import dataclass
from typing import List

@dataclass
class Mining_data():
    job_ID: str = None
    prev_HASH: str = None
    gen_tranx_1: str = None
    gen_tranx_2: str = None
    merkle_branches: List[str] = None
    btc_block_version: str = None
    nBits: str = None
    nTime: str = None
    clean_jobs: bool = None
    difficulty: int = None


