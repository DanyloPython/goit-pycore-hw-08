import pickle
from collections import UserDict
from datetime import datetime, timedelta

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    
def input_error(func): 
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Контакт не знайдено."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Відсутній аргумент. Будь ласка, перевірте свої дані."
    return wrapper

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону повинен містити 10 цифр.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Неправильний формат дати. Використовуйте DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return
        raise ValueError("Телефон не знайдено.")

    def delete_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                return
        raise ValueError("Телефон не знайдено.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        now = datetime.now()
        one_week_ahead = now + timedelta(days=7)
        for record in self.data.values():
            if record.birthday and now <= record.birthday.value <= one_week_ahead:
                upcoming_birthdays.append(record.name.value)
        return upcoming_birthdays


def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    if phone:
        record.add_phone(phone)
    return message


def change_contact(args, book):
    if len(args) != 2:
        raise IndexError
    name, phone = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.edit_phone(record.phones[0].value, phone)
    return "Контакт оновлено."


def show_phone(args, book):
    if len(args) != 1:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    return ', '.join(phone.value for phone in record.phones)


def add_birthday(args, book):
    if len(args) != 2:
        raise IndexError
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise ValueError(f"Контакт {name} не знайдено.")
    record.add_birthday(birthday)
    return f"День народження додано до контакту {name}."


def show_birthday(args, book):
    if len(args) != 1:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if record is None or record.birthday is None:
        raise ValueError(f"День народження для контакту {name} не знайдено.")
    return record.birthday.value.strftime("%d.%m.%Y")


def birthdays(book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "Ніяких днів народження в найближчий тиждень."
    return "\n".join(upcoming_birthdays)

def main():
    book = load_data()
    print("Ласкаво просимо до бота-помічника!")
    try:
        while True:
            user_input = input("Введіть команду: ")
            command, args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("До побачення!")
                break
            elif command == "hello":
                print("Чим я можу вам допомогти?")
            elif command == "add":
                print(add_contact(args, book))
            elif command == "change":
                print(change_contact(args, book))
            elif command == "phone":
                print(show_phone(args, book))
            elif command == "all":
                for record in book.values():
                    print(record)
            elif command == "add-birthday":
                print(add_birthday(args, book))
            elif command == "show-birthday":
                print(show_birthday(args, book))
            elif command == "birthdays":
                print(birthdays(book))
            else:
                print("Неправильна команда.")
    finally:
        save_data(book)
    
if __name__ == "__main__":
    main()
