from data_sourcer import DataSourcer
from collections import deque

class DataManager:

    dataSourcer = None
    needed_points = None
    next_index = 0
    data: deque

    def __init__(self, dataSourcer: DataSourcer, needed_points: int):
        self.dataSourcer = dataSourcer
        self.data = deque(maxlen=needed_points)

    def get(self) -> list:
        new_data, self.next_index = self.dataSourcer.getFromIndex(self.next_index)
        self.data.extend(new_data)
        return list(self.data)