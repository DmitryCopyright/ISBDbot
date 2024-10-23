from Configuration.db import create_connection
from Configuration.db_operations import delete_record


def delete_user_reservation(reservation_id):
    return delete_record("BookReservations", "reservation_id", reservation_id)
