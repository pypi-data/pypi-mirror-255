#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  29 12:44:20 2023.

@author: gp
"""
import threading
import json
import requests
import numpy as np
import openpyxl
import pandas as pd
import websocket
import time


class WebSocketClient:
    """Класс для создания соединения типа вебсокет."""

    def __init__(
            self,
            url: str,
            logs: list,
            host,
            session
    ):
        # Настраиваем логи
        self.logs = logs
        self.host = host
        self.session = session
        cookies = self.session.cookies
        # Создаем объект вебсокета, но пока не открываем канал
        self.websock = websocket.WebSocketApp(
            url,
            header=self.session.headers,
            cookie="; ".join(["%s=%s" % (i, j) for i, j in cookies.items()]),
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close)
        # Указываем, что должно отправиться при открытии вебсокета
        self.websock.on_open = self.on_open
        # Создаем объект канала для вебсокета в качестве параллельного потока
        self.websocket_thread = threading.Thread(target=self.run_websocket)
        # Открывам канал вебсокета в параллельном потоке
        self.websocket_thread.start()

        time.sleep(3)
        # Инициализация и запуск дополнительного потока для выполнения цикла
        self.additional_thread = threading.Thread(
            target=self.run_additional_task
            )
        self.additional_thread.start()

    def run_additional_task(self):
        """
        Метод запускает отправку таймаутов (похоже, оказалось нужно).

        Returns
        -------
        None.

        """
        while 'Connection closed' not in self.logs:
            try:
                _ = self.session.post(
                    f'https://{self.host}/oo/r/webapi/entry.cgi/'
                    'SYNO.Core.Desktop.Timeout',
                    data=dict(
                        api='SYNO.Core.Desktop.Timeout',
                        method='check',
                        version=1
                        )
                )
                self.logs.append('timeout sent')
            except Exception:
                self.logs.append('Exception in additional task')
            time.sleep(60)

    def on_message(self, _, message: str) -> None:
        """
        Метод обрабатывает входящие сообщения по вебсокету.

        Parameters
        ----------
        message : str
            Входящее сообщение по вебсокету.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        self.logs.append(f'Received message: {message}')
        # Обработка входящих сообщений от сервера, чтобы канал работал
        if message == '2':
            # Сервер постоянно опрашивает канал и, чтобы канал не закрывался
            # нужно на 2 отвечать 3
            self.websock.send('3')
            self.logs.append('3')
        elif message == '3probe':
            # Ответ на приветственное сообщение
            self.websock.send('5')
            self.logs.append('5')
            self.websock.send('420["say_hello"]')
            self.logs.append('say_hello')
            self.websock.send('421["ask_peers"]')
            self.logs.append('ask_peers')
            self.websock.send('422["init"]')
            self.logs.append('init')

    def on_error(self, _, error: str) -> None:
        """
        Метод обрабатывает ошибки.

        Parameters
        ----------
        error : str
            Текст ошибки.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        self.logs.append(f'Error occurred: {error}')

    def on_close(self, _) -> None:
        """
        Метод обрабатывает событие закрытия вебсокета.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        self.logs.append('Connection closed')

    def on_open(self, _) -> None:
        """
        Метод выполняет первые действия при октрытии вебсокета.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        # Отправляем приветственное сообщение
        self.websock.send('2probe')
        self.logs.append('2probe')

    def run_websocket(self) -> None:
        """
        Метод запускает вебсокет.

        Returns
        -------
        None.

        """
        self.websock.run_forever()

    def send_message(self, message: str) -> None:
        """
        Метод отправляет сообщение по вебсокету.

        Parameters
        ----------
        message : str
            Сообщение для отправки.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        if self.websock is not None and self.websock.sock and \
                self.websock.sock.connected:
            self.logs.append(message)
            self.websock.send(message)
        else:
            self.logs.append('Connection is not open. Message not sent.')


class DriveConnectorShared:
    """Класс для работы с драйвом."""

    def __init__(
            self
    ):
        # Создаем сессию (чтобы обновлялись куки)
        self.session = requests.Session()
        # Указываем, что логи будут лежать в переменной list для удобства
        self.logs = []
        # Заглушка для хоста
        self.host = ''
        # Заглушка для идентификатора документа
        self.doc_id = ''
        # Заглушка информации о документе
        self.snapshot = {}
        # Заглушка для клиента-вебсокета
        self.client = None

    def update_dataframes(self) -> pd.DataFrame:
        """
        Метод вносит в датафрейм данные из логов.

        Returns
        -------
        dict_tables : pd.DataFrame
            Датафрейм отредактированный.

        """
        # Заполняем мэппинг названий таблиц
        dict_sheets = self.list_tables()
        # Заполняем словарь с таблицами
        dict_tables = {
            v: self.read_table(t) for t, v in dict_sheets.items()
            }
        # Проходим по всем логам
        for log in self.logs:
            # Пытаемся преобразовать строку лога в объект json
            try:
                log_json = json.loads(log[log.index('['):])
                if 'set' in log_json:
                    log_json = log_json[1]
                else:
                    continue
            except ValueError:
                continue
            # Проверяем, есть ли в логе нужные ключи
            if 'cmd' in log_json and log_json['cmd'] == 'value'\
                    and 'id' in log_json and 'changes' in log_json:
                # Получаем id датафрейма и изменения
                df_id = log_json['id']
                changes = log_json['changes']

                # Проверяем, существует ли такой датафрейм
                if df_id in dict_tables:
                    # Применяем все изменения к датафрейму
                    for change in changes:
                        try:
                            dict_tables[df_id].iat[change[0], change[1]] =\
                                change[2]
                        except IndexError:
                            # Расширяем датафрейм, если изменение выходит за
                            # его границы
                            max_index = max(
                                change[0], dict_tables[df_id].index.max()
                                )
                            max_columns = max(
                                change[1], dict_tables[df_id].columns.max()
                                )
                            dict_tables[df_id] = dict_tables[df_id].reindex(
                                index=range(max_index + 1),
                                columns=range(max_columns + 1)
                                )
                            dict_tables[df_id].iat[change[0], change[1]] =\
                                change[2]
        return dict_tables

    def login_shared(self, url: str) -> None:
        """
        Логинимся через расшаренную ссылку.

        Parameters
        ----------
        url : str
            Расшаренная ссылка.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        # Заполняем хост
        self.host = url.split('//', 1)[1].split('/', 1)[0]
        # Заполняем идентификатор документа
        self.doc_id = url.rsplit('/', 2)[1]
        # Извлекаем расшаренную ссылку
        sharing_link = url.rsplit('/', 2)[2]
        # Этот запрос нужен для получения куков, из которых получаем токен
        # drive-sharing
        self.session.get(url)
        # Извлекаем токен
        token = self.session.cookies.get_dict()[
            f'drive-sharing-{sharing_link}'
            ]
        time.sleep(0.5)
        # Получаем идентификатор таблицы
        self.objectId = self.session.post(
            f'https://{self.host}/oo/r/webapi/entry.cgi/'
            'SYNO.Office.Shard.Type',
            data={
                 'api': 'SYNO.Office.Shard.Type',
                 'method': 'get',
                 'version': '1',
                 'link_id': self.doc_id,
                 'sharing_token': token
            }
            ).json()['data']['objectId']
        time.sleep(0.5)
        # Этот запрос нужен, чтобы получить sid
        r_sid = self.session.get(
            f'https://{self.host}/oo/r/oo/socket.io/sheet/',
            params={
                'objectId': self.objectId,
                'sharing_link': sharing_link,
                'sharing_token': token,
                'EIO': '4',
                'transport': 'polling'
            }
        )
        time.sleep(0.5)
        # Извлекаем идентификатор сессии
        sid = r_sid.content.decode('utf-8').split('":"')[1].split('"')[0]
        # Без этого запроса не запустится вебсокет
        self.session.post(
            f'https://{self.host}/oo/r/oo/socket.io/sheet/',
            params={
                'objectId': self.objectId,
                'sharing_link': sharing_link,
                'sharing_token': token,
                'EIO': '4',
                'transport': 'polling',
                'sid': sid
            },
            data='40'
        )
        time.sleep(0.5)
        # Заполняем информацию о документе
        self.snapshot = self.get_snapshot(token)
        # Эта ссылка нужна для создания вебсокета, она одноразовая
        url_ws = (f'wss://{self.host}/oo/r/oo/socket.io/sheet/'
                  f'?objectId={self.objectId}'
                  f'&sharing_link={sharing_link}'
                  f'&sharing_token={token}'
                  f'&EIO=4&transport=websocket&sid={sid}')
        # Открываем канал вебсокета
        # Открываем канал вебсокета
        self.client = WebSocketClient(
            url=url_ws,
            logs=self.logs,
            session=self.session,
            host=self.host
            )

    def login_mfa(self, url: str, login: str, password: str) -> None:
        """
        Логинимся через логин и пароль с учетом двухфакторной аутентификации.

        Parameters
        ----------
        url : str
            Ссылка на таблицу.
        login : str
            Логин (почта).
        password : str
            Пароль.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        # Заполняем хост
        self.host = url.split('//', 1)[1].split('/', 1)[0]
        # Заполняем идентификатор документа
        self.doc_id = url.rsplit('/', 1)[1]
        self.version = int(time.time() * 1000)
        # Мусорные запросы для замедления авторизации
        # 1
        _ = self.session.get(
            f'https://{self.host}/oo/r/{self.doc_id}/synoscgi.sock/socket.io/',
            params=dict(
                Version=self.version,
                SynoToken='undefined',
                UserType='guest',
                EIO=3,
                transport='polling'
            )
        )
        time.sleep(0.5)
        # 2
        _ = self.session.get(
            f'https://{self.host}/oo/r/{self.doc_id}/synoscgi.sock/socket.io/',
            params=dict(
                Version=self.version,
                SynoToken='undefined',
                UserType='guest',
                EIO=3,
                transport='polling'
            )
        )
        time.sleep(0.5)
        # 3
        _ = self.session.get(
            f'https://{self.host}/oo/r/{self.doc_id}/synoscgi.sock/socket.io/',
            params=dict(
                Version=self.version,
                SynoToken='undefined',
                UserType='guest',
                EIO=3,
                transport='polling',
                sid=self.session.cookies.get_dict()['io']
            )
        )
        time.sleep(0.5)
        # 4
        _ = self.session.post(
            f'https://{self.host}/oo/r/{self.doc_id}/synoscgi.sock/socket.io/',
            params=dict(
                Version=self.version,
                SynoToken='undefined',
                UserType='guest',
                EIO=3,
                transport='polling',
                sid=self.session.cookies.get_dict()['io']
            ),
            data='11:42["ready"]'
        )
        time.sleep(0.5)
        # 5
        _ = self.session.post(
            f'https://{self.host}/webapi/entry.cgi/SYNO.API.Auth.UIConfig',
            data=dict(
                api='SYNO.API.Auth.UIConfig',
                method='get',
                version='1'
            )
        )
        time.sleep(0.5)
        # Инициируем сессию для получения куков
        # 6
        r_token = self.session.post(
            f'https://{self.host}/webapi/entry.cgi',
            params=dict(api='SYNO.API.Auth'),
            data=dict(
                launchApp='SYNO.SDS.Office.Sheet.Application',
                launchParam=f'link={self.doc_id}',
                api='SYNO.API.Auth',
                version='7',
                method='login',
                session='webui',
                enable_syno_token='yes',
                account=login,
                passwd=password,
                logintype='local',
                otp_code=None,
                enable_device_token='no',
                timezone='+03:00',
                rememberme=0,
                client='browser'
            )
        )
        time.sleep(0.5)
        # Извлекаем токен
        synotoken = r_token.json()['data']['synotoken']
        # Добавляем токен в заголовки
        self.session.headers.update({'X-Syno-Token': synotoken})
        # Получаем идентификатор таблицы
        self.objectId = self.session.post(
            f'https://{self.host}/oo/r/webapi/entry.cgi/'
            'SYNO.Office.Shard.Type',
            data={
                 'api': 'SYNO.Office.Shard.Type',
                 'method': 'get',
                 'version': '1',
                 'link_id': self.doc_id
            }
            ).json()['data']['object_id']
        time.sleep(0.5)
        # Еще мусорные запросы для замедления
        # 7
        _ = self.session.post(
            f'https://{self.host}/webapi/entry.cgi/'
            'SYNO.Core.Desktop.PersonalUpdater',
            data=dict(
                api='SYNO.Core.Desktop.PersonalUpdater',
                method='need_update',
                version='1'
            )
        )
        time.sleep(0.5)
        # 8
        _ = self.session.get(
            f'https://{self.host}/synoscgi.sock/socket.io/',
            params=dict(
                Version=self.version,
                SynoToken=synotoken,
                UserType='user',
                EIO='3',
                transport='polling',
            )
        )
        time.sleep(0.5)
        # 9
        _ = self.session.get(
            f'https://{self.host}//synoscgi.sock/socket.io/',
            params=dict(
                Version=self.version,
                SynoToken=synotoken,
                UserType='user',
                EIO='3',
                transport='polling',
                sid=self.session.cookies.get_dict()['io']
            )
        )
        time.sleep(0.5)
        # Инициируем сессию для получения куков
        # 10
        r_sid = self.session.get(
            f'https://{self.host}/oo/r/oo/socket.io/sheet/',
            params=dict(
                objectId=self.objectId,
                EIO='4',
                transport='polling',
            )
        )
        time.sleep(0.5)
        # Извлекаем идентификатор сессии
        sid = r_sid.content.decode('utf-8').split('":"')[1].split('"')[0]
        # Инициируем сессию для получения куков
        # 11
        _ = self.session.post(
            f'https://{self.host}/oo/r/oo/socket.io/sheet/',
            params=dict(
                objectId=self.objectId,
                EIO='4',
                transport='polling',
                sid=sid
            ),
            data='40'
        )
        time.sleep(0.5)
        # Еще один мусорный запрос для замедления
        # 12
        _ = self.session.get(
            f'https://{self.host}/oo/r/oo/socket.io/sheet/',
            params=dict(
                objectId=self.objectId,
                EIO='4',
                transport='polling',
                sid=sid
            )
        )
        time.sleep(0.5)
        # Заполняем информацию о документе
        self.snapshot = self.get_snapshot('')
        # Эта ссылка нужна для создания вебсокета, она одноразовая
        url_ws = (f'wss://{self.host}/oo/r/oo/socket.io/sheet/'
                  f'?objectId={self.objectId}'
                  '&EIO=4'
                  '&transport=websocket'
                  f'&sid={sid}')
        # Открываем канал вебсокета
        self.client = WebSocketClient(
            url=url_ws,
            logs=self.logs,
            session=self.session,
            host=self.host
            )

    def get_snapshot(self, token: str) -> dict:
        """
        Метод получает всю информацию о документе.

        Parameters
        ----------
        token : str
            Токен для подключения.

        Returns
        -------
        dict
            Словарь с данными документа.

        """
        # Получаем содержимое документа
        r_table = self.session.post(
            (f'https://{self.host}/d/s/{self.doc_id}/webapi/entry.cgi'
             '/SYNO.Office.Sheet.Snapshot'),
            data={
                'api': 'SYNO.Office.Sheet.Snapshot',
                'method': 'get',
                'version': '1',
                'password': "",
                'object_id': self.objectId,
                'sharing_token': token
            }
        )
        return r_table.json()

    def list_tables(self) -> dict:
        """
        Метод получает мэппинг названий таблиц.

        Returns
        -------
        dict
            Словарь с мэппингом.

        """
        # Генерим словарь с мэппингом
        dict_sheets = {
            v['title']: k
            for k, v in self.snapshot['data']['index']['sheets'].items()
            }
        return dict_sheets

    def read_table(self, table: str) -> pd.DataFrame:
        """
        Метод чтения таблицы.

        Считываем страницу с таблицей.
        Важно: изменения, внесенные между использованиями этого метода
        при каждом последующем использовании после авторизации, не отображаются

        Parameters
        ----------
        table : str
            Нозвание таблицы.

        Returns
        -------
        df_table : pd.DataFrame
            Таблица.

        """
        # Генерим словарь с мэппингом
        dict_sheets = self.list_tables()
        # Проверяем корректность названия указанной таблицы
        assert table in dict_sheets, 'Такой таблицы нет'
        # Извлечение данных из ответа на запрос в формате JSON
        data = self.snapshot['data'][dict_sheets[table]]['cells']
        # Преобразование данных в словарь, где ключами являются индексы строк
        # и столбцов, а значениями - значения ячеек
        data_for_df = {
            int(row_idx): {
                int(col_idx): cell.get('v', np.nan)
                for col_idx, cell in row.items()
                }
            for row_idx, row in data.items()}
        # Создание датафрейма из словаря
        df_table = pd.DataFrame(data_for_df).T
        # Получение максимальных индексов строк и столбцов
        max_row_index = df_table.index.max()
        max_col_index = df_table.columns.max()
        try:
            # Создание массивов новых индексов строк и столбцов
            new_row_indices = np.arange(max_row_index + 1)
            new_col_indices = np.arange(max_col_index + 1)
        except ValueError:
            # Если возникла ошибка (например, индексы отсутствуют), создаем
            # пустые массивы
            new_row_indices = np.arange(0)
            new_col_indices = np.arange(0)
        # Переиндексация датафрейма с новыми индексами строк
        df_table = df_table.sort_index().reindex(index=new_row_indices)
        # Переиндексация датафрейма с новыми индексами столбцов
        df_table = df_table.T.reindex(new_col_indices).T
        # Сортировка столбцов датафрейма по возрастанию
        df_table = df_table.sort_index(axis=1, ascending=True)
        return df_table

    def send_cmd(self, cmd: str) -> None:
        """
        Метод для отправки сообщения по каналу вебсокета.

        Parameters
        ----------
        cmd : str
            Сообщение для отправки, например изменение в таблице.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        self.client.send_message(cmd)

    def get_table(self, str_table: str) -> pd.DataFrame:
        """
        Метод получения таблицы.

        Метод возвращает запрошенную таблиц с внесенными изменениями
        согласно сообщениям по вебсокету.

        Parameters
        ----------
        str_table : str
            Название запрошенной таблицы.

        Returns
        -------
        new_df : pd.DataFrame
            Измененная таблица.

        """
        # Обновление данных во временной копии словаря таблиц
        new_dict_tables = self.update_dataframes()
        # Копирование таблицы из обновленного словаря по ключу str_table
        new_df = new_dict_tables[self.list_tables()[str_table]].copy()
        # Переименование индексов строк, увеличивая каждый индекс на 1
        new_df.index = [i + 1 for i in new_df.index]
        # Переименование столбцов: каждому индексу столбца присваивается
        # соответствующая буква алфавита. Например, 0 -> 'A', 1 -> 'B', и
        # так далее. Используется функция get_column_letter из библиотеки
        # openpyxl для преобразования числа в букву.
        new_df.columns = [
            openpyxl.utils.get_column_letter(1 + i) for i in new_df.columns
            ]
        return new_df

    def write_to_table(self, df_to_load: pd.DataFrame, page_name: str) -> None:
        """
        Метод будет генерировать команды и записывать датафрейм по ним.

        Parameters
        ----------
        df_to_load : pd.DataFrame
            Датафрейм для записи.
        page_name : str
            Лист для записи.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        # Список команд
        commands = []
        # Генерируем словарь, где ключами являются названия таблиц, а
        # значениями - их идентификаторы
        dict_sheets = self.list_tables()
        # Получаем идентификатор указанной таблицы
        table_name = dict_sheets[page_name]
        # Проходим по всем элементам датафрейма
        for i in range(df_to_load.shape[0]):
            for j in range(df_to_load.shape[1]):
                # Для каждого элемента создаем команду
                commands.append([i, j, df_to_load.iloc[i, j]])
        command = {
            "cmd": "value",
            "id": table_name,
            "changes": commands,
            }
        # Добавляем команду в список
        cmd = f'424["set",{command}]'
        cmd = cmd.replace('\'', '"')
        cmd = cmd.replace('nan', 'null')
        cmd = cmd.replace('None', 'null')
        # Выполняем команду
        self.send_cmd(cmd)

    def clear_table(self, page_name: str) -> None:
        """
        Метод будет очищать таблицу на драйве.

        Parameters
        ----------
        page_name : str
            Название таблицы.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        # Список команд
        commands = []
        # Генерируем словарь, где ключами являются названия таблиц, а
        # значениями - их идентификаторы
        dict_sheets = self.list_tables()
        # Проверяем, что указанная таблица присутствует в словаре
        assert page_name in dict_sheets, 'Такой таблицы нет'
        # Получаем идентификатор указанной таблицы
        table_name = dict_sheets[page_name]
        # Получаем актуальную таблицу
        df_actual = self.get_table(page_name)
        # Проходим по всем элементам датафрейма
        for i in range(df_actual.shape[0]):
            for j in range(df_actual.shape[1]):
                # Создаем команду для изменения значения ячейки на None
                commands.append([i, j, None])
        command = {
            "cmd": "value",
            "id": table_name,
            "changes": commands,
        }
        # Преобразуем команду в строку и делаем необходимые замены для
        # корректного формата
        cmd = f'423["set",{command}]'
        cmd = cmd.replace('\'', '"')
        cmd = cmd.replace('nan', 'null')
        cmd = cmd.replace('None', 'null')
        # Выполняем команду
        self.send_cmd(cmd)

    def rename_table(self, page_name_old: str, page_name_new: str) -> None:
        """
        Метод для переименовывания таблицы.

        Parameters
        ----------
        page_name_old : str
            Старое название.
        page_name_new : str
            Новое название.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        # Генерируем словарь, где ключами являются названия таблиц, а
        # значениями - их идентификаторы
        dict_sheets = self.list_tables()
        # Получаем идентификатор указанной таблицы
        table_name = dict_sheets[page_name_old]
        command = {
            "cmd": "worksheet.rename",
            "id": table_name,
            "title": page_name_new,
        }
        cmd = f'424["set",{command}]'
        cmd = cmd.replace('\'', '"')
        # Выполняем команду
        self.send_cmd(cmd)

    def create_table(self, page_name_new: str = 'Таблица{0}') -> None:
        """
        Метод для создания таблицы.

        Parameters
        ----------
        page_name_new : str, optional
            Название таблицы. The default is 'Таблица{0}'.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        command = {
            "cmd": "worksheet.create",
            "titleTpl": page_name_new,
        }
        cmd = f'425["set",{command}]'
        cmd = cmd.replace('\'', '"')
        # Выполняем команду
        self.send_cmd(cmd)

    def del_table(self, page_name_del: str) -> None:
        """
        Метод для удаления таблицы.

        Parameters
        ----------
        page_name_del : str
            Название таблицы.

        Returns
        -------
        None
            Метод ничего не возвращает.

        """
        # Генерируем словарь, где ключами являются названия таблиц, а
        # значениями - их идентификаторы
        dict_sheets = self.list_tables()
        # Получаем идентификатор указанной таблицы
        table_name = dict_sheets[page_name_del]
        command = {
            "cmd": "worksheet.delete",
            "id": table_name,
            "includeSnapshotData": 'false',
        }
        cmd = f'426["set",{command}]'
        cmd = cmd.replace('\'', '"')
        # Выполняем команду
        self.send_cmd(cmd)
