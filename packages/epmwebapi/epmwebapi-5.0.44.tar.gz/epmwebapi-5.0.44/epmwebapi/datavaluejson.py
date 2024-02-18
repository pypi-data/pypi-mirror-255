import dateutil
import datetime
from datetime import timezone
import numpy as np
from typing import Union

class DataValueJSON(object):
    """
    Class representing a DataValue.
    """
    def __init__(self, value, statusCode, timestamp, dataTypeId=None):
        """
        Creates a new DataValue.

        :param value: Value of this DataValue.
        :type value: Union[datetime.datetime|int|bool|float|str]
        :param statusCode: OPC UA status code.
        :type statusCode: int
        :param timestamp: Timestamp of this DataValue.
        :type timestamp: datetime.datetime
        :param dataTypeId: ID of data type. Default is None.
        :type dataTypeId: object
        """
        self._value = value
        self._statusCode = statusCode
        if type(timestamp) == str:
          try:
            self._timestamp = dateutil.parser.parse(timestamp).astimezone(timezone.utc)
          except OverflowError as error:
            self._timestamp = datetime.datetime(1,1,1,0,0,tzinfo=datetime.timezone.utc)
        else:
          self._timestamp = timestamp
        self._dataTypeId = dataTypeId

    @property
    def value(self) -> Union[datetime.datetime,int,bool,float,str]:
      """
      Returns the value from this DataValue.

      :return: The value of this DataValue as a `datetime.datetime`, an `int`, a `bool`, a `float`, or a `str`.
      :rtype: Union[datetime.datetime|int|bool|float|str]
      """
      return self._value

    @property
    def statusCode(self) -> int:
      """
      Returns an OPC UA status code (quality) for this DataValue.

      :return: An OPC UA status code.
      :rtype: int
      """
      return self._statusCode

    @property
    def timestamp(self) -> datetime.datetime:
      """
      Returns the source timestamp from this DataValue.

      :return: A `datetime.datetime` value representing a source timestamp.
      :rtype: datetime.datetime
      """
      return self._timestamp

    def toDict(self):
        """
        Returns this `DataValueJSON` object as a dictionary.

        :return: A dictionary containing `value`, `statusCode` (quality), and `timestamp` of this DataValue
        :rtype: dict
        """
        value = self._value.isoformat() if type(self._value) == datetime.datetime else self._value
        if self._dataTypeId is None:
            return {'value': value, 'quality': self._statusCode,
                   'timestamp' : self._timestamp.isoformat()}
        else:
            return {'value': value, 'quality': self._statusCode,
                    'timestamp': self._timestamp.isoformat(), 'dataTypeId': self._dataTypeId}
