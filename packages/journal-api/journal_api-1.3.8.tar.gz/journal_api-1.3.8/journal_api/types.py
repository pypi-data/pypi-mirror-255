import datetime


class Mark:
    __slots__ = ("value", "weight", "lesson", "is_mark", "date", "mark_id",
                 "teacher_comment", "lesson_comment", "period", "student", "mtype")

    def __init__(self, value: str, weight: float, lesson: str, is_mark: bool, date: datetime.date, mark_id: int,
                 teacher_comment: str, lesson_comment: str, period: str, student, mtype: str):
        self.value = value  # Значение отметки
        self.weight = weight  # Коэффициент отметки
        self.lesson = lesson  # Предмет
        self.is_mark = is_mark  # Является ли отметка цифрой
        self.date = date  # Дата за которую поставлена отметка
        self.mark_id = mark_id  # Идентификатор для отметок, выставленных за один и тот же день по такому же предмету
        self.teacher_comment = teacher_comment  # Уникальный комментарий от учителя лично ученику
        self.lesson_comment = lesson_comment  # Общий комментарий от учителя всему классу
        self.period = period  # Период (обычная, четвертная, промежуточная, годовая, егэ/огэ и т.д.)
        self.student = student  # Ученик, которому принадлежит отметка
        self.mtype = mtype  # Тип работы за которую стоит оценка (Проверочная, Контрольная и т. д.)

    def __str__(self):
        weight = int(self.weight) if int(self.weight) == float(self.weight) else self.weight
        return f"{self.value if self.is_mark else self.value.upper()}{'×' if weight > 1 and self.is_mark else ''}{weight if weight > 1 and self.is_mark else ''}"


class Message:
    __slots__ = ("id", "subject", "date", "text", "user_from", "student", "short_text")

    def __init__(self, id_: str, subject: str, date, student, text, user_from, short_text):
        self.id = id_  # Идентификатор сообщения
        self.subject = subject  # Заголовок
        self.date = date  # Дата и время сообщения
        self.student = student  # Ученик, которому принадлежит сообщение
        self.text = text  # текст сообщения
        self.short_text = short_text
        self.user_from = user_from  # ФИО отправителя

    def __str__(self):
        return self.text


class Homework:
    __slots__ = ("lesson", "text", "date", "is_individual", "group", "lesson_number",
                 "student")

    def __init__(self, lesson: str, text: str, date: datetime.date, is_individual: bool, group: str, lesson_number: int,
                 student):
        self.lesson = lesson  # Предмет
        self.date = date  # Дата урока
        self.text = text  # Текст дз
        self.lesson_number = lesson_number  # порядковый номер урока
        self.is_individual = is_individual  # Является ли дз индивидуальным
        self.group = group  # Группа к которой относится ученик
        self.student = student  # Ученик, которому принадлежит отметка

    def __str__(self):
        return self.text


class Lesson:
    __slots__ = ("lesson", "number", "room", "date", "student")

    def __init__(self, lesson: str, number: int, room: str, date: datetime.date, student):
        self.lesson = lesson  # Предмет
        self.date = date  # Дата урока
        self.number = number  # Порядковый номер урока
        self.room = room  # Номер кабинета
        self.student = student  # Ученик, которому принадлежит отметка
