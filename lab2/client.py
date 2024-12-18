import flet as ft
import requests

API_URL = "http://localhost:8000/api"  # Замените на URL вашего FastAPI сервера


def main(page: ft.Page):
    page.title = "Блоговая платформа"
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Элементы интерфейса
    username_input = ft.TextField(label="Имя пользователя", width=300)
    password_input = ft.TextField(label="Пароль", password=True, width=300)
    login_button = ft.ElevatedButton(text="Войти", on_click=lambda e: login())
    output_area = ft.Column()
    user_options = ft.Row()  # Изменено на Row для расположения в строку
    posts_list = ft.ListView(height=400)  # Установите фиксированную высоту для ListView

    # Функция для аутентификации
    def login():
        output_area.controls.clear()
        output_area.controls.append(ft.Text("Идентификация..."))
        page.update()
        username = username_input.value
        password = password_input.value
        response = requests.post(f"{API_URL}/users/login", json={"name": username, "password": password})

        if response.status_code == 200:
            user_data = response.json()
            output_area.controls.clear()
            page.update()
            set_user_options(user_data['role'])  # Устанавливаем опции для пользователя/администратора
        else:
            user_options.controls.clear()
            output_area.controls.clear()
            output_area.controls.append(ft.Text("Ошибка аутентификации!", color=ft.colors.RED))
            page.update()

    # Функция для установки опций пользователя или администратора
    def set_user_options(role):
        user_options.controls.clear()

        user_options.controls.append(ft.Text("Выберите действие:"))

        # Создание прокручиваемого контейнера для кнопок
        scrollable_container = ft.Column()

        refresh_button = ft.ElevatedButton(text="Обновить контент", on_click=lambda e: refresh_content())
        scrollable_container.controls.append(refresh_button)

        if role == 'admin':
            # Группировка кнопок в отдельные строки
            admin_buttons_row1 = ft.Row(spacing=10, controls=[
                ft.ElevatedButton(text="Добавить пост", on_click=lambda e: show_add_post_form()),
                ft.ElevatedButton(text="Редактировать пост", on_click=lambda e: show_edit_post_form()),
                ft.ElevatedButton(text="Удалить пост", on_click=lambda e: show_del_post_form())
            ])

            admin_buttons_row2 = ft.Row(spacing=10, controls=[
                ft.ElevatedButton(text="Добавить пользователя", on_click=lambda e: show_add_user_form()),
                ft.ElevatedButton(text="Редактировать пользователя", on_click=lambda e: show_edit_user_form()),
                ft.ElevatedButton(text="Удалить пользователя", on_click=lambda e: show_del_user_form()),
                ft.ElevatedButton(text="Получить рекомендации", on_click=lambda e: show_recommend_form())
            ])

            # Добавление групп кнопок в прокручиваемый контейнер
            scrollable_container.controls.extend([admin_buttons_row1, admin_buttons_row2])

        # Добавление прокручиваемого контейнера в пользовательские опции
        user_options.controls.append(scrollable_container)

        # Обновление страницы
        page.update()

    # Функция для обновления контента
    def refresh_content():
        output_area.controls.clear()
        posts_list.controls.clear()  # Очищаем список постов

        output_area.controls.append(ft.Text("Загрузка постов..."))
        page.update()

        # Получение постов с сервера
        response = requests.get(f"{API_URL}/posts/get")
        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                post_item = ft.Column([
                    ft.Text(f"Заголовок: {post['title']}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Содержимое: {post['body']}"),
                    ft.Text(f"Дополнительная информация: {post['addition']}"),
                    ft.Divider()
                ])
                posts_list.controls.append(post_item)
            output_area.controls.append(posts_list)
        else:
            output_area.controls.append(ft.Text("Ошибка при получении постов!", color=ft.colors.RED))

        page.update()

    # Функция для отображения формы добавления поста
    def show_add_post_form():
        output_area.controls.clear()
        page.update()
        title_input = ft.TextField(label="Заголовок поста", width=300)
        body_input = ft.TextField(label="Содержимое поста", width=300)
        addition_input = ft.TextField(label="Приложение поста", width=300)
        submit_button = ft.ElevatedButton(text="Добавить пост",
                                          on_click=lambda e: add_post(title_input.value, body_input.value,
                                                                      addition_input.value))

        output_area.controls.append(title_input)
        output_area.controls.append(body_input)
        output_area.controls.append(addition_input)
        output_area.controls.append(submit_button)
        page.update()

    # Функция для добавления поста
    def add_post(title, body, addition):
        if not title or not body or not addition:
            output_area.controls.append(ft.Text("Пожалуйста, заполните все поля!", color=ft.colors.RED))
            page.update()
            return

        response = requests.post(f"{API_URL}/posts/add", json={"title": title, "body": body, "addition": addition})

        if response.status_code == 200:
            output_area.controls.clear()
            output_area.controls.append(ft.Text("Пост успешно добавлен!"))
        else:
            output_area.controls.append(ft.Text("Ошибка при добавлении поста!", color=ft.colors.RED))

        page.update()

    def show_edit_post_form():
        output_area.controls.clear()
        page.update()
        id_input = ft.TextField(label="Идентификатор поста", width=300)
        title_input = ft.TextField(label="Заголовок поста", width=300)
        body_input = ft.TextField(label="Содержимое поста", width=300)
        addition_input = ft.TextField(label="Приложение поста", width=300)
        submit_button = ft.ElevatedButton(text="Редактировать пост",
                                          on_click=lambda e: edit_post(id_input.value, title_input.value,
                                                                       body_input.value,
                                                                       addition_input.value))

        output_area.controls.append(id_input)
        output_area.controls.append(title_input)
        output_area.controls.append(body_input)
        output_area.controls.append(addition_input)
        output_area.controls.append(submit_button)
        page.update()

    # Функция для сохранения изменений поста
    def edit_post(post_id, title, body, addition):
        if not post_id or not title or not body or not addition:
            output_area.controls.append(ft.Text("Пожалуйста, заполните все поля!", color=ft.colors.RED))
            page.update()
            return

        response = requests.post(f"{API_URL}/posts/edit",
                                 json={"id": post_id, "title": title, "body": body, "addition": addition})

        if response.status_code == 200:
            output_area.controls.clear()
            output_area.controls.append(ft.Text("Пост успешно редактирован!"))
        else:
            error_message = response.json().get("detail")
            output_area.controls.append(ft.Text(f"Ошибка при редактировании поста: <{error_message}>!", color=ft.colors.RED))

        page.update()

    def show_del_post_form():
        output_area.controls.clear()
        page.update()
        id_input = ft.TextField(label="Идентификатор поста", width=300)
        submit_button = ft.ElevatedButton(text="Удалить пост",
                                          on_click=lambda e: del_post(id_input.value))

        output_area.controls.append(id_input)
        output_area.controls.append(submit_button)
        page.update()

    # Функция для сохранения изменений поста
    def del_post(post_id):
        if not post_id:
            output_area.controls.append(ft.Text("Пожалуйста, заполните все поля!", color=ft.colors.RED))
            page.update()
            return

        response = requests.delete(f"{API_URL}/posts/del", json={"id": post_id})

        if response.status_code == 200:
            output_area.controls.clear()
            output_area.controls.append(ft.Text("Пост успешно удален!"))
        else:
            error_message = response.json().get("detail")
            output_area.controls.append(ft.Text(f"Ошибка при удалении поста: <{error_message}>!", color=ft.colors.RED))

        page.update()

    def show_add_user_form():
        output_area.controls.clear()
        page.update()
        name_input = ft.TextField(label="Имя пользователя", width=300)
        password_input = ft.TextField(label="Пароль пользователя", width=300)
        role_input = ft.Dropdown(
            label="Роль пользователя",
            options=[
                ft.dropdown.Option("user"),
                ft.dropdown.Option("admin")
            ],
            width=300
        )
        submit_button = ft.ElevatedButton(text="Добавить пользователя",
                                          on_click=lambda e: add_user(name_input.value, password_input.value,
                                                                      role_input.value))

        output_area.controls.append(name_input)
        output_area.controls.append(password_input)
        output_area.controls.append(role_input)
        output_area.controls.append(submit_button)
        page.update()

    # Функция для добавления поста
    def add_user(name, password, role):
        if not name or not password or not role:
            output_area.controls.append(ft.Text("Пожалуйста, заполните все поля!", color=ft.colors.RED))
            page.update()
            return

        response = requests.post(f"{API_URL}/users/add", json={"name": name, "password": password, "role": role})

        if response.status_code == 200:
            output_area.controls.clear()
            output_area.controls.append(ft.Text("Пользователь добавлен!"))
        else:
            error_message = response.json().get("detail")
            output_area.controls.append(ft.Text(f"Ошибка при добавлении пользователя: <{error_message}>!", color=ft.colors.RED))

        page.update()

    def show_edit_user_form():
        output_area.controls.clear()
        page.update()
        id_input = ft.TextField(label="Идентификатор пользователя", width=300)
        name_input = ft.TextField(label="Имя пользователя", width=300)
        password_input = ft.TextField(label="Пароль пользователя", width=300)
        role_input = ft.Dropdown(
            label="Роль пользователя",
            options=[
                ft.dropdown.Option("user"),
                ft.dropdown.Option("admin")
            ],
            width=300
        )
        submit_button = ft.ElevatedButton(text="Редактировать пользователя",
                                          on_click=lambda e: edit_user(id_input.value, name_input.value,
                                                                       password_input.value,
                                                                       role_input.value))

        output_area.controls.append(id_input)
        output_area.controls.append(name_input)
        output_area.controls.append(password_input)
        output_area.controls.append(role_input)
        output_area.controls.append(submit_button)
        page.update()

    # Функция для добавления поста
    def edit_user(id, name, password, role):
        if not id or not name or not password or not role:
            output_area.controls.append(ft.Text("Пожалуйста, заполните все поля!", color=ft.colors.RED))
            page.update()
            return

        response = requests.post(f"{API_URL}/users/edit", json={"id": id, "name": name, "password": password, "role": role})

        if response.status_code == 200:
            output_area.controls.clear()
            output_area.controls.append(ft.Text("Пользователь успешно редактирован!"))
        else:
            error_message = response.json().get("detail")
            output_area.controls.append(ft.Text(f"Ошибка при редактировании пользователя: <{error_message}>!", color=ft.colors.RED))

        page.update()

    def show_del_user_form():
        output_area.controls.clear()
        page.update()
        id_input = ft.TextField(label="Идентификатор пользователя", width=300)
        submit_button = ft.ElevatedButton(text="Удалить пользователя",
                                          on_click=lambda e: del_user(id_input.value))

        output_area.controls.append(id_input)
        output_area.controls.append(submit_button)
        page.update()

    # Функция для добавления поста
    def del_user(id):
        if not id:
            output_area.controls.append(ft.Text("Пожалуйста, заполните все поля!", color=ft.colors.RED))
            page.update()
            return

        response = requests.delete(f"{API_URL}/users/del", json={"id": id})

        if response.status_code == 200:
            output_area.controls.clear()
            output_area.controls.append(ft.Text("Пользователь успешно удален!"))
        else:
            error_message = response.json().get("detail")
            output_area.controls.append(ft.Text(f"Ошибка при удалении пользователя: <{error_message}>!", color=ft.colors.RED))

        page.update()

    page.add(username_input, password_input, login_button, user_options, output_area)


    def show_recommend_form():
        output_area.controls.clear()
        page.update()
        visit_input = ft.TextField(label="Желаемое число посещений", width=300)
        submit_button = ft.ElevatedButton(text="Получить рекомендацию",
                                          on_click=lambda e: recommend(visit_input.value))

        output_area.controls.append(visit_input)
        output_area.controls.append(submit_button)
        page.update()

    # Функция для добавления поста
    def recommend(visit):
        if not visit:
            output_area.controls.append(ft.Text("Пожалуйста, заполните все поля!", color=ft.colors.RED))
            page.update()
            return

        response = requests.post(f"{API_URL}/recommend", json={"visit": visit})

        if response.status_code == 200:
            output_area.controls.clear()
            message = response.json().get("message")
            output_area.controls.append(ft.Text(f"{message}"))
        else:
            error_message = response.json().get("detail")
            output_area.controls.append(ft.Text(f"Ошибка при составлении рекомендации: <{error_message}>!", color=ft.colors.RED))

        page.update()

    page.add(username_input, password_input, login_button, user_options, output_area)

ft.app(target=main)
