from back_end_whisper_woods import Customer, Hotel, Room


def test_customer_pay_for_booking():
    customer = Customer(
        'Nino',
        500.0,
        2
    )

    result = customer.pay_for_booking(200.0)

    assert result is True
    assert customer.budget == 300.0


def test_hotel_books_only_available_room():
    room = Room(
        101,
        'Forest Deluxe',
        280.0,
        True,
        2
    )

    hotel = Hotel(
        'Whisper Woods',
        [room]
    )

    first_customer = Customer(
        'Nino',
        1000.0,
        2
    )

    second_customer = Customer(
        'Giorgi',
        1000.0,
        2
    )

    first_result = hotel.book_room_for_customer(
        first_customer,
        101,
        1,
        '2026-07-20',
        '2026-07-21'
    )

    second_result = hotel.book_room_for_customer(
        second_customer,
        101,
        1,
        '2026-07-20',
        '2026-07-21'
    )

    assert first_result is True
    assert second_result is False
    assert room.is_available is False