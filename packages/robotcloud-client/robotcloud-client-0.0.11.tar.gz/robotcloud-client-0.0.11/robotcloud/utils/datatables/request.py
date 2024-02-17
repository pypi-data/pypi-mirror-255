from dataclasses import dataclass


@dataclass
class DataTableRequest:
    draw: int = 0
    start: int = 0
    length: int = 10
    # search: List[str | bool] = ()
    # order: List = ()
    # columns: List = ()

    def from_query_params(self, query_params: dict):
        self.draw = query_params.get('draw')
        self.start = query_params.get('start')
        self.length = query_params.get('length')
        return self
