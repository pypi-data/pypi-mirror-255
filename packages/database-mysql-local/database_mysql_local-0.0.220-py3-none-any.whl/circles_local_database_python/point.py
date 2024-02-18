from .to_sql_interface import ToSQLInterface


class Point(ToSQLInterface):
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

    def to_sql(self):
        return f"POINT ({self.longitude}, {self.latitude})"

    @staticmethod
    def create_select_stmt(column_name: str):
        return f"ST_X({column_name}), ST_Y({column_name})"

    def __eq__(self, other_point):
        if isinstance(other_point, Point):
            return self.longitude == other_point.longitude and self.latitude == other_point.latitude
        return False
