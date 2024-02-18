import datetime
import aiohttp
import asyncio

from .types import Mark, Lesson, Homework, Message
from . import exceptions
from bs4 import BeautifulSoup
from enum import Enum

base = "https://edu.gounn.ru:443/apiv3/"
dev_key = "Your dev_key here"
out_format = "json"
vendor = "edu"


class RequestType(Enum):
    get = 0
    post = 1


class Methods:
    authorize = "auth"
    get_rules = "getrules"
    get_marks = "getmarks"
    get_periods = "getperiods"
    get_diary = "getdiary"
    get_final_marks = "getfinalassessments"
    get_board_notices = "getboardnotices"
    get_board_notice_info = "getboardnoticeinfo"
    get_messages = "getmessages"
    get_message_info = "getmessageinfo"
    get_message_receivers = "getmessagereceivers"


class Student:
    __slots__ = (
        "auth_token", "token_expires", "student_num", "name", "full_school_name", "student_class", "current_period",
        "all_periods", "city", "email_confirmed")

    def __init__(self, **kwargs):
        self.auth_token = kwargs.get('auth_token')
        self.token_expires = kwargs.get('token_expires')
        self.student_num = kwargs.get('student_num')
        self.name = kwargs.get('name')
        self.full_school_name = kwargs.get('school')
        self.student_class = kwargs.get('student_class')
        self.current_period = kwargs.get('current_period')
        self.all_periods = kwargs.get('all_periods', [])
        self.city = kwargs.get('city')
        self.email_confirmed = kwargs.get('email_confirmed')

    async def auto_fill_data(self, all_periods_as_dict: bool = True) -> bool:
        """
        Автоматически заполняет все поля класса (Информация берётся из сервера дневника.
Заполняемые поля: student_num, name, full_school_name, student_class, current_period, all_periods, city)


        :return: Вернёт True если все запросы к серверу дневника были успешными, и программа смогла заполнить все поля класса Student. Иначе вернёт False.
        """
        await self.get_rules()
        await self.get_periods(all_periods_as_dict)
        return self

    async def authorization(self, login: str, password: str) -> str:
        """
        Выполняет авторизацию на сервере дневника по логину и паролю.

        :param login: Логин ученика:
        :param password: Пароль ученика:
        :return: При успешном выполнении запроса, возвращает токен
        """

        request = await self._make_request(Methods.authorize)
        response = await self._order(request, RequestType.post, {"login": login, "password": password})

        if int(response['state']) == 200:
            self.auth_token = response['result']['token']
            self.token_expires = response['result']['expires']
            return response['result']['token']
        else:
            if response['result']['errorCode'] == "login":
                raise exceptions.DataError()
            else:
                raise exceptions.ServerAnswerError(response['error'])

    async def get_children(self) -> dict:
        """
        Получение всех учеников, относящихся к данному аккаунту

        :return: Возвращает имена и коды учеников
        """
        request = await self._make_request(Methods.get_rules, auth_token=self.auth_token)
        response = await self._order(request, RequestType.get)
        if response['state'] == 200:
            if bool(response['result']['relations'].get('students', False)):
                if len(response['result']['relations']['students']) > 0:
                    results = []
                    for k in response['result']['relations']['students'].keys():
                        results.append((response['result']['relations']['students'][k]['title'], k))
                    return results
                else:
                    return []

            return []
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_rules(self, key=None) -> dict:
        """
        Получение всей информации об ученике и её заполнение в поля класса

        :param key: Если аккаунт принадлежит родителю, то нужно указать key конкретного ребёнка. Список детей можно получить функцией get_children
        :return: Возвращает имя, класс, название школы, номер ученика и его город
        """
        request = await self._make_request(Methods.get_rules, auth_token=self.auth_token)
        response = await self._order(request, RequestType.get)
        if response['state'] == 200:
            if bool(response['result']['relations'].get('students', False)):
                self.email_confirmed = response['result']['email_confirmed']
                if len(response['result']['relations']['students']) > 0:
                    if not self.student_num:
                        if not key:
                            for k in response['result']['relations']['students'].keys():
                                self.student_num = k
                                break
                        else:
                            if not isinstance(key, str):
                                key = str(key)
                            if response['result']['relations']['students'].get(key):
                                self.student_num = key
                            else:
                                raise exceptions.AbsenceStudentNumber("Не удалось найти ученика с заданным номером")
                    else:
                        if not response['result']['relations']['students'].get(self.student_num):
                            raise exceptions.AbsenceStudentNumber("Не удалось найти ученика с заданным номером")

                    _student = response['result']['relations']['students'][self.student_num]

                    firstname = _student['firstname']
                    last_name = _student['lastname']
                    self.name = f"{last_name} {firstname}"
                    self.student_class = _student['class']
                    self.full_school_name = response['result']['relations']['schools'][0]['title']

                    self.city = _student['city']

                    return {'name': self.name, 'student_class': self.student_class,
                            'full_school_name': self.full_school_name, 'student_num': self.student_num,
                            'city': self.city}
                else:
                    raise exceptions.AbsenceStudentNumber("Не удалось найти номер ученика")
            else:
                raise exceptions.AbsenceStudentNumber("Не удалось найти номер ученика")
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_periods(self, return_dict=True) -> list:
        """
        Определяет текущий период(четверть, полугодие и т.д)

        :return: Возвращает список со всеми периодами
        """

        request = await self._make_request(Methods.get_periods, auth_token=self.auth_token, show_disabled="true")
        response = await self._order(request, RequestType.get)

        if response['state'] == 200:
            all_periods = []
            last = 0
            successful_find = False
            if response['result']['students']:
                for num, period in enumerate(response['result']['students'][0]['periods']):
                    if not period['ambigious']:
                        start_date = datetime.datetime.strptime(period['start'], "%Y%m%d").date()
                        end_date = datetime.datetime.strptime(period['end'], "%Y%m%d").date()
                        if return_dict:
                            period_obj = {"name": period['fullname'], "start": start_date, "end": end_date}
                        else:
                            period_obj = f"{period['fullname']}::{period['start']}-{period['end']}"

                        today = datetime.date.today()

                        if start_date <= today:
                            last = num
                            if today <= end_date:
                                self.current_period = num
                                successful_find = True

                        all_periods.append(period_obj)

                if not successful_find:
                    self.current_period = last

                self.all_periods = all_periods

                return all_periods
            else:
                raise exceptions.AbsenceStudentNumber()
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_diary(self, start_date: datetime.date = None, end_date: None = None) -> list:
        """
        Получение уроков и дз за определённый период

        Если не указать начало или конец периода, то возьмётся промежуток от -14 до + 14 дней от текущего дня

        :param start_date: отвечает за начальную дату периода
        :param end_date: конец нужного периода
        :return: возвращает список в котором первый элемент будет списком всех уроков, а второй элемент будет
        списком всех заданий
        """
        if not start_date:
            start_date = datetime.date.today() - datetime.timedelta(days=14)
            end_date = datetime.date.today() + datetime.timedelta(days=14)

        request = await self._make_request(Methods.get_diary, student=self.student_num, auth_token=self.auth_token,
                                           rings="false",
                                           days=f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}")

        response = await self._order(request, RequestType.get)

        if response['state'] == 200:
            all_lessons = []
            all_homeworks = []
            if response['result']['students']:
                for day in response['result']['students'][self.student_num]['days']:
                    if 'items' in response['result']['students'][self.student_num]['days'][day]:
                        for convert_to_diary in asyncio.as_completed(
                                [self._convert_to_diary(
                                    response['result']['students'][self.student_num]['days'][day]['items'][item],
                                    datetime.datetime.strptime(day, "%Y%m%d").date()) for item in
                                    response['result']['students'][self.student_num]['days'][day]['items']]):
                            lesson, homework = await convert_to_diary
                            all_lessons.append(lesson)
                            if homework:
                                all_homeworks.append(homework)

                return all_lessons, all_homeworks, self
            else:
                raise exceptions.AbsenceStudentNumber()
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_marks(self, days: str | None = None) -> list:
        """
        Получение всех оценок ученика

        :return: возвращает список со всеми оценками
        """

        if not days:
            days = f"{self.all_periods[0]['start'].strftime('%Y%m%d')}-{self.all_periods[-1]['end'].strftime('%Y%m%d')}"  # С самого первого учебного дня, до самого последнего

        request = await self._make_request(Methods.get_marks, auth_token=self.auth_token, student=self.student_num,
                                           days=days)
        response = await self._order(request, RequestType.get)

        if response['state'] == 200:
            if response['result']['students']:
                all_marks = []

                for convert_to_marks in asyncio.as_completed(
                        [self._convert_to_marks(lesson['name'], lesson['marks']) for lesson in
                         response['result']['students'][self.student_num]['lessons']]):
                    all_lesson_marks = await convert_to_marks
                    all_marks = [*all_marks, *all_lesson_marks]

                return all_marks, self
            else:
                raise exceptions.AbsenceStudentNumber()
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_final_marks(self) -> list:
        """
        Получение всех итоговых оценок ученика


        :return: список итоговых оценок
        """

        request = await self._make_request(Methods.get_final_marks, auth_token=self.auth_token,
                                           student=self.student_num)
        response = await self._order(request, RequestType.get)

        if response['state'] == 200:
            if response['result']['students']:
                items = response['result']['students'][self.student_num].get('items')
                all_marks = []
                if items:
                    for convert_to_marks in asyncio.as_completed(
                            [self._convert_to_marks(item['name'], item['assessments']) for item in items]):
                        all_lesson_marks = await convert_to_marks
                        all_marks = [*all_marks, *all_lesson_marks]

                return all_marks, self
            else:
                raise exceptions.AbsenceStudentNumber()
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_noticed(self) -> list:
        """
        Получение всех объявлений

        :return: Возвращает список со всеми объявлениями
        """

        request = await self._make_request(Methods.get_board_notices, auth_token=self.auth_token,
                                           student=self.student_num, folder='inbox', unreadonly="no", limit=10000)
        response = await self._order(request, RequestType.get)

        if response['state'] == 200:
            notices = []
            if 'notices' in response['result']:
                for convert_to_notice in asyncio.as_completed(
                        [self._convert_to_notice(notice) for notice in response['result']['notices']]):
                    notice_ = await convert_to_notice
                    notices.append(notice_)

            return notices, self

        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_messages(self) -> list:
        """
        Получение всех объявлений

        :return: Возвращает список со всеми объявлениями
        """
        request = await self._make_request(Methods.get_messages, auth_token=self.auth_token,
                                           student=self.student_num, folder='inbox', unreadonly="no", limit=10000)

        response = await self._order(request, RequestType.get)
        if response['state'] == 200:
            messages = []
            if 'messages' in response['result']:
                for convert_to_message in asyncio.as_completed(
                        [self._convert_to_message(message) for message in response['result']['messages']]):
                    message = await convert_to_message
                    messages.append(message)

            return messages, self
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_message_info(self, message: Message) -> Message:
        """
        Позволяет получить подробную информацию о конкретном сообщении


        :param message: Либо объект класса Message, либо идентификатор сообщения

        :return: Возвращает объект Message с заполненной информацией
        """
        request = await self._make_request(Methods.get_message_info, auth_token=self.auth_token,
                                           student=self.student_num,
                                           id=message.id if not isinstance(message, str) else message)

        response = await self._order(request, RequestType.get)

        if response['state'] == 200:
            message_ = await self._convert_to_message(response['result']['message'])
            return message_
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def get_notice_info(self, message) -> Message:
        """
        Позволяет получить подробную информацию о конкретном объявлении


        :param message: Либо объект класса Message, либо идентификатор объявления

        :return: Возвращает объект Message!!! С заполненной информацией
        """
        request = await self._make_request(Methods.get_board_notice_info, auth_token=self.auth_token,
                                           student=self.student_num,
                                           id=message.id if not isinstance(message, str) else message)
        response = await self._order(request, RequestType.get)

        if response['state'] == 200:
            notice = await self._convert_to_notice(response['result']['notice'])
            return notice
        else:
            raise exceptions.ServerAnswerError(response['error'])

    async def _convert_to_diary(self, item: dict, date: datetime.date) -> (Lesson, Homework):
        """
        Конвертирует Json данные в объекты Lesson и Homework

        :param item:
        :param date:
        :return: Возвращает полученный объекты
        """

        lesson = item['name']
        number = item['num']
        room = item['room']

        homework_obj = None

        if item['homework']:
            text = ""
            group = item.get('grp', None)
            all_individual = False

            for id_ in item['homework']:
                if item['homework'][id_]['value'].strip().lower().replace(".", "") == "без задания":
                    continue

                if bool(text):
                    text += "\n"

                is_individual = item['homework'][id_]['individual']

                if is_individual:
                    all_individual = True

                text += f"\t\t{'▸ Индивидуальное задание: ' if is_individual else '▸ '}"
                text += item['homework'][id_]['value'].strip()

            for num, file in enumerate([*item['files'], *item['resources']], 1):
                if bool(text):
                    text += "\n"

                text += f"\t\t<a href='{file['link']}'>◉ Файл №{num}</a>"

            if bool(text):
                homework_obj = Homework(lesson, text, date, all_individual, group, number, self)

        lesson_obj = Lesson(lesson, number, room, date, self)

        return lesson_obj, homework_obj

    async def _convert_to_message(self, data: dict) -> Message:
        """
        Конвертирует Json данные в объект Message

        :param data:
        :return: Возвращает полученный объект
        """
        id_ = data['id']
        subject = data['subject']
        date = datetime.date.fromisoformat(data['date'].split()[0])
        time = datetime.time.fromisoformat(data['date'].split()[1])
        text = data.get('text', '').replace("<p>", "\n\n").replace("</p>", "").replace('<p style="text-align:center;">',
                                                                                       "\n")
        text = BeautifulSoup(text, 'lxml').text
        short_text = data.get('short_text', "").replace("<p>", "\n\n").replace("</p>", "").replace(
            '<p style="text-align:center;">', "\n")
        short_text = BeautifulSoup(short_text, 'lxml').text

        if 'files' in data or "resources" in data:
            text += "\n\n<b>Прикреплённые файлы:</b>"

            for file in [*data.get('files', []), *data.get('resources', [])]:
                text += f"\n\t\t<a href='{file['link']}'>◉ {file['filename']}</a>"

        user_from = f"{data['user_from']['lastname']} {data['user_from']['firstname']} {data['user_from']['middlename']}"
        full_date = datetime.datetime(date.year, date.month, date.day, time.hour, time.minute, time.second)

        return Message(id_, subject, full_date, self, text, user_from, short_text)

    async def _convert_to_notice(self, data: dict) -> list:
        """
        Конвертирует Json данные в объект Message

        :param data:
        :return: Возвращает полученный объект
        """

        id_ = data['id']
        subject = data['subject']

        date = datetime.date.fromisoformat(data['date'])
        text = data.get('text', '').replace("<p>", "\n\n").replace("</p>", "").replace('<p style="text-align:center;">', "\n")
        text = BeautifulSoup(text, 'lxml').text
        short_text = data.get('short_text', "").replace("<p>", "\n\n").replace("</p>", "").replace('<p style="text-align:center;">', "\n")
        short_text= BeautifulSoup(short_text, 'lxml').text
        if 'files' in data or "resources" in data:
            text += "\n\n<b>Прикреплённые файлы:</b>"

            for file in [*data.get('files', []), *data.get('resources', [])]:
                text += f"\n\t\t<a href='{file['link']}'>◉ {file['filename']}</a>"
        text = text.strip()
        user_from = f"{data['user_from']['lastname']} {data['user_from']['firstname']} {data['user_from']['middlename']}"
        full_date = datetime.datetime(date.year, date.month, date.day)

        return Message(id_, subject, full_date, self, text, user_from, short_text)

    async def _convert_to_marks(self, lesson: str, marks: list) -> list:
        """
        Конвертирует Json данные в объекты Mark

        :param lesson:
        :param marks:
        :return: Возвращает лист с полученными оценками
        """

        marks_obj = []

        num = 0

        for mark in marks:
            value = mark['value'].replace("-", "").replace("+", "").replace(".", "")

            for num_, value in enumerate(list(value) if mark.get('count', False) else [value]):

                if "period" not in mark:
                    if not bool(value.strip()):
                        continue

                if "period" in mark:
                    mark_obj = Mark(value if value.strip() else "-", 1, lesson, True, datetime.date(2006, 2, 9), 0,
                                    None,
                                    None, mark['period'], self, None)
                else:
                    teacher_comment = mark['comment']
                    lesson_comment = mark['lesson_comment']
                    is_mark = mark['count']
                    date = datetime.date.fromisoformat(mark['date'])
                    mark_id = num_
                    weight = mark.get('weight', 1)

                    if len(marks_obj) > 0:
                        if marks_obj[num - 1].date == date:
                            mark_id = marks_obj[num - 1].mark_id + 1

                    if 'mtype' in mark:
                        mtype = mark['mtype']['type']
                    else:
                        mtype = None

                    mark_obj = Mark(value, weight, lesson, is_mark, date, mark_id, teacher_comment, lesson_comment,
                                    "default", self, mtype)

                marks_obj.append(mark_obj)
                num += 1

        return marks_obj

    @staticmethod
    async def _order(request: str, request_type: Enum, data: dict = None) -> dict:
        """
        Выполняет запрос к серверу дневника
        :param request: адрес
        :param request_type: Либо RequestType.get, либо RequestType.post
        :param data: дополнительная информация, которая нужна для запроса
        :return: Возвращает ответ с сервера в формате json
        """

        if dev_key == "Your dev_key here":
            raise Exception(
                'The dev_key value is not set. You need to install journal_api.api.dev_key = "your dev_key"')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0 (Edition Yx 05)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "edu.gounn.ru",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"}

        async with aiohttp.ClientSession(conn_timeout=10) as session:
            if request_type == RequestType.post:
                async with session.post(request, data=data, headers=headers) as resp:
                    response = await resp.json()
            elif request_type == RequestType.get:
                async with session.get(request, headers=headers) as resp:
                    response = await resp.json()
        return response['response']

    @staticmethod
    async def _make_request(method, **kwargs) -> str:
        """
        Создание запроса

        :param method:
        :param kwargs:
        :return:
        """
        request = f"{base}{method}?devkey={dev_key}&out_format={out_format}&vendor={vendor}"

        for key in kwargs:
            request = f"{request}&{key}={kwargs.get(key)}"

        return request
