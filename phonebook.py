"""Запуск телефонного справочника."""

from pathlib import Path

from controller import Controller
from model import FileReader, FileWriter, PhoneBook


PROJECT_DIR = Path(__file__).parent
FILE_PATH = PROJECT_DIR / "contacts.json"


def main():
    """Создать справочник и открыть меню."""
    reader = FileReader(FILE_PATH)
    writer = FileWriter(FILE_PATH)
    phonebook = PhoneBook(reader, writer)
    controller = Controller(phonebook)
    controller.run()


if __name__ == "__main__":
    main()
