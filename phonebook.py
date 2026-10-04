import json
from pathlib import Path


PROJECT_DIR = Path(__file__).parent
FILE_PATH = PROJECT_DIR / "contacts.json"


def show_menu():
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
    # Пустая строка перед сообщением.
    print()
    print(message)


def get_input(message):
    # Пустая строка перед приглашением ко вводу.
    print()
    answer = input(message).strip()

    # Пустая строка после ввода и разделитель.
    # Отступ после разделителя добавит следующая функция:
    # show_message(), get_input() или show_menu().
    print()
    print("-" * 30)
    return answer


def open_file(file_path):
    if not file_path.exists():
        show_message(f"Файл не найден: {file_path}")
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        contacts = json.load(file)

    if not isinstance(contacts, list):
        show_message("В файле должен находиться список контактов")
        return None

    show_message(f"Файл открыт. Загружено контактов: {len(contacts)}")
    return contacts


def save_file(contacts, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(contacts, file, ensure_ascii=False, indent=4)

    show_message(f"Контакты сохранены в файл: {file_path}")


def show_contact(contact):
    print("ID:", contact["id"])
    print("Имя:", contact["name"])
    print("Телефон:", contact["phone"])
    print("Комментарий:", contact["comment"])
    print("-" * 30)


def show_contacts(contacts):
    if not contacts:
        show_message("Контакты отсутствуют")
        return

    for contact in contacts:
        show_contact(contact)


def get_next_id(contacts):
    new_id = 1

    for contact in contacts:
        if contact["id"] >= new_id:
            new_id = contact["id"] + 1

    return new_id


def create_contact(contacts):
    name = get_input("Введите имя контакта: ")

    if not name:
        show_message("Имя контакта не может быть пустым")
        return False

    phone = get_input("Введите номер телефона: ")

    if not phone:
        show_message("Номер телефона не может быть пустым")
        return False

    comment = get_input("Введите комментарий: ")

    new_contact = {
        "id": get_next_id(contacts),
        "name": name,
        "phone": phone,
        "comment": comment,
    }

    contacts.append(new_contact)
    show_message(f"Контакт создан. ID: {new_contact['id']}")
    return True


def find_contacts(contacts, query):
    found_contacts = []
    query = query.lower()

    for contact in contacts:
        name = contact["name"].lower()
        phone = contact["phone"].lower()
        comment = contact["comment"].lower()

        if query in name or query in phone or query in comment:
            found_contacts.append(contact)

    return found_contacts


def search_contacts(contacts):
    if not contacts:
        show_message("Контакты отсутствуют")
        return []

    query = get_input("Введите имя, телефон или комментарий: ")

    if not query:
        show_message("Поисковый запрос не может быть пустым")
        return []

    found_contacts = find_contacts(contacts, query)

    if not found_contacts:
        show_message("Контакты не найдены")
        return []

    show_message(f"Найдено контактов: {len(found_contacts)}")
    print()
    show_contacts(found_contacts)
    return found_contacts


def select_contact(found_contacts):
    if not found_contacts:
        return None

    selected_id = get_input("Введите ID нужного контакта: ")

    for contact in found_contacts:
        if str(contact["id"]) == selected_id:
            return contact

    show_message("Контакт с таким ID не найден")
    return None


def edit_contact(contacts):
    found_contacts = search_contacts(contacts)
    contact = select_contact(found_contacts)

    if contact is None:
        return False

    changed = False

    name = get_input("Введите новое имя или нажмите Enter: ")
    if name and name != contact["name"]:
        contact["name"] = name
        changed = True

# нужна проверка ввода, while
    phone = get_input("Введите новый номер или нажмите Enter: ")
    if phone and phone != contact["phone"]:
        contact["phone"] = phone
        changed = True

    comment = get_input("Введите новый комментарий или нажмите Enter: ")
    if comment and comment != contact["comment"]:
        contact["comment"] = comment
        changed = True

    if changed:
        show_message("Контакт изменён")
    else:
        show_message("Контакт не изменён")

    return changed


def delete_contact(contacts):
    found_contacts = search_contacts(contacts)
    contact = select_contact(found_contacts)

    if contact is None:
        return False

    answer = get_input("Удалить выбранный контакт? да/нет: ").lower()

    if answer == "да":
        contacts.remove(contact)
        show_message("Контакт удалён")
        return True

    show_message("Удаление отменено")
    return False


def main():
    contacts = None
    changed = False

    while True:
        show_menu()
        choice = get_input("Введите пункт меню: ")

        if choice in ("2", "3", "4", "5", "6", "7") and contacts is None:
            show_message(
                "Необходимо открыть файл справочника — выберите пункт 1"
            )
            continue

        if choice == "1":
            if changed:
                show_message(
                    "Необходимо сохранить изменения или выйти без сохранения"
                )
                continue

            loaded_contacts = open_file(FILE_PATH)

            if loaded_contacts is not None:
                contacts = loaded_contacts
                changed = False

        elif choice == "2":
            save_file(contacts, FILE_PATH)
            changed = False

        elif choice == "3":
            show_contacts(contacts)

        elif choice == "4":
            if create_contact(contacts):
                changed = True

        elif choice == "5":
            search_contacts(contacts)

        elif choice == "6":
            if edit_contact(contacts):
                changed = True

        elif choice == "7":
            if delete_contact(contacts):
                changed = True

        elif choice == "0":
            if changed:
                answer = get_input(
                    "Есть несохранённые изменения. Сохранить? да/нет: "
                ).lower()

                if answer == "да":
                    save_file(contacts, FILE_PATH)
                elif answer != "нет":
                    show_message("Введите «да» или «нет»")
                    continue

            show_message("Справочник закрыт")
            break

        else:
            show_message("Пункт меню отсутствует")


main()