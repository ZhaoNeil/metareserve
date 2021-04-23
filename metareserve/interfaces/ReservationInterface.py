

class ReservationInterface(object):

    '''Perform a reservation, as specified by the reservation request.
    Must return immediately without blocking.
    Time-consuming reservation systems should use a separate thread for reservation logic.
    Args:
        reservationRequest (ReservationRequest): Object containing request information.

    Returns:
        ReservationWait object.'''
    def reserve(reservation_request):
        pass


    '''Stops a reservation.
    Must return immediately without blocking.
    Time-consuming reservation systems should use a separate thread for reservation logic.
    Args:
        reservation (Reservation): Object containing reservation.

    Returns:
        Nothing.
        '''
    def stopReservation(reservation):
        pass