"""Меню и управление действиями пользователя."""

from model import ContactError, PhonebookError
from view import get_input, show_contacts, show_menu, show_message


class Controller:
    """Связывает ввод и вывод со справочником."""

    def __init__(self, phonebook):
        self.phonebook = phonebook

    def search(self):
        """Запросить строку поиска и показать найденные контакты."""
        if not self.phonebook.contacts:
            show_message("Контакты отсутствуют")
            return []
        query = get_input("Введите имя, телефон или комментарий: ")
        found = self.phonebook.find(query)
        if not found:
            show_message("Контакты не найдены")
            return []
        show_message(f"Найдено контактов: {len(found)}")
        show_contacts(found)
        return found

    def choose_contact(self):
        """Найти контакт и выбрать его по ID среди результатов поиска."""
        found = self.search()
        if not found:
            return None
        selected_id = get_input("Введите ID нужного контакта: ")
        return self.phonebook.select(found, selected_id)

    def create(self):
        """Спросить данные нового контакта."""
        name = get_input("Введите имя контакта: ")
        if not name:
            raise ContactError("Имя контакта не может быть пустым")
        phone = get_input("Введите номер телефона: ")
        if not phone:
            raise ContactError("Номер телефона не может быть пустым")
        comment = get_input("Введите комментарий: ")
        contact = self.phonebook.add(name, phone, comment)
        show_message(f"Контакт создан. ID: {contact.id}")

    def edit(self):
        """Найти контакт и изменить введённые поля."""
        contact = self.choose_contact()
        if contact is None:
            return
        name = get_input("Введите новое имя или нажмите Enter: ")
        phone = get_input("Введите новый номер или нажмите Enter: ")
        comment = get_input("Введите новый комментарий или нажмите Enter: ")
        if self.phonebook.edit(contact, name, phone, comment):
            show_message("Контакт изменён")
        else:
            show_message("Контакт не изменён")

    def delete(self):
        """Найти контакт и спросить подтверждение удаления."""
        contact = self.choose_contact()
        if contact is None:
            return
        answer = get_input("Удалить выбранный контакт? да/нет: ").lower()
        if answer == "да":
            self.phonebook.delete(contact)
            show_message("Контакт удалён")
        elif answer == "нет":
            show_message("Удаление отменено")
        else:
            show_message("Введите «да» или «нет». Удаление отменено")

    def exit(self):
        """При изменениях предложить сохранение перед выходом."""
        if self.phonebook.changed:
            answer = get_input(
                "Есть несохранённые изменения. Сохранить? да/нет: "
            ).lower()
            if answer == "да":
                self.phonebook.save()
            elif answer != "нет":
                show_message("Введите «да» или «нет»")
                return False
        show_message("Справочник закрыт")
        return True

    def run(self):
        """Показывать меню и выполнять выбранное действие."""
        running = True
        while running:
            show_menu()
            choice = get_input("Введите пункт меню: ")

            if choice in ("2", "3", "4", "5", "6", "7") \
                    and self.phonebook.contacts is None:
                show_message(
                    "Необходимо открыть файл справочника — выберите пункт 1"
                )
                continue

            try:
                if choice == "1":
                    if self.phonebook.changed:
                        show_message(
                            "Сначала сохраните изменения или выйдите без сохранения"
                        )
                        continue
                    count = self.phonebook.open()
                    show_message(f"Файл открыт. Загружено контактов: {count}")
                elif choice == "2":
                    self.phonebook.save()
                    show_message("Контакты сохранены")
                elif choice == "3":
                    show_contacts(self.phonebook.contacts)
                elif choice == "4":
                    self.create()
                elif choice == "5":
                    self.search()
                elif choice == "6":
                    self.edit()
                elif choice == "7":
                    self.delete()
                elif choice == "0":
                    running = not self.exit()
                else:
                    show_message("Пункт меню отсутствует")
            except PhonebookError as error:
                show_message(error)
