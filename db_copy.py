from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Подключаемся к первой базе данных (где 21000 строк)
engine_first_db = create_engine("sqlite:///realtors.db")  # Замените на ваш URI
Base.metadata.create_all(bind=engine_first_db)
first_table = Table("realtors", autoload_with=engine_first_db)

# Подключаемся ко второй базе данных (куда будем вставлять 7000 строк)
engine_second_db = create_engine("sqlite:///realtors7000.db")  # Замените на ваш URI
Base.metadata.create_all(bind=engine_second_db)
second_table = Table("realtors7000", autoload_with=engine_second_db)

# Создаем сессии для обеих баз данных
SessionFirst = sessionmaker(bind=engine_first_db)
session_first = SessionFirst()

SessionSecond = sessionmaker(bind=engine_second_db)
session_second = SessionSecond()

# Получаем первые 7000 строк из первой таблицы
first_7000_rows = session_first.query(first_table).limit(7000).all()

# Вставляем полученные строки во вторую таблицу
for row in first_7000_rows:
    # Создаем словарь значений для вставки
    insert_data = {
        column.name: getattr(row, column.name) for column in first_table.columns
    }

    # Вставляем данные во вторую таблицу
    session_second.execute(second_table.insert().values(insert_data))

# Фиксируем изменения во второй базе данных
session_second.commit()

# Закрываем сессии
session_first.close()
session_second.close()

print("Первые 7000 строк успешно скопированы во вторую базу данных.")
