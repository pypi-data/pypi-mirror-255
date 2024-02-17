from abc import ABC, abstractmethod


# TODO: should we use SqlLiteral instead of ToSQLInterface and all its subclasses?
class ToSQLInterface(ABC):
    """
    An interface for objects that represent structures to be
    inserted into a database.

    Subclasses must implement the `to_sql` method, which should return a string
    representing the SQL representation of the structure.

    Example:
    --------
    class Point(ToSQLInterface):
        def __init__(self, longitude, latitude):
            self.longitude = longitude
            self.latitude = latitude

        def to_sql(self):
            return f"POINT({self.longitude}, {self.latitude})"
    """

    @abstractmethod
    def to_sql(self) -> str:
        pass


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
        return (isinstance(other_point, Point) and
                self.longitude == other_point.longitude and
                self.latitude == other_point.latitude)

    def __repr__(self):
        return f"Point(longitude={self.longitude}, latitude={self.latitude})"


class Now(ToSQLInterface):
    """
    Represents the current time in SQL.
    """

    def to_sql(self):
        return "NOW()"


class CurrentDate(ToSQLInterface):
    """
    Represents the current time in SQL.
    """

    def to_sql(self):
        return "CURDATE()"


class TimeStampDiff(ToSQLInterface):
    """
    Represents the current time in SQL.
    """

    def __init__(self, unit, start, end):
        allowed_units = ("YEAR", "QUARTER", "MONTH", "WEEK", "DAY", "HOUR", "MINUTE", "SECOND", "FRAC_SECOND")
        if unit not in allowed_units:
            raise ValueError(f"unit must be one of {allowed_units}")
        self.unit = unit
        self.start = start
        self.end = end

    def to_sql(self):
        return f"TIMESTAMPDIFF({self.unit}, {self.start}, {self.end})"


class Count(ToSQLInterface):
    """Represents a COUNT() function in SQL."""

    def __init__(self, column_name="*"):
        self.column_name = column_name

    def to_sql(self):
        return f"COUNT({self.column_name})"
