from enum import Enum as _Enum
from time import sleep as _time_sleep
import datetime as _datetime
import concurrent.futures

class Node(object):
    def __init__(self, node_id, node_name='', ip_local='', ip_public='', port=22, extra_info=dict()):
        self._node_id = node_id
        self._hostname = node_name
        self._ip_local = ip_local
        self._ip_public = ip_public
        self._port = port
        self._extra_info = extra_info

    @property
    def node_id(self):
        return self._node_id

    @property
    def hostname(self):
        return self._hostname
    
    @property
    def ip_local(self):
        return self._ip_local
    
    @property
    def ip_public(self):
        return self._ip_public

    @property
    def port(self):
        return self._port
    
    @property
    def extra_info(self):
        return self._extra_info

    @staticmethod
    def from_string(string):
        node_id, node_name, ip_local, ip_public, port, dictentry_string = string.split('|', 5)
        return Node(int(node_id), node_name, ip_local, ip_public, int(port), extra_info={key: val for (key, val) in (x.split('=') for x in dictentry_string.split('|'))})

    def __str__(self):
        return '|'.join(str(x) for x in [self._node_id, self._hostname, self._ip_local, self._ip_public, self._port, '|'.join('{}={}'.format(key, val) for key, val in self._extra_info.items())])


class Reservation(object):
    def __init__(self, nodes):
            self._nodes = {x.node_id: x for x in nodes}

    @property
    def nodes(self):
        return self._nodes.values()
    

    def get_node(self, node_id=-1, hostname=''):
        '''Search for and return a node.
        Args:
            node_id (optional int): If set, searches for node using its ID. Returns in O(1).
            hostname (optional str): if set, searches for node using its hostname. Returns in O(n).
        
        Raises:
            ValueError, if neither id nor hostname provided.
            KeyError, if no Node was found.
        
        Returns:
            Found Node instance.'''
        if node_id != -1: # search by id
            return self._nodes(node_id)
        elif any(hostname):
            try: # search by hostname
                return next(x for x in self._nodes.values() if x.hostname == hostname)
            except StopIteration as e:
                raise KeyError('Could not find hostname {} in reservation. Available hostnames: {}'.format(hostname, ', '.join(self._nodes.values())))
        else:
            raise ValueError('To get a node, please either set node_id or specify a hostname.')


    @staticmethod
    def from_string(string):
        return Reservation([Node.from_string(line) for line in string.split('\n')])


    def __str__(self):
        return '\n'.join(str(x) for x in self.nodes)


    def __len__(self):
        return len(self._nodes)


class ReservationWait(object):
    '''ReservationWait object, to let clients wait for the reservation to be ready.
    Args:
        status (optional Status): Object representing status of reservation.'''

    class Status(_Enum):
        '''Enum to represent different possible states of a reservation.'''
        PENDING = 0,
        SUCCESS = 1,
        FAILED = 2

    def __init__(self, func, *args, status=Status.PENDING):
        self._thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        def stat_func(stat, func, *args):
            val = func(*args)
            stat._status = Status.SUCCESS
            return val
        self._future = self._thread_executor.submit(stat_func, self, func, *args)
        self._status = status


    @property
    def status(self):
        return self._status


    def get(blocking=True):
        '''Gets a reservation. Raises exception when reservation fails/failed.
        Args:
            blocking (optional bool): If set, blocks until reservation is ready. Otherwise, instantly returns either reservation object or `None` if not ready,

        Raises:
            ValueError, if reservation fails/failed or shutdown occured before completion.

        Returns:
            Reservation object (once ready). If `blocking` is not set, directly returns None if reservation object is not ready.'''
        if self._status == Status.FAILED:
            raise ValueError('Reservation failed.')
        if self._future.is_cancelled():
            raise ValueError('Reservation request was cancelled.')
        if blocking or self._future.done():
            try:
                nodes = self._future.result()
            except Exception as e:
                self._status = Status.FAILED
                raise ValueError('Experienced error', e)
        else:
            nodes = None
        return nodes


    def get_or_timeout(timeout_seconds=30, request_sleep_period=5):
        '''Gets a reservation. Specify a timeout in seconds to get the request. Once the allocated time has passed without getting the reservation, returns `None`.
        Args:
            timeout_seconds (optional int): Number of seconds to wait before giving up and returning `None`.
            request_sleep_period (optional int): Number of seconds to wait between requests.

        Raises:
            ValueError, if reservation fails/failed.

        Returns:
            Reservation object, if ready before `timeout_seconds`. Otherwise `None`.'''
        if request_sleep_period >= timeout_seconds:
            raise ValueError('Cannot wait more than (or equal to) {} seconds per period (specified {})'.format(timeout_seconds, request_sleep_period))
  
        time_out = _datetime.datetime.now() + _datetime.timedelta(seconds=timeout_seconds)
        while _datetime.datetime.now() < time_out:
            val = get(blocking=False)
            if val:
                return val
            _time_sleep(request_sleep_period)
        return None


    def shutdown(self):
        '''Shuts down reservation wait. Implementations have to cal this method to gracefully shutdown threadpool executor.'''
        if not self._future.done():
            self._future.cancel() # Cancels future (only works if future did not start execution yet. Returns True on success, False on failure)
        self._thread_executor.shutdown()




class _AbstractReservationRequest(object):
    '''Abstract object representing a reservation.
    Args:
        num_nodes (int): Number of nodes in reservation.
        duration_minutes (int): Number of minutes to reserve nodes.
        location (str, optional): Location for reserved nodes.
        extra_info (dict, optional): Key-value mapping with extra info.'''
    def __init__(self, num_nodes, location='', extra_info=dict()):
        self._num_nodes = num_nodes
        self._location = location
        self._extra_info = extra_info

    @property
    def num_nodes(self):
        return self._num_nodes
    
    @property
    def location(self):
        return self._location

    @property
    def extra_info(self):
        return self._extra_info



class ReservationRequest(_AbstractReservationRequest):
    '''Object representing a regular reservation request (request nodes for X minutes).
    Args:
        num_nodes (int): Number of nodes in reservation.
        duration_minutes (int): Number of minutes to reserve nodes.
        location (str, optional): Location for reserved nodes.'''
    def __init__(self, num_nodes, duration_minutes, location=''):
        super().__init__(num_nodes, location=location)
        self._duration_minutes = duration_minutes

    @property
    def duration_minutes(self):
        return self._duration_minutes



class TimeSlotReservationRequest(_AbstractReservationRequest):
    '''Object representing a timeslot reservation request (request nodes from datetime X, ending at datetime Y).
    Args:
        num_nodes (int): Number of nodes in reservation.
        duration_start (datetime): Start time for reserved nodes.
        duration_end (datetime): End time for reserved nodes.
        location (str, optional): Location for reserved nodes.'''
    def __init__(self, num_nodes, duration_start, duration_end, location=''):
        super().__init__(num_nodes, location=location)
        self._duration_start = duration_start
        self._duration_end = duration_end

    @property
    def duration_start(self):
        return self._duration_start

    @property
    def duration_end(self):
        return self._duration_end
    