import gc
import os
import sys
import time
import traceback
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, QueuePool
from sqlalchemy import exc
load_dotenv()


class DB_KM:
    _km = None

    def __new__(cls, *args, **kwargs):
        if not cls._km:
            #print(f"Инициализация класса {cls.__name__}")
            cls._km = super().__new__(cls)
        return cls._km

    def __init__(self):
        self.engine_km = None
        self.engine = None
        if not hasattr(self, 'initialized'):
            self.pool_Analitik()
            self.initialized = True


    def pool_Analitik(self):
        password = os.getenv('DB_PASSWORD')
        user = os.getenv('DB_USER')
        port = os.getenv('DB_PORT')
        host = os.getenv('DB_HOST')
        database = 'telegram_bots' #os.getenv('DB_NAME') #'telegram_bots'
        try:
            conn_str = f'postgresql://{user}:{password}@{host}:{port}/{database}'
            self.engine_km = create_engine(conn_str, pool_size=100, max_overflow=100, pool_timeout=300, poolclass=QueuePool)

        except Exception as error:
                 print(traceback.format_exc(),error)

    def ANALITIC_ENGINE(self):

        if self.engine_km is None:
            try:
                self.pool_Analitik()
            except Exception as error:
                print('Ошибка при создании подключения Analitik', traceback.format_exc(), error)

                time.sleep(60)
                try:
                    self.engine_km.dispose()
                    self.pool_Analitik()
                except Exception as error:
                    print('Ошибка при восстановлении подключения Analitik', traceback.format_exc(), error)
        return self.engine_km

    def ANALITIC_TO_DATAFRAME(self,query, params=None):#analitik_to_dataframe

        while True:
            try:
                self.engine_km = self.ANALITIC_ENGINE()
                with self.engine_km.connect() as conn:
                    if params:
                        df = pd.read_sql_query(query, conn, params=params)
                    else:
                        df = pd.read_sql_query(query, conn)
                return df
            except Exception as error:
                print('Подключение не установлено. Жду... ', traceback.format_exc(), error)



    def ANALITIC_TO_SCALAR(self,query):
        while True:
            try:
                self.engine_km = self.ANALITIC_ENGINE()
                with self.engine_km.connect() as conn:
                    max_km = conn.execute(query)
                    date_max_km = max_km.scalar()
                return date_max_km
            except Exception as error:
                print('Подключение не установлено ANALITIC_TO_SCALAR. Жду... ', traceback.format_exc(), error)

                time.sleep(60)


            #  Загрузка новых данных, загружает данные в таблицы по строчно
    def analitik_up_update_in_FOR(self,columns_to_update, conflict, df, tabele_name):
        for col in df.columns:
            if df[col].dtype.kind in 'ifc':
                df[col] = df[col].replace(0, np.nan)
        df.replace({'None': None, 'nan': None, '<NA>': None, "NaT": None, 'NaN': None, np.nan: None,'': None},
                   inplace=True)
        while True:
            try:
                self.engine_km = self.ANALITIC_ENGINE()
                with self.engine_km.connect() as conn:
                        for record in df.to_dict(orient='records'):

                            insert_query = text(f'''
                                                        INSERT INTO {tabele_name} ({', '.join(columns_to_update)}) 
                                                        VALUES ({', '.join([':' + col for col in columns_to_update])})
                                                         ON CONFLICT ({', '.join(conflict)}) DO UPDATE 
                                                        SET {', '.join([f"{col} = :{col}" for col in columns_to_update])};''')


                            conn.execute(insert_query, record)
                            conn.commit()
                        return
            except exc.IntegrityError as e:
                print(f"шибка клчей {e}")
                # обработчик ошибок ключей
                #errorExeptionIntegrityError(e)
            except Exception as error:
                print('Подключение не установлено analitik_up_update_in_FOR. Жду... ', traceback.format_exc(), error)

                time.sleep(60)
            finally:
                del columns_to_update, conflict, df, tabele_name
                gc.collect()


    #  Загрузка новых данных, загружает данные в таблицы
    def analitik_up_update(self,columns_to_update, conflict, df, tabele_name):
        conflict = list(conflict)
        while True:
            try:
                for col in df.columns:
                    if df[col].dtype.kind in 'ifc':
                        print(f"обновление {col} {df[col].dtype.kind}")
                        df.loc[:, col] = df[col].replace(0, np.nan)

                self.engine_km = self.ANALITIC_ENGINE()
                df = df.replace({'None': None, 'nan': None, '<NA>': None, "NaT": None, 'NaN': None, np.nan: None,'': None} )
                with self.engine_km.connect() as conn:
                        records = df.to_dict(orient='records')
                        insert_query = text(f'''
                                            INSERT INTO {tabele_name} ({', '.join(columns_to_update)}) 
                                            VALUES ({', '.join([':' + col for col in columns_to_update])})
                                             ON CONFLICT ({', '.join(conflict)}) DO UPDATE 
                                            SET {', '.join([f"{col} = :{col}" for col in columns_to_update])};''')
                        conn.execute(insert_query, records)
                        conn.commit()
                        break
            except Exception as error:
                print(f"шибка клчей {error}")
                print('Подключение не установлено analitik_up_update. Жду... ', traceback.format_exc(), error)

    #  только обновление
    def analitik_up_only_update(self,columns_to_update, conflict, df, tabele_name):
        try:
            for col in df.columns:
                if df[col].dtype.kind in 'ifc':
                    df.loc[:, col] = df[col].replace(0, np.nan)
            conflict = tuple(conflict)
            while True:
                self.engine_km = self.ANALITIC_ENGINE()
                df = df.replace({'None': None, 'nan': None, '<NA>': None, "NaT": None, 'NaN': None, np.nan: None,'': None})
                with self.engine_km.begin() as conn:
                    columns_to_update = ', '.join([f"{col} = :{col}" for col in columns_to_update])
                    conflict = ' AND '.join([f"{col} = :{col}" for col in conflict])
                    sql_query = text(f'UPDATE {tabele_name} SET {columns_to_update} WHERE {conflict}')
                    conn.execute(sql_query, df.to_dict('records'))
                    conn.commit()
                    break
        except Exception as error:
            print('Подключение не установлено analitik_up_only_update. Жду... ', traceback.format_exc(), error)
            time.sleep(60)
        finally:
            del columns_to_update, conflict, df, tabele_name
            gc.collect()

    def ANALITIC_QUERY(self,query, params=None):
        try:
            self.engine_km = self.ANALITIC_ENGINE()
            with self.engine_km.connect() as conn:
                query_ = text(query)
                if params:
                    conn.execute(query_, params)
                else:
                    conn.execute(query_)
                conn.commit()
        except Exception as error:
            print('Подключение не установлено ANALITIC_QUERY. Жду... ', traceback.format_exc(), error)

    def ANALITIC_RECORD_TRANZACTION_CONNECT(self):
        while True:
            try:
                self.engine_km = self.ANALITIC_ENGINE()
                conn = self.engine_km.connect()
                return conn
            except Exception as error:
                print('Подключение не установлено ANALITIC_RECORD_TRANZACTION_CONNECT. Жду... ', traceback.format_exc(), error)
                time.sleep(60)


    def ANALITIC_RECORD_TRANZACTION_query(self, query, conn,  params = None,):
        try:
            quer_ = text(query)
            if params:
                conn.execute(quer_, params)
            else:
                conn.execute(quer_)
        except Exception as error:
            print('Подключение не установлено ANALITIC_RECORD_TRANZACTION_query. Жду... ', traceback.format_exc(),
                  error)
            time.sleep(60)
        finally:
            del query, params
            gc.collect()

    def TRANZACTION_UPDATE(self, columns_to_update, conflict, df, tabele_name, conn=None):
        for col in df.columns:
            if df[col].dtype.kind in 'ifc':
                df.loc[:, col] = df[col].replace(0, np.nan)
        while True:
            try:
                if conn is None:
                    conn = self.ANALITIC_RECORD_TRANZACTION_CONNECT()
                df = df.replace(
                    {'None': None, 'nan': None, '<NA>': None, "NaT": None, 'NaN': None, np.nan: None, '': None,
                     0: None})

                columns_to_update = ', '.join([f"{col} = :{col}" for col in columns_to_update])
                conflict = ' AND '.join([f"{col} = :{col}" for col in conflict])
                sql_query = text(f'UPDATE {tabele_name} SET {columns_to_update} WHERE {conflict}')

                conn.execute(sql_query, df.to_dict('records'))
                break

            except exc.IntegrityError as e:
                print(f"шибка клчей {e}")
                # обработчик ошибок ключей
                # errorExeptionIntegrityError(e)
            except Exception as error:
                print('Подключение не установлено ANALITIC_ONLY_UPDATE. Жду... ', traceback.format_exc())

                time.sleep(60)

    def TRANZACTION_INSERT(self, columns_to_update: list, conflict: list, df:pd.DataFrame, table_name: str, conn = None, ):
        try:
            for col in df.columns:
                if df[col].dtype.kind in 'ifc':
                    df.loc[:, col] = df[col].replace(0, np.nan)
            if conn is None:
                conn = self.ANALITIC_RECORD_TRANZACTION_CONNECT()

            df = df.replace(0, np.nan)
            df = df.replace({'None': None, 'nan': None, '<NA>': None, "NaT": None, 'NaN': None, np.nan: None, '': None})
            records = df.to_dict(orient='records')
            insert_query = text(f'''
                                                    INSERT INTO {table_name} ({', '.join(columns_to_update)}) 
                                                    VALUES ({', '.join([':' + col for col in columns_to_update])})
                                                    ON CONFLICT ({', '.join(conflict)}) DO UPDATE 
                                                    SET {', '.join([f"{col} = :{col}" for col in columns_to_update])};''')
            conn.execute(insert_query, records)
            """with conn.begin():
                conn.execute(insert_query, records)
                conn.commit()"""
            del columns_to_update, conflict, df, table_name
            gc.collect()

        except Exception as error:
            print('Подключение не установлено ANALITIC_RECORD_TRANZACTION_INSERT. Жду... ', traceback.format_exc())

            time.sleep(60)





    # обовление с последующей вставкой
    def ANALITIC_UPDATE_AND_INSERT(self,columns_to_update, conflict, df, tabele_name):
        self.ANALITIC_ONLY_UPDATE(columns_to_update, conflict, df, tabele_name)
        self.ANALITIC_ONLY_INSERT(columns_to_update, conflict, df, tabele_name)
        del columns_to_update, conflict, df, tabele_name
        gc.collect()
        return


    # простая вставка без проверки конфликтов
    def ANALITIC_SIMPLE_INSERT(self, columns_to_update, df, tabele_name, conn=None):
        """
        Простая вставка данных без проверки конфликтов.
        Используется когда в таблице нет уникальных ограничений или нужно просто добавить записи.
        """
        for col in df.columns:
            if df[col].dtype.kind in 'ifc':
                df.loc[:, col] = df[col].replace(0, np.nan)
        while True:
            try:
                if conn is None:
                    self.engine_km = self.ANALITIC_ENGINE()
                    conn = self.engine_km.connect()
                    need_commit = True
                else:
                    need_commit = False
                
                df = df.replace({'None': None, 'nan': None, '<NA>': None, "NaT": None, 'NaN': None, np.nan: None, '': None})
                records = df.to_dict(orient='records')
                insert_query = text(f'''
                    INSERT INTO {tabele_name} ({', '.join(columns_to_update)}) 
                    VALUES ({', '.join([':' + col for col in columns_to_update])});''')
                conn.execute(insert_query, records)
                if need_commit:
                    conn.commit()
                    conn.close()
                break
            except exc.IntegrityError as e:
                print(f"Ошибка целостности данных {e}")
                if need_commit:
                    conn.rollback()
                    conn.close()
                raise
            except Exception as error:
                print('Подключение не установлено ANALITIC_SIMPLE_INSERT. Жду... ', traceback.format_exc(), error)
                if need_commit and conn:
                    conn.close()
                time.sleep(60)

    #только вставка
    def ANALITIC_ONLY_INSERT(self,columns_to_update, conflict, df, tabele_name):
        for col in df.columns:
            if df[col].dtype.kind in 'ifc':
                df.loc[:, col] = df[col].replace(0, np.nan)
        while True:
            try:
                self.engine_km = self.ANALITIC_ENGINE()
                df = df.replace({'None': None, 'nan': None, '<NA>': None, "NaT": None, 'NaN': None, np.nan: None,'': None})
                with self.engine_km.connect() as conn:
                        records = df.to_dict(orient='records')
                        insert_query =text(f'''
                                                INSERT INTO {tabele_name} ({', '.join(columns_to_update)}) 
                                                SELECT {', '.join([':' + col for col in columns_to_update])}
                                               
                                                WHERE NOT EXISTS (
                                                    SELECT 1 
                                                    FROM {tabele_name}
                                                    WHERE 1 = 1 and {' AND '.join([f'{col} = :' + col for col in conflict]) 
                                                    if len(conflict) > 1 else f' {conflict[0]} = :{conflict[0]}'}
                                                );
                                               
                                                ''')
                        result = conn.execute(insert_query, records)
                        conn.commit()
                        if result.rowcount > 0:
                            return  True
                        else:
                            return False


            except exc.IntegrityError as e:
                print(f"шибка клчей {e}")
                # обработчик ошибок ключей
                # errorExeptionIntegrityError(e)
            except Exception as error:
                print('Подключение не установлено ANALITIC_ONLY_INSERT. Жду... ', traceback.format_exc())

                time.sleep(60)



    #  только обновление
    def ANALITIC_ONLY_UPDATE(self, columns_to_update, conflict, df, tabele_name, conn=None):
        for col in df.columns:
            if df[col].dtype.kind in 'ifc':
                df.loc[:, col] = df[col].replace(0, np.nan)
        while True:
            try:

                self.engine_km = self.ANALITIC_ENGINE()
                df = df.replace({'None': None, 'nan': None, '<NA>': None, "NaT": None, 'NaN': None, np.nan: None,'': None, 0: None})
                with self.engine_km.connect() as conn:
                    columns_to_update = ', '.join([f"{col} = :{col}" for col in columns_to_update])
                    conflict = ' AND '.join([f"{col} = :{col}" for col in conflict])
                    sql_query = text(f'UPDATE {tabele_name} SET {columns_to_update} WHERE {conflict}')
                    try:
                        conn.execute(sql_query, df.to_dict('records'))
                        conn.commit()
                        break
                    except Exception as error:
                        print(traceback.format_exc())
                        sys.exit()
            except exc.IntegrityError as e:
                print(f"шибка клчей {e}")
                # обработчик ошибок ключей
                # errorExeptionIntegrityError(e)
            except Exception as error:
                print('Подключение не установлено ANALITIC_ONLY_UPDATE. Жду... ', traceback.format_exc())

                time.sleep(60)


    # закрытие пула
    def close_connection_pool_analitik(self):

        if self.engine_km:
            try:
                self.engine_km.dispose()
            except Exception as error:
                print('Ошибка при закрытии пула Analitik ', traceback.format_exc())
                time.sleep(60)
if __name__ == '__main__':
    df = DB_KM().ANALITIC_TO_DATAFRAME("select * from spr_client limit 10")
    print(df)