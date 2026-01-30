
import pandas as pd

from dotenv import load_dotenv

from connect.db_loyal import DB_KM


load_dotenv()
pd.set_option("expand_frame_repr", False)
pd.set_option('display.max_colwidth', None)

class BaseClass:
    _lickhouse = None
    def __new__(cls, *args, **kwargs):
        if not cls._lickhouse:

            print(f"[Init] {cls.__name__}")
            cls._lickhouse = super().__new__(cls)
        return cls._lickhouse

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_km = DB_KM()
            



if __name__ == '__main__':

    # Создание экземпляра и вызов метода dsdsdsd
    base_class_instance = BaseClass()

