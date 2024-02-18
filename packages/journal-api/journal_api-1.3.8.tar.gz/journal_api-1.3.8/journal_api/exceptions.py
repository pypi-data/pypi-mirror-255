class DataError(Exception):
    def __init__(self):
        super(DataError, self).__init__("Неправильный логин или пароль")


class ServerAnswerError(Exception):
    def __init__(self, message=None):
        super(ServerAnswerError, self).__init__(f"Неизвестная серверная ошибка: {message}")


class AbsenceStudentNumber(Exception):
    def __init__(self, message=None):
        super(AbsenceStudentNumber, self).__init__(message)
