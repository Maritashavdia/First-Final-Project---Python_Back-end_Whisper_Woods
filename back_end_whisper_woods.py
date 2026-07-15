import logging
from datetime import datetime

logging.basicConfig(
    filename='bookings_history.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class Room:
    def __init__(
            self,
            room_number: int,
            room_type: str,
            price_per_night: float,
            is_available: bool,
            max_guests: int
    ):
        self.room_number = room_number
        self.room_type = room_type
        self.price_per_night = price_per_night
        self.is_available = is_available
        self.max_guests = max_guests

    def book_room(self):
        self.is_available = False

    def release_room(self):
        self.is_available = True

    def calculate_price(self, nights: int) -> float:
        return self.price_per_night * nights

    def __str__(self):
        return (
            f'Room number: {self.room_number}, '
            f'Room type: {self.room_type}, '
            f'Price per night: {self.price_per_night} GEL, '
            f'Available: {self.is_available}, '
            f'Max guests: {self.max_guests}'
        )


class Customer:
    def __init__(
            self,
            name: str,
            budget: float,
            number_of_guests: int
    ):
        self.name = name
        self.budget = budget
        self.number_of_guests = number_of_guests
        self.booked_rooms = []
        self.bookings = []
        self.reward_points = 0
        self.booking_count = 0

    def add_room(self, room: Room):
        self.booked_rooms.append(room)

    def remove_room(self, room: Room):
        if room in self.booked_rooms:
            self.booked_rooms.remove(room)

    def calculate_next_booking_points(self) -> int:
        next_booking_number = self.booking_count + 1
        group_number = (next_booking_number - 1) // 5
        position_in_group = (next_booking_number - 1) % 5 + 1

        if position_in_group == 5:
            return (group_number + 1) * 100

        return (
                group_number * 100
                + position_in_group * 10
        )

    def add_reward_points(self) -> int:
        earned_points = self.calculate_next_booking_points()

        self.booking_count += 1
        self.reward_points += earned_points

        return earned_points

    def calculate_discount(
            self,
            points_to_use: int
    ) -> float:
        if points_to_use < 0:
            return 0

        if points_to_use > self.reward_points:
            return 0

        if points_to_use % 100 != 0:
            return 0

        if points_to_use > 1000:
            return 0

        return (points_to_use // 100) * 2

    def use_reward_points(
            self,
            points_to_use: int
    ):
        self.reward_points -= points_to_use

    def pay_for_booking(
            self,
            total_price: float
    ) -> bool:
        if self.budget >= total_price:
            self.budget -= total_price
            return True

        return False

    def show_booking_summary(self) -> str:
        if not self.bookings:
            return f'{self.name} has no bookings.'

        summary = (
            f'\nCustomer: {self.name}\n'
            f'Remaining budget: {self.budget:.2f} GEL\n'
            f'Booking count: {self.booking_count}\n'
            f'Reward points: {self.reward_points}\n'
            f'Bookings:\n'
        )

        for booking in self.bookings:
            summary += f'{booking}\n'

        return summary


class Booking:
    def __init__(
            self,
            customer: Customer,
            room: Room,
            nights: int,
            original_price: float,
            discount_percent: float,
            points_used: int,
            final_price: float,
            check_in_date: str,
            check_out_date: str,
            earned_points: int
    ):
        self.customer = customer
        self.room = room
        self.nights = nights
        self.original_price = original_price
        self.discount_percent = discount_percent
        self.points_used = points_used
        self.final_price = final_price
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.earned_points = earned_points
        self.booking_status = 'Confirmed'

    def cancel_booking(self):
        self.booking_status = 'Cancelled'

    def __str__(self):
        return (
            f'Room number: {self.room.room_number}\n'
            f'Room type: {self.room.room_type}\n'
            f'Check-in: {self.check_in_date}\n'
            f'Check-out: {self.check_out_date}\n'
            f'Nights: {self.nights}\n'
            f'Original price: {self.original_price:.2f} GEL\n'
            f'Discount: {self.discount_percent:.0f}%\n'
            f'Final price: {self.final_price:.2f} GEL\n'
            f'Status: {self.booking_status}'
        )


class Hotel:
    def __init__(
            self,
            name: str,
            rooms: list
    ):
        self.name = name
        self.rooms = rooms
        self.bookings_log = []
        self.last_booking_message = ''

    def find_room(
            self,
            room_number: int
    ):
        for room in self.rooms:
            if room.room_number == room_number:
                return room

        return None

    def is_room_available_for_dates(
            self,
            room_number: int,
            check_in_date: str,
            check_out_date: str
    ) -> bool:
        new_check_in = datetime.strptime(
            check_in_date,
            '%Y-%m-%d'
        )

        new_check_out = datetime.strptime(
            check_out_date,
            '%Y-%m-%d'
        )

        for booking in self.bookings_log:
            if (
                    booking.room.room_number == room_number
                    and booking.booking_status == 'Confirmed'
            ):
                existing_check_in = datetime.strptime(
                    booking.check_in_date,
                    '%Y-%m-%d'
                )

                existing_check_out = datetime.strptime(
                    booking.check_out_date,
                    '%Y-%m-%d'
                )

                dates_overlap = (
                        new_check_in < existing_check_out
                        and new_check_out > existing_check_in
                )

                if dates_overlap:
                    return False

        return True

    def show_available_rooms(
            self,
            room_type: str = None,
            number_of_guests: int = None,
            check_in_date: str = None,
            check_out_date: str = None
    ) -> list:
        available_rooms = []

        for room in self.rooms:
            if (
                    room_type is not None
                    and room.room_type != room_type
            ):
                continue

            if (
                    number_of_guests is not None
                    and room.max_guests < number_of_guests
            ):
                continue

            if (
                    check_in_date is not None
                    and check_out_date is not None
                    and not self.is_room_available_for_dates(
                room.room_number,
                check_in_date,
                check_out_date
            )
            ):
                continue

            available_rooms.append(room)

        return available_rooms

    def get_season_multiplier(
            self,
            check_in_date: str
    ) -> float:
        check_in = datetime.strptime(
            check_in_date,
            '%Y-%m-%d'
        )

        month = check_in.month

        if month in [6, 7, 8, 12, 1, 2]:
            return 1.20

        return 1.0

    def calculate_total_booking(
            self,
            room_number: int,
            nights: int,
            check_in_date: str
    ) -> float:
        room = self.find_room(room_number)

        if room is None:
            return 0.0

        regular_price = room.calculate_price(nights)
        season_multiplier = self.get_season_multiplier(
            check_in_date
        )

        return regular_price * season_multiplier

    def book_room_for_customer(
            self,
            customer: Customer,
            room_number: int,
            nights: int,
            check_in_date: str,
            check_out_date: str,
            points_to_use: int = 0
    ) -> bool:
        room = self.find_room(room_number)

        if room is None:
            self.last_booking_message = (
                'Booking failed. Room not found.'
            )
            return False

        if not self.is_room_available_for_dates(
                room_number,
                check_in_date,
                check_out_date
        ):
            self.last_booking_message = (
                'Booking failed. The room is already booked '
                'for the selected dates.'
            )
            return False

        if customer.number_of_guests > room.max_guests:
            self.last_booking_message = (
                'Booking failed. The room capacity '
                'is not sufficient.'
            )
            return False

        if nights <= 0:
            self.last_booking_message = (
                'Booking failed. Check-out date must '
                'be later than check-in date.'
            )
            return False

        original_price = self.calculate_total_booking(
            room_number,
            nights,
            check_in_date
        )

        discount_percent = customer.calculate_discount(
            points_to_use
        )

        if discount_percent == 0:
            points_to_use = 0

        discount_amount = (
                original_price
                * discount_percent
                / 100
        )

        final_price = original_price - discount_amount

        if not customer.pay_for_booking(final_price):
            self.last_booking_message = (
                'Booking failed. The customer does '
                'not have enough budget.'
            )
            return False

        if points_to_use > 0:
            customer.use_reward_points(points_to_use)

        room.book_room()
        customer.add_room(room)
        earned_points = customer.add_reward_points()

        booking = Booking(
            customer,
            room,
            nights,
            original_price,
            discount_percent,
            points_to_use,
            final_price,
            check_in_date,
            check_out_date,
            earned_points
        )

        customer.bookings.append(booking)

        self.log_booking(
            customer,
            room,
            final_price,
            booking,
            earned_points
        )

        self.last_booking_message = (
            'Booking was successful.'
        )

        return True

    def log_booking(
            self,
            customer: Customer,
            room: Room,
            total_price: float,
            booking: Booking,
            earned_points: int
    ):
        self.bookings_log.append(booking)

        logging.info(
            'Booking created - '
            'Customer: %s, '
            'Room: %s, '
            'Type: %s, '
            'Check-in: %s, '
            'Check-out: %s, '
            'Nights: %s, '
            'Guests: %s, '
            'Original price: %.2f GEL, '
            'Discount: %.0f%%, '
            'Points used: %s, '
            'Final price: %.2f GEL, '
            'Points earned: %s',
            customer.name,
            room.room_number,
            room.room_type,
            booking.check_in_date,
            booking.check_out_date,
            booking.nights,
            customer.number_of_guests,
            booking.original_price,
            booking.discount_percent,
            booking.points_used,
            total_price,
            earned_points
        )

    def cancel_booking(
            self,
            customer: Customer,
            room_number: int
    ):
        for booking in reversed(self.bookings_log):
            if (
                    booking.customer == customer
                    and booking.room.room_number == room_number
                    and booking.booking_status == 'Confirmed'
            ):
                booking.cancel_booking()
                customer.remove_room(booking.room)
                customer.budget += booking.final_price
                customer.reward_points = max(
                    0,
                    customer.reward_points - booking.earned_points
                )

                room_has_active_booking = any(
                    current_booking.room.room_number == room_number
                    and current_booking.booking_status == 'Confirmed'
                    for current_booking in self.bookings_log
                )

                if not room_has_active_booking:
                    booking.room.release_room()

                logging.info(
                    'Booking cancelled - '
                    'Customer: %s, '
                    'Room: %s, '
                    'Type: %s, '
                    'Check-in: %s, '
                    'Check-out: %s, '
                    'Refunded: %.2f GEL',
                    customer.name,
                    booking.room.room_number,
                    booking.room.room_type,
                    booking.check_in_date,
                    booking.check_out_date,
                    booking.final_price
                )

                return (
                    True,
                    f'Booking was cancelled successfully. '
                    f'{booking.final_price:.2f} GEL was refunded.'
                )

        return (
            False,
            'Booking cancellation failed. '
            'No active booking was found for this room.'
        )


def create_rooms() -> list:
    rooms = []

    for room_number in range(101, 105):
        rooms.append(Room(room_number, 'Forest Deluxe', 280.0, True, 2))

    for room_number in range(105, 108):
        rooms.append(Room(room_number, 'Forest Deluxe', 330.0, True, 3))

    for room_number in range(108, 111):
        rooms.append(Room(room_number, 'Forest Deluxe', 380.0, True, 4))

    for room_number in range(111, 116):
        rooms.append(Room(room_number, 'Whisper Suite', 420.0, True, 2))

    for room_number in range(116, 121):
        rooms.append(Room(room_number, 'Whisper Suite', 470.0, True, 3))

    for room_number in range(121, 126):
        rooms.append(Room(room_number, 'Whisper Suite', 520.0, True, 4))

    for room_number in range(126, 130):
        rooms.append(Room(room_number, 'Garden Family Room', 350.0, True, 4))

    for room_number in range(130, 134):
        rooms.append(Room(room_number, 'Garden Family Room', 400.0, True, 5))

    return rooms


def calculate_nights(
        check_in_date: str,
        check_out_date: str
) -> int:
    check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
    check_out = datetime.strptime(check_out_date, '%Y-%m-%d')

    return (check_out - check_in).days


def main():
    rooms = create_rooms()
    hotel = Hotel('Whisper Woods', rooms)

    print('Welcome to Whisper Woods Hotel')

    customer_name = input('Enter customer name: ')

    while True:
        try:
            customer_budget = float(
                input('Enter customer budget in GEL: ')
            )

            if customer_budget <= 0:
                print('Invalid input. Please enter a positive number.')
                continue

            break

        except ValueError:
            print('Invalid input. Please enter a valid number.')

    while True:
        try:
            number_of_guests = int(input('Enter number of guests: '))

            if number_of_guests <= 0:
                print('Number of guests must be at least 1.')
                continue

            break

        except ValueError:
            print('Please enter a valid number.')

    customer = Customer(customer_name, customer_budget, number_of_guests)

    while True:
        print('\nWhisper Woods Hotel')
        print('1. Book a room')
        print('2. Show booking summary')
        print('3. Cancel booking')
        print('4. Exit')

        choice = input('Enter your choice (1-4): ')

        if choice == '1':
            print('\nRoom types:')
            print('1. Forest Deluxe')
            print('2. Whisper Suite')
            print('3. Garden Family Room')

            while True:
                room_type_choice = input('Choose room type (1-3): ')

                if room_type_choice == '1':
                    room_type = 'Forest Deluxe'
                    break
                elif room_type_choice == '2':
                    room_type = 'Whisper Suite'
                    break
                elif room_type_choice == '3':
                    room_type = 'Garden Family Room'
                    break
                else:
                    print('Please choose 1, 2 or 3.')

            while True:
                check_in_date = input(
                    'Enter check-in date (YYYY-MM-DD): '
                )
                check_out_date = input(
                    'Enter check-out date (YYYY-MM-DD): '
                )

                try:
                    nights = calculate_nights(
                        check_in_date,
                        check_out_date
                    )

                    if nights <= 0:
                        print(
                            'Check-out date must be later '
                            'than check-in date.'
                        )
                        continue

                    break

                except ValueError:
                    print(
                        'Invalid date format. '
                        'Please use YYYY-MM-DD.'
                    )

            available_rooms = hotel.show_available_rooms(
                room_type,
                customer.number_of_guests,
                check_in_date,
                check_out_date
            )

            if not available_rooms:
                print(
                    'No available rooms were found '
                    'for the selected type and capacity.'
                )
                continue

            print('\nAvailable rooms:')

            for room in available_rooms:
                seasonal_price = hotel.calculate_total_booking(room.room_number, 1, check_in_date)
                print(
                    f'Room number: {room.room_number}, '
                    f'Room type: {room.room_type}, '
                    f'Price per night: {seasonal_price:.2f} GEL, '
                    f'Available: True, '
                    f'Max guests: {room.max_guests}'
                )

            while True:
                try:
                    room_number = int(input('\nEnter room number: '))
                except ValueError:
                    print('Please enter a valid room number.')

                    continue

                selected_room = hotel.find_room(room_number)

                if selected_room not in available_rooms:
                    print(
                        'Please choose a room from the available rooms list.'
                    )
                    continue
                break

            total_price = hotel.calculate_total_booking(
                room_number,
                nights,
                check_in_date
            )

            print(
                f'Original booking price: '
                f'{total_price:.2f} GEL'
            )

            points_to_use = 0

            if customer.reward_points >= 100:
                redeem_choice = input(
                    'Do you want to redeem reward points? '
                    '(yes/no): '
                )

                if redeem_choice == 'yes':
                    print(
                        f'Available reward points: '
                        f'{customer.reward_points}'
                    )

                    try:
                        points_to_use = int(
                            input(
                                'How many points do you want '
                                'to use? '
                            )
                        )
                    except ValueError:
                        print(
                            'Invalid points. '
                            'No points will be used.'
                        )
                        points_to_use = 0

            booking_successful = hotel.book_room_for_customer(
                customer,
                room_number,
                nights,
                check_in_date,
                check_out_date,
                points_to_use
            )

            print(f'\n{hotel.last_booking_message}')

            if booking_successful:
                print(customer.show_booking_summary())

        elif choice == '2':
            print(customer.show_booking_summary())

        elif choice == '3':
            try:
                room_number = int(
                    input('Enter the room number to cancel: ')
                )
            except ValueError:
                print('Please enter a valid room number.')
                continue

            cancellation_successful, message = hotel.cancel_booking(
                customer,
                room_number
            )

            print(message)

        elif choice == '4':
            print('Thank you for choosing Whisper Woods.')
            break

        else:
            print(
                'Invalid choice. '
                'Please enter a number from 1 to 4.'
            )


if __name__ == '__main__':
    main()
