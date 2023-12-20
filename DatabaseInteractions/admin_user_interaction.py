from db import create_connection


def delete_user_reservation(reservation_id):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            query = '''
                DELETE FROM BookReservations
                WHERE reservation_id = %s
            '''
            cursor.execute(query, (reservation_id,))