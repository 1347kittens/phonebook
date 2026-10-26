import json
from pathlib import Path

import pytest

from model import Contact, ContactError, FileError, FileReader, FileWriter
from model import PhoneBook, PhonebookError


@pytest.fixture
def file_path():
    # Отдельный файл для тестов, не рабочий contacts.json.
    path = Path(__file__).parent / "test_contacts.json"
    path.unlink(missing_ok=True)
    return path


@pytest.fixture
def phonebook(file_path):
    book = PhoneBook(FileReader(file_path), FileWriter(file_path))
    book.contacts = [
        Contact(1, "Анна", "+79991111111", "Работа"),
        Contact(3, "Боб", "1234567890", "Автосервис"),
    ]
    return book


class TestPhoneBook:
    @pytest.mark.parametrize(
        "name, phone",
        [
            ("Иван", "1234567890"),
            ("Анна-Мария", "+7 (999) 222-33-44"),
            ("Bob Smith", "8-999-222-33-44"),
        ],
    )
    def test_add(self, phonebook, name, phone):
        contact = phonebook.add(name, phone, "Друг")
        assert len(phonebook.contacts) == 3
        assert contact.id == 4
        assert contact.name == name
        assert contact.phone == phone
        assert contact.comment == "Друг"
        assert phonebook.changed is True

    @pytest.mark.parametrize(
        "name, phone, comment",
        [
            ("", "123", ""),
            ("   ", "123", ""),
            (None, "123", ""),
            ("Анна", "", ""),
            ("Анна", 123, ""),
            ("Анна", "123", None),
        ],
    )
    def test_add_error(self, phonebook, name, phone, comment):
        with pytest.raises(ContactError):
            phonebook.add(name, phone, comment)
        assert len(phonebook.contacts) == 2
        assert phonebook.changed is False

    def test_add_empty_book(self, phonebook):
        phonebook.contacts = []
        contact = phonebook.add("Иван", "123", "")
        assert contact.id == 1

    @pytest.mark.parametrize(
        "query, expected_id",
        [
            ("Анна", 1),
            ("АННА", 1),
            ("1111111", 1),
            ("работа", 1),
            ("сервис", 3),
        ],
    )
    def test_find(self, phonebook, query, expected_id):
        found = phonebook.find(query)
        assert len(found) == 1
        assert found[0].id == expected_id

    def test_find_nothing(self, phonebook):
        assert phonebook.find("Несуществующий контакт") == []

    def test_common_search(self, phonebook):
        # Совпадение в имени Анна и в комментарии Автосервис.
        found = phonebook.find("а")
        assert len(found) == 2
        assert found[0].id == 1
        assert found[1].id == 3

    def test_find_same_names(self, phonebook):
        phonebook.add("Анна", "456", "Семья")
        assert len(phonebook.find("Анна")) == 2

    @pytest.mark.parametrize("query", ["", "   ", None, 123])
    def test_find_error(self, phonebook, query):
        with pytest.raises(ContactError):
            phonebook.find(query)

    def test_edit(self, phonebook):
        contact = phonebook.contacts[0]
        assert phonebook.edit(contact, "Мария", "456", "Друг") is True
        assert contact.to_dict() == {
            "id": 1,
            "name": "Мария",
            "phone": "456",
            "comment": "Друг",
        }
        assert phonebook.changed is True

    def test_edit_empty_input(self, phonebook):
        contact = phonebook.contacts[0]
        assert phonebook.edit(contact, "", "", "") is False
        assert contact.name == "Анна"
        assert contact.phone == "+79991111111"
        assert contact.comment == "Работа"
        assert phonebook.changed is False

    @pytest.mark.parametrize("phone", [123, None, "   "])
    def test_edit_error(self, phonebook, phone):
        contact = phonebook.contacts[0]
        with pytest.raises(ContactError):
            phonebook.edit(contact, "Мария", phone, "")
        # При неверном телефоне имя тоже не должно измениться.
        assert contact.name == "Анна"
        assert contact.phone == "+79991111111"
        assert phonebook.changed is False

    def test_delete(self, phonebook):
        contact = phonebook.select(phonebook.find("Боб"), "3")
        phonebook.delete(contact)
        assert len(phonebook.contacts) == 1
        assert phonebook.find("Боб") == []
        assert phonebook.changed is True

    @pytest.mark.parametrize("selected_id", ["999", "abc", ""])
    def test_delete_wrong_id(self, phonebook, selected_id):
        with pytest.raises(ContactError):
            contact = phonebook.select(phonebook.find("Анна"), selected_id)
            phonebook.delete(contact)
        assert len(phonebook.contacts) == 2
        assert phonebook.changed is False

    def test_delete_twice(self, phonebook):
        contact = phonebook.contacts[0]
        phonebook.delete(contact)
        with pytest.raises(ContactError):
            phonebook.delete(contact)

    def test_before_open(self, file_path):
        book = PhoneBook(FileReader(file_path), FileWriter(file_path))
        with pytest.raises(PhonebookError):
            book.save()
        with pytest.raises(PhonebookError):
            book.add("Анна", "123", "")


class TestFiles:
    def test_save_and_open(self, phonebook, file_path):
        phonebook.add("Иван", "456", "Семья")
        phonebook.edit(phonebook.contacts[0], "Мария", "", "")
        phonebook.delete(phonebook.contacts[1])
        phonebook.save()
        assert phonebook.changed is False

        # Другой справочник читает файл, который сохранил первый.
        other = PhoneBook(FileReader(file_path), FileWriter(file_path))
        assert other.open() == 2
        assert other.contacts[0].name == "Мария"
        assert other.contacts[0].phone == "+79991111111"
        assert other.contacts[1].to_dict() == {
            "id": 4,
            "name": "Иван",
            "phone": "456",
            "comment": "Семья",
        }
        file_path.unlink()

    def test_empty_file_list(self, file_path):
        FileWriter(file_path).write([])
        assert FileReader(file_path).read() == []
        file_path.unlink()

    def test_missing_file(self, file_path):
        with pytest.raises(FileError, match="Не удалось открыть файл"):
            FileReader(file_path).read()

    @pytest.mark.parametrize("text", ["", "{", "не json"])
    def test_broken_json(self, file_path, text):
        file_path.write_text(text, encoding="utf-8")
        with pytest.raises(FileError):
            FileReader(file_path).read()
        file_path.unlink()

    @pytest.mark.parametrize(
        "data",
        [
            {},
            [123],
            [{"id": 1, "name": "Анна"}],
            [{"id": 1, "name": "", "phone": "123", "comment": ""}],
            [{"id": 1, "name": "Анна", "phone": 123, "comment": ""}],
        ],
    )
    def test_invalid_file(self, file_path, data):
        file_path.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(FileError):
            FileReader(file_path).read()
        file_path.unlink()

    def test_duplicate_id(self, file_path):
        data = [
            {"id": 1, "name": "Анна", "phone": "123", "comment": ""},
            {"id": 1, "name": "Боб", "phone": "456", "comment": ""},
        ]
        file_path.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(FileError):
            FileReader(file_path).read()
        file_path.unlink()

    def test_save_error(self, phonebook, file_path):
        phonebook.add("Иван", "123", "")
        # Такого каталога нет, поэтому сохранить файл не получится.
        phonebook.writer = FileWriter(file_path / "contacts.json")
        with pytest.raises(FileError):
            phonebook.save()
        assert phonebook.changed is True
