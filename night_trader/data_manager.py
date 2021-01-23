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

    def get(self) -> tuple:
        new_data, new_index = self.dataSourcer.getFromIndex(self.next_index)
        if(new_index == self.next_index):
            return (False, list(self.data))
        else:
            self.next_index = new_index
            self.data.extend(new_data)
            return (True, list(self.data))