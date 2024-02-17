import csv
import numpy as np
from pyaro.timeseries import Data, NpStructuredData, Flag, Station
import pyaro.timeseries.AutoFilterReaderEngine


def _lookup_function():
    from geocoder_reverse_natural_earth import Geocoder_Reverse_NE

    geo = Geocoder_Reverse_NE()
    return lambda lat, lon: geo.lookup_nearest(lat, lon)["ISO_A2_EH"]


class CSVTimeseriesReader(pyaro.timeseries.AutoFilterReaderEngine.AutoFilterReader):
    _col_keys = (
        "variable",
        "units",
        "value",
        "flag",
        "station",
        "longitude",
        "latitude",
        "altitude",
        "start_time",
        "end_time",
        "country",
        "standard_deviation",
    )

    def __init__(
        self,
        filename,
        columns={
            "variable": 0,
            "station": 1,
            "longitude": 2,
            "latitude": 3,
            "value": 4,
            "units": 5,
            "start_time": 6,
            "end_time": 7,
            "altitude": "0",
            "country": "NO",
            "standard_deviation": "NaN",
            "flag": "0",
        },
        variable_units={"SOx": "Gg", "NOx": "Mg"},
        country_lookup=False,
        csvreader_kwargs={"delimiter": ","},
        filters=[],
    ):
        """open a new csv timeseries-reader

        :param filename_or_obj_or_url: path-like object to csv-file
        :param columns: mapping of column in the csv-file to key, see col_keys().
            Column-numbering starts with 0.
            If column is a string rather than a integer, it is a constant value and not
            read from the csv-table. This is also true for numerical values,
            i.e. altitude or standard_deviation.
        :variable_units: dict translating variable-names to units, e.g. overwrite units given in columns
        :country_lookup: use pyaro_readers.geocoder_reverse_natural_earth to lookup country-codes from lat/lon
        :csvreader_kwargs: kwargs send directly to csv.reader module
        :filters: default auto-filter filters
        """
        self._filename = filename
        self._stations = {}
        self._data = {}  # var -> {data-array}
        self._set_filters(filters)
        if country_lookup:
            lookupISO2 = _lookup_function()
        with open(self._filename, newline="") as csvfile:
            crd = csv.reader(csvfile, **csvreader_kwargs)
            for row in crd:
                r = {}
                for t in self.col_keys():
                    if isinstance(columns[t], str):
                        r[t] = columns[t]
                    else:
                        r[t] = row[columns[t]]
                for t in (
                    "value",
                    "latitude",
                    "longitude",
                    "altitude",
                    "standard_deviation",
                ):
                    r[t] = float(r[t])
                for t in ("start_time", "end_time"):
                    r[t] = np.datetime64(r[t])

                if r["variable"] in variable_units:
                    r["units"] = variable_units[r["variable"]]
                if country_lookup:
                    r["country"] = lookupISO2(r["latitude"], r["longitude"])
                if r["variable"] in self._data:
                    da = self._data[r["variable"]]
                    if da.units != r["units"]:
                        raise Exception(
                            f"unit change from '{da.units}' to '{r['units']}'"
                        )
                else:
                    da = NpStructuredData(r["variable"], r["units"])
                    self._data[r["variable"]] = da
                da.append(
                    *[
                        r[x]
                        for x in (
                            "value",
                            "station",
                            "latitude",
                            "longitude",
                            "altitude",
                            "start_time",
                            "end_time",
                            "flag",
                            "standard_deviation",
                        )
                    ]
                )
                if not r["station"] in self._stations:
                    self._stations[r["station"]] = Station(
                        {
                            "station": r["station"],
                            "longitude": r["longitude"],
                            "latitude": r["latitude"],
                            "altitude": r["altitude"],
                            "country": r["country"],
                            "url": "",
                            "long_name": r["station"],
                        }
                    )

    @classmethod
    def col_keys(cls):
        """Column keys possible to initialize with this reader.

        :return: list of columns possible to initialize with columns argument of this reader
        """
        return cls._col_keys

    def _unfiltered_data(self, varname) -> Data:
        return self._data[varname]

    def _unfiltered_stations(self) -> dict[str, Station]:
        return self._stations

    def _unfiltered_variables(self) -> list[str]:
        return self._data.keys()

    def close(self):
        pass


class CSVTimeseriesEngine(pyaro.timeseries.AutoFilterReaderEngine.AutoFilterEngine):
    def reader_class(self):
        return CSVTimeseriesReader

    def open(self, filename, *args, **kwargs) -> CSVTimeseriesReader:
        return self.reader_class()(filename, *args, **kwargs)

    def description(self):
        return "Simple reader of csv-files using python csv-reader"

    def url(self):
        return "https://github.com/metno/pyaro"
