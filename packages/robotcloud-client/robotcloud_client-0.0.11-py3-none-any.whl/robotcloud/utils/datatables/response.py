from dataclasses import dataclass
from typing import List

from robotcloud.utils import PaginatedResponse
from robotcloud.utils.datatables.request import DataTableRequest


@dataclass
class DataTableResponse:
    draw: int
    recordsTotal: int
    recordsFiltered: int
    data: List

    def __init__(self, req: DataTableRequest, res: PaginatedResponse):
        self.draw = 0 if req.draw is None else int(req.draw)
        self.recordsTotal = res.total_records
        self.recordsFiltered = res.total_records_filtered
        self.data = res.data
