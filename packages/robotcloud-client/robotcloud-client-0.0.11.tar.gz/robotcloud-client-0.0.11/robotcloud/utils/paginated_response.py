from dataclasses import dataclass
from typing import List


@dataclass
class PaginatedResponse:
    data: List
    total_records: int  # Total records, before filtering
    total_records_filtered: int  # Total records, after filtering
