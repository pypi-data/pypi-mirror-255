class Station:
    """Baseclass for a station returned from a pyaro.timeseries.Reader.

    This is the minimum set of columns required for a reader to return.
    A reader is welcome to return a self-implemented subclass of
    Station.

    All Station fields are accessible as a dict or as property, e.g.
    ```
    td = Station()
    print(td.station)
    print(td["station"])
    ```

    """

    def __init__(self, fields: dict = None) -> None:
        self._fields = {
            "station": "",
            "latitude": float("nan"),
            "longitude": float("nan"),
            "altitude": float("nan"),
            "long_name": "",
            "country": "",
            "url": "",
        }
        if fields:
            self.set_fields(fields)
        pass

    def __getitem__(self, key):
        """access the data as a dict"""
        return self._fields[key]

    def keys(self):
        """all available data-fields, excluding variable and units which are
        considered metadata"""
        return self._fields.keys()

    def set_fields(self, fields: dict):
        """Initialization code for this station.
        Only known data-fields will be read from data, i.e. it is not
        possible to extend TimeseriesData without subclassing.

        :param fields: dict with the required fields:
            station, latitude, longitude, altitude, long_name, country, url
        :raises KeyError: on missing field
        """
        for key in self.keys():
            if not key in fields:
                raise KeyError(f"{key} not in fields")
        if abs(fields["latitude"]) > 90:
            raise Exception(f"latitude out of bounds: {fields['latitude']}")
        if abs(fields["longitude"]) > 180:
            raise Exception(f"longitude out of bounds: {fields['longitude']}")
        for key in self.keys():
            self._fields[key] = fields[key]
        return

    @property
    def station(self) -> str:
        """Station name, unique for the reader.

        :return: station name
        """
        return self._fields["station"]

    @property
    def latitude(self) -> float:
        """Latitude in range [-90, 90]

        :return: latitude
        """
        return self._fields["latitude"]

    @property
    def longitude(self) -> float:
        """Longitude in range [-180, 180]

        :return: longitude
        """
        return self._fields["longitude"]

    @property
    def altitude(self) -> float:
        """altitude in range [-180, 180]

        :return: altitude
        """
        return self._fields["altitude"]

    @property
    def long_name(self) -> str:
        """Long station name, does not need to be unique.

        :return: long name
        """
        return self._fields["long_name"]

    @property
    def country(self) -> str:
        """Station country as ISO 3166-2 code

        :return: country
        """
        return self._fields["country"]

    @property
    def url(self) -> str:
        """url to more information about the station

        :return: url
        """
        return self._fields["url"]

    def __str__(self):
        return self._fields.__str__()
