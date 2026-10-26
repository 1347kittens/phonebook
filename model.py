"""Контакты, справочник и работа с файлом."""

import json


class PhonebookError(Exception):
    """Ошибка, о которой можно сообщить пользователю."""


class FileError(PhonebookError):
    """Ошибка чтения, записи или содержимого файла."""


class ContactError(PhonebookError):
    """Ошибка данных или выбора контакта."""


class Contact:
    """Один контакт справочника."""

    def __init__(self, contact_id, name, phone, comment):
        if type(contact_id) is not int or contact_id < 1:
            raise ContactError("ID должен быть положительным целым числом")
        if not isinstance(name, str) or not name.strip():
            raise ContactError("Имя должно быть непустой строкой")
        if not isinstance(phone, str) or not phone.strip():
            raise ContactError("Телефон должен быть непустой строкой")
        if not isinstance(comment, str):
            raise ContactError("Комментарий должен быть строкой")
        self.id = contact_id
        self.name = name.strip()
        self.phone = phone.strip()
        self.comment = comment.strip()

    def to_dict(self):
        """Подготовить контакт для записи в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "comment": self.comment,
        }


class FileReader:
    """Читает список контактов из JSON-файла."""

    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        """Вернуть проверенные контакты, не меняя текущий справочник."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise FileError(f"Не удалось открыть файл: {error}")

        if not isinstance(data, list):
            raise FileError("В файле должен находиться список контактов")

        contacts = []
        used_ids = []
        for item in data:
            if not isinstance(item, dict):
                raise FileError("Каждый контакт должен быть словарём")
            for key in ("id", "name", "phone", "comment"):
                if key not in item:
                    raise FileError(f"В контакте отсутствует поле {key}")

            contact_id = item["id"]
            if type(contact_id) is not int or contact_id < 1 or contact_id in used_ids:
                raise FileError(
                    "ID контактов должны быть уникальными положительными числами"
                )
            if (
                not isinstance(item["name"], str)
                or not item["name"].strip()
                or not isinstance(item["phone"], str)
                or not item["phone"].strip()
                or not isinstance(item["comment"], str)
            ):
                raise FileError("Неверные данные имени, телефона или комментария")

            used_ids.append(contact_id)
            contacts.append(
                Contact(contact_id, item["name"], item["phone"], item["comment"])
            )

        return contacts


class FileWriter:
    """Сохраняет список контактов в JSON-файл."""

    def __init__(self, file_path):
        self.file_path = file_path

    def write(self, contacts):
        """Записать контакты в файл."""
        if not isinstance(contacts, list):
            raise FileError("Для сохранения нужен список контактов")
        data = []
        for contact in contacts:
            if not isinstance(contact, Contact):
                raise FileError("Список должен содержать объекты Contact")
            data.append(contact.to_dict())

        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except (OSError, UnicodeError) as error:
            raise FileError(f"Не удалось сохранить файл: {error}")


class PhoneBook:
    """Хранит контакты и изменения между открытием и сохранением файла."""

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.contacts = None
        self.changed = False

    def check_opened(self):
        """Не работать с контактами, пока файл не открыт."""
        if self.contacts is None:
            raise PhonebookError("Сначала откройте файл справочника")

    def open(self):
        """Загрузить контакты из файла."""
        self.contacts = self.reader.read()
        self.changed = False
        return len(self.contacts)

    def save(self):
        """Сохранить контакты и сбросить отметку об изменениях."""
        self.check_opened()
        self.writer.write(self.contacts)
        self.changed = False

    def add(self, name, phone, comment):
        """Добавить контакт и вернуть его."""
        self.check_opened()

        next_id = 1
        for contact in self.contacts:
            if contact.id >= next_id:
                next_id = contact.id + 1

        contact = Contact(next_id, name, phone, comment)
        self.contacts.append(contact)
        self.changed = True
        return contact

    def find(self, query):
        """Найти контакты по имени, номеру или комментарию."""
        self.check_opened()
        if not isinstance(query, str) or not query.strip():
            raise ContactError("Поисковый запрос должен быть непустой строкой")
        found = []
        query = query.strip().lower()
        for contact in self.contacts:
            if (
                query in contact.name.lower()
                or query in contact.phone.lower()
                or query in contact.comment.lower()
            ):
                found.append(contact)
        return found

    def select(self, found, selected_id):
        """Выбрать один контакт среди найденных."""
        self.check_opened()
        for contact in found:
            if str(contact.id) == selected_id:
                return contact
        raise ContactError("Контакт с таким ID среди найденных не найден")

    def edit(self, contact, name, phone, comment):
        """Обновить поля; пустой ввод оставляет прежнее значение."""
        self.check_opened()
        if contact not in self.contacts:
            raise ContactError("Контакт не найден в справочнике")

        if name == "":
            name = contact.name
        if phone == "":
            phone = contact.phone
        if comment == "":
            comment = contact.comment

        # Сначала проверяем все поля. Ошибка не должна менять контакт частично.
        updated = Contact(contact.id, name, phone, comment)
        if updated.to_dict() == contact.to_dict():
            return False
        contact.name = updated.name
        contact.phone = updated.phone
        contact.comment = updated.comment
        self.changed = True
        return True

    def delete(self, contact):
        """Удалить контакт."""
        self.check_opened()
        if contact not in self.contacts:
            raise ContactError("Контакт не найден в справочнике")
        self.contacts.remove(contact)
        self.changed = True
