"""Вывод сообщений и ввод данных пользователем."""


def show_menu():
    """Показать меню справочника."""
    print()
    print("-" * 30)
    print("Телефонный справочник")
    print("1. Открыть файл")
    print("2. Сохранить файл")
    print("3. Показать все контакты")
    print("4. Создать контакт")
    print("5. Найти контакт")
    print("6. Изменить контакт")
    print("7. Удалить контакт")
    print("0. Выход")
    print("-" * 30)


def show_message(message):
    """Вывести сообщение с отступом."""
    print()
    print(message)


def get_input(message):
    """Считать строку и отделить ввод от следующего сообщения."""
    print()
    answer = input(message).strip()
    print()
    print("-" * 30)
    return answer


def show_contact(contact):
    """Показать один контакт."""
    print("ID:", contact.id)
    print("Имя:", contact.name)
    print("Телефон:", contact.phone)
    print("Комментарий:", contact.comment)
    print("-" * 30)


def show_contacts(contacts):
    """Показать список контактов."""
    if not contacts:
        show_message("Контакты отсутствуют")
        return
    print()
    for contact in contacts:
        show_contact(contact)
