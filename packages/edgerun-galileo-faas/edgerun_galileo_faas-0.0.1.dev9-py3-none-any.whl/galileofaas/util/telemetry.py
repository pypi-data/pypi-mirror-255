from typing import Dict, List, Optional

from faas.util.point import PointWindow, Point
from faas.util.rwlock import ReadWriteLock


class Resources:
    node: str
    limit: int
    window_lists: Dict[str, PointWindow[float]]

    def __init__(self, node: str, limit: int, metrics: List[str]):
        self.node = node
        self.limit = limit
        self.metrics = metrics
        self.window_lists = {}
        self.rw_locks = {}
        for metric in metrics:
            self.rw_locks[metric] = ReadWriteLock()
            self.window_lists[metric] = PointWindow[float](self.limit)

    def append(self, metric: str, resource_point: Point) -> bool:
        """
        Append the window to the specified metric
        :return: false if metric is not supported, otherwise true
        """
        window_list = self.window_lists.get(metric, None)
        if window_list is None:
            return False
        else:
            with self.rw_locks[metric].lock.gen_wlock():
                window_list.append(resource_point)
            return True

    def get_resource_windows(self, metric: str) -> Optional[List[Point[float]]]:
        window_list = self.window_lists.get(metric, None)
        if window_list is None:
            return None
        else:
            with self.rw_locks[metric].lock.gen_rlock():
                ret = window_list.value()
            return ret
