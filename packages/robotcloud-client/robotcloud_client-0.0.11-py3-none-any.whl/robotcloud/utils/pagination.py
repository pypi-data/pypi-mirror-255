from dataclasses import dataclass

from robotcloud.utils.datatables.request import DataTableRequest


@dataclass
class Pagination:
    startIndex: int
    maxSize: int

    def __init__(self, req: DataTableRequest):
        self.startIndex = req.start
        self.maxSize = req.length
