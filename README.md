# Проект Yatube

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)


## Описание.
Yatube - это социальная сеть, с такими возможностями:
- Регистрация и восстановление пароля по электронной почте.
- Создание и редактирование собственных постов, возможность добавить изображение.
- Просмотр страниц других авторов.
- Комментирование других постов.
- Подписки и отписки от авторов.
- Личная страница для публикации записей.
- Группы для постов и отдельная лента для групп.
- Отдельная лента с постами авторов на которых подписан пользователь.

## Запуск проекта.

1. Клонируйте репозиторий:
```
git@github.com:IlianL/hw05_final.git
```
2. Перейдите в папку с проектом, создайте и активируйте виртуальное окружение:
```
сd hw05_final
python -m venv venv  

# для OS Lunix и MacOS
source venv/bin/activate

# для OS Windows
source venv/Scripts/activate
```
3. Установите зависимости:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
4. Выполните миграции:
```
cd yatube
python manage.py migrate
```
5. Запустите проект локально:
```
python manage.py runserver

# адрес запущенного сайта
http://127.0.0.1:8000
```
6. Создание администратора:
```
python manage.py createsuperuser

# панель администратора
http://127.0.0.1:8000/admin/
```
  
Автор: Илиан Ляпота


