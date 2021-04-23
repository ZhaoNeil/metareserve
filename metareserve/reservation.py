
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



class Reservation(object):
    def __init__(self, nodes):
        self._nodes = {x.node_id: x for x in nodes}


    '''Search for and return a node.
    Args:
        node_id (optional int): If set, searches for node using its ID. Returns in O(1).
        hostname (optional str): if set, searches for node using its hostname. Returns in O(n).
    
    Raises:
        ValueError, if neither id nor hostname provided.
        KeyError, if no Node was found.
    
    Returns:
        Found Node instance.'''
    def get_node(self, node_id=-1, hostname=''):
        if node_id != -1: # search by id
            return self._nodes(node_id)
        elif any(hostname):
            try: # search by hostname
                return next(x for x in self._nodes.values() if x.hostname == hostname)
            except StopIteration as e:
                raise KeyError('Could not find hostname {} in reservation. Available hostnames: {}'.format(hostname, ', '.join(self._nodes.values())))
        else:
            raise ValueError('To get a node, please either set node_id or specify a hostname.')

    def __len__(self):
        return len(self._nodes)



class ReservationWait(object):
    '''ReservationWait object, to let clients wait for the reservation to be ready.
    Args:
        status (optional Status): Object representing status of reservation.'''

    from enum import Enum as _Enum
    from time import sleep as _time_sleep
    from threading import Thread as _Thread
    from datetime.datetime import now as _datetime_now
    from datetime import timedelta as _datetime_timedelta
    class Status(_Enum):
        PENDING = 0,
        STARTED = 1,
        FAILED = 2

    def __init__(self, status=Status.PENDING):
        self._status = status

    @property
    def status(self):
        return self._status

    '''Gets a reservation. Raises exception when reservation fails/failed.
    Args:
        blocking (optional bool): If set, blocks until reservation is ready. Otherwise, instantly returns either reservation object or `None` if not ready,
    Raises:
        ValueError, if reservation fails/failed.

    Returns:
        Reservation object (once ready). If `blocking` is not set, directly returns None if reservation object is not ready.'''
    def get(blocking=True):
        pass


    '''Gets a reservation. Specify a timeout in seconds to get the request. Once the allocated time has passed without getting the reservation, returns `None`.
    Args:
        timeout_seconds (optional int): Number of seconds to wait before giving up and returning `None`.
        request_sleep_period (optional int): Number of seconds to wait between requests.

    Raises:
        ValueError, if reservation fails/failed.

    Returns:
        Reservation object, if ready before `timeout_seconds`. Otherwise `None`.
        '''
    def get_or_timeout(timeout_seconds=30, request_sleep_period=10):
        if request_sleep_period >= timeout_seconds:
            raise ValueError('Cannot wait more than (or equal to) {} seconds per period (specified {})'.format(timeout_seconds, request_sleep_period))
        t = _Thread(target=get)

        time_out = _datetime_now() + _datetime_timedelta(seconds=timeout_seconds)
        while _datetime_now() < time_out:
            val = get(blocking=False)
            if val:
                return val
            _time_sleep(request_sleep_period)
        return None        



class _AbstractReservationRequest(object):
    '''Abstract object representing a reservation
    Args:
        num_nodes (int): Number of nodes in reservation.
        duration_minutes (int): Number of minutes to reserve nodes

    '''
    def __init__(self, num_nodes, location=''):
        self._num_nodes = num_nodes
        self._location = location

    @property
    def num_nodes(self):
        return self._num_nodes
    
    @property
    def location(self):
        return self._location



class ReservationRequest(_AbstractReservationRequest):
    '''Object representing a regular reservation request (request nodes for X minutes).
    Args:
        num_nodes (int): Number of nodes in reservation.
        duration_minutes (int): Number of minutes to reserve nodes.
        location (str, optional): Location for reserved nodes
    '''
    def __init__(self, num_nodes, duration_minutes, location=''):
        super.__init__(num_nodes, location=location)
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
        location (str, optional): Location for reserved nodes
    '''
    def __init__(self, num_nodes, duration_start, duration_end, location=''):
        super.__init__(num_nodes, location=location)
        self._duration_start = duration_start
        self._duration_end = duration_end

    @property
    def duration_start(self):
        return self._duration_start

    @property
    def duration_end(self):
        return self._duration_end
    