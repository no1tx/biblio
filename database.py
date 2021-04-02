# Импортируем модули логирования и SQLAlchemy
import logging
from sqlalchemy import create_engine, Boolean, ForeignKey, Column, String, DateTime, Integer
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Инициализируем модуль логирования. Ставим уровень на DEBUG для отчитывания полного лога исполнения.
# Для упрощения вывода можно перевести пониже, скажем на INFO.
LOG_FORMAT = '%(asctime)s,%(msecs)d %(levelname)s: %(message)s'  # Формат лога.
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

# Путь к базе данных. Используем SQLite.
base_path = './database.db'

# Объявляем декларативную модель БД, с описание в дальнейшем структуры в виде классов-моделей.
Model = declarative_base()

# Каркас URL доступа к БД. Здесь и объявляем SQLite в качестве СУБД. При наличии модуля-коннектора и желании
# можем использовать любую СУБД, но опять же - зачем, когда и SQLite хватит?

DATABASE = {
    'drivername': 'sqlite',
    'database': base_path
}

# Объявляем движок БД и "скармливаем" ему URL базы данных, и отключаем проверку исполнения запросов в том же потоке.
dbengine = create_engine(URL(**DATABASE), connect_args={'check_same_thread': False})
# Объявляем класс сеанса работы с движком БД
Session = sessionmaker(bind=dbengine)
# Пишем в лог о создании сеанса.
LOGGER.log(logging.INFO, msg="Creating session with database %s" % base_path)
# Поднимаем наш сеанс работы с БД и выводим его в отдельный объект, с которым и будем работать внутри классов.
session = Session()


# Класс книги. Описываем его структуру и перетаскиваем атрибуты в конструктор класса, чтобы обращаться к ним.
class Book(Model):
    __tablename__ = 'books'  # внутреннее имя таблицы в СУБД.
    book_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    author = Column(String)
    count = Column(Integer)

    def __init__(self, book_id, name, author, count):
        self.id = book_id
        self.name = name
        self.author = author
        self.count = count  # Остаток количества данной книги.

    def __repr__(self):  # Представление класса.
        # Не обязательно его объявлять, но полезно, когда отлаживаете код - сразу видите какого типа объект.
        return "<Book(%s)>" % self.book_id

    def save(self):  # Метод для сохранения книги в БД.
        try:
            session.add(self)
            session.commit()
            LOGGER.log(logging.INFO, msg="Добавили книгу %s в БД." % self.name)
        except Exception as e:
            session.rollback()
            LOGGER.log(logging.INFO, msg="Не получилось добавить книгу в БД по причине: %s" % e)

    @staticmethod
    def get(book_id):  # Метод получения книги из БД по её идентификатору.
        try:
            book = session.query(Book).filter_by(book_id=book_id)
            return book
        except Exception as e:
            LOGGER.log(logging.INFO, msg="Failed to query all bots because %s" % e)


# Класс посетителя библиотеки.
class Client(Model):
    __tablename__ = 'clients'
    client_id = Column(Integer, primary_key=True, unique=True)  # Номер библиотечной карточки.
    name = Column(String)  # ФИО посетителя.

    def __init__(self, client_id, name):
        self.client_id = client_id
        self.name = name

    def __repr__(self):
        return "<Client(%s)>" % self.client_id

    def save(self):  # Метод для сохранения книги в БД.
        try:
            session.add(self)
            session.commit()
            LOGGER.log(logging.INFO, msg="Добавили посетителя %s в БД." % self.name)
        except Exception as e:
            session.rollback()
            LOGGER.log(logging.INFO, msg="Не получилось добавить посетителя в БД по причине: %s" % e)

    @staticmethod
    def get(client_id):
        client = session.query(Client).filter_by(client_id).one_or_none()
        return client

    @staticmethod
    def get_all():
        clients = session.query(Client).all()
        return clients


# Класс аренды книги посетителем.
class Rent(Model):
    __tablename__ = 'rents'
    client_id = Column(Integer, ForeignKey('clients.client_id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('books.book_id'))

    def __init__(self, client_id, book_id):
        self.client_id = client_id
        self.book_id = book_id
        self.returned = Column(Boolean)

    def __repr__(self):
        return "<Rent(%s, %s)>" % (self.client_id, self.book_id)

    def save(self):
        try:
            session.add(self)
            session.commit()
            LOGGER.log(logging.INFO, msg='Сохранили аренду книги %s -> %s' % (self.client_id, self.book_id))
        except Exception as e:
            session.rollback()
            LOGGER.log(logging.INFO, msg="Failed to save new message because %s" % e)

    @staticmethod
    def get_by_client(client_id):
        rent = session.query(Rent).filter_by(user_id=client_id).all()
        return rent


# Инициализируем структуру таблиц БД и метаданные.
Model.metadata.create_all(dbengine)
