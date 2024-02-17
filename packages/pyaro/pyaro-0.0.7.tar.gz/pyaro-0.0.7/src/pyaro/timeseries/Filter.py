import abc
from collections import defaultdict
import csv
from datetime import datetime
import inspect
import types

import numpy as np

from .Data import Data, Flag
from .Station import Station


class Filter(abc.ABC):
    """Base-class for all filters used from pyaro-Readers"""

    time_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, **kwargs):
        """constructor of Filters. All filters must have a default constructor without kwargs
        for an empty filter object"""
        return

    def args(self) -> list:
        """retrieve the kwargs possible to retrieve a new object of this filter with filter restrictions

        :return: a dictionary possible to use as kwargs for the new method
        """
        ba = inspect.signature(self.__class__.__init__).bind(0)
        ba.apply_defaults()
        args = ba.arguments
        args.pop("self")
        return args

    @abc.abstractmethod
    def init_kwargs(self) -> dict:
        """return the init kwargs"""

    @abc.abstractmethod
    def name(self) -> str:
        """Return a unique name for this filter

        :return: a string to be used by FilterFactory
        """

    def filter_data(self, data: Data, stations: [Station], variables: [str]) -> Data:
        """Filtering of data

        :param data: Data of e.g. a Reader.data(varname) call
        :param stations: List of stations, e.g. from a Reader.stations() call
        :param variables: variables, i.e. from a Reader.variables() call
        :return: a updated Data-object with this filter applied
        """
        return data

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        """Filtering of stations list

        :param stations: List of stations, e.g. from a Reader.stations() call
        :return: dict of filtered stations
        """
        return stations

    def filter_variables(self, variables: [str]) -> [str]:
        """Filtering of variables

        :param variables: List of variables, e.g. from a Reader.variables() call
        :return: List of filtered variables.
        """
        return variables

    def __repr__(self):
        return f"{type(self).__name__}(**{self.init_kwargs()})"


class DataIndexFilter(Filter):
    """A abstract baseclass implementing filter_data by an abstract method
    filter_data_idx"""

    @abc.abstractmethod
    def filter_data_idx(self, data: Data, stations: dict[str, Station], variables: str):
        """Filter data to an index which can be applied to Data.slice(idx) later

        :return: a index for Data.slice(idx)
        """
        pass

    def filter_data(self, data: Data, stations: dict[str, Station], variables: str):
        idx = self.filter_data_idx(data, stations, variables)
        return data.slice(idx)


class FilterFactoryException(Exception):
    pass


class FilterFactory:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(FilterFactory, cls).__new__(cls)
            cls.instance._filters = {}
        return cls.instance

    def register(self, filter: Filter):
        """Register a new filter to the factory
        with a filter object (might be empty)

        :param filter: a filter implementation
        """
        if filter.name() in self._filters:
            raise FilterFactoryException(
                f"Cannot use {filter}: {filter.name()} already in use by {self.get(filter.name())}"
            )
        self._filters[filter.name()] = filter

    def get(self, name, **kwargs):
        """Get a filter by name. If kwargs are given, they will be send to the
        filters new method

        :param name: a filter-name
        :return: a filter, optionally initialized
        """
        filter = self._filters[name]
        return filter.__class__(**kwargs)

    def list(self) -> dict[str, Filter]:
        """List all available filter-names and their initalizations"""
        return types.MappingProxyType(self._filters)


filters = FilterFactory()


def registered_filter(filter_class):
    """Simple decorator to register a FilterClass to the FilterFactory on construction

    :param filter_class: class to register
    """
    filters.register(filter_class())
    return filter_class


class FilterCollectionException(Exception):
    pass


class FilterCollection:
    def __init__(self, filterlist=[]):
        """A collection of DataIndexFilters which can be appied together.

        :param filterlist: _description_, defaults to []
        :return: _description_
        """
        self._filters = []
        tmp_filterlist = []
        if isinstance(filterlist, dict):
            for name, kwargs in filterlist.items():
                tmp_filterlist.append(filters.get(name, **kwargs))
        else:
            tmp_filterlist = filterlist
        for f in tmp_filterlist:
            self.add(f)

    def add(self, difilter: DataIndexFilter):
        if not isinstance(difilter, DataIndexFilter):
            raise FilterCollectionException(
                f"filter not a DataIndexFilter, so can't add to collection"
            )
        else:
            self._filters.append(difilter)

    def filter_data(
        self, data: Data, stations: dict[str, Station], variables: str
    ) -> Data:
        """Filter data with all filters in this collection.

        :param data: Data from a timeseries-reader, i.e. retrieved by ts.data(varname)
        :param stations: stations-dict of a reader, i.e. retrieved by ts.stations()
        :param variables: variables of a reader, i.e. retrieved by ts.variables()
        :return: _description_
        """
        for fi in self._filters:
            data = fi.filter_data(data, stations, variables)
        return data

    def filter(self, ts_reader, variable: str) -> Data:
        """Filter the data for a variable of a reader with all filters in this collection.

        :param ts_reader: a timeseries-reader instance
        :param variable: a valid variable-name
        :return: filtered data
        """
        stations = ts_reader.stations()
        variables = ts_reader.variables()
        data = ts_reader.data(variable)
        return self.filter_data(data, stations, variables)


@registered_filter
class VariableNameFilter(Filter):
    """Filter to change variable-names and/or include/exclude variables"""

    def __init__(
        self,
        reader_to_new: dict[str, str] = {},
        include: [str] = [],
        exclude: [str] = [],
    ):
        """Create a new variable name filter.

        :param reader_to_new: dictionary from readers-variable names to new variable-names,
            e.g. used in your project, defaults to {}
        :param include: list of variables to include only (new names if changed), defaults to []
            meaning keep all variables unless excluded.
        :param exclude: list of variables to exclude (new names if changed), defaults to []
        """
        self._reader_to_new = reader_to_new
        self._new_to_reader = {v: k for k, v in reader_to_new.items()}
        self._include = set(include)
        self._exclude = set(exclude)
        return

    def init_kwargs(self):
        return {
            "reader_to_new": self._reader_to_new,
            "include": list(self._include),
            "exclude": list(self._exclude),
        }

    def name(self):
        return "variables"

    def reader_varname(self, new_variable: str) -> str:
        """convert a new variable name to a reader-variable name

        :param new_variable: variable name after translation
        :return: variable name in the original reader
        """
        return self._new_to_reader.get(new_variable, new_variable)

    def new_varname(self, reader_variable: str) -> str:
        """convert a reader-variable to a new variable name

        :param reader_variable: variable as used in the reader
        :return: variable name after translation
        """
        return self._reader_to_new.get(reader_variable, reader_variable)

    def filter_data(self, data, stations, variables):
        """Translate data's variable"""
        data._set_variable(self._reader_to_new.get(data.variable, data.variable))
        return data

    def filter_variables(self, variables: [str]) -> [str]:
        """change variable name and reduce variables applying include and exclude parameters

        :param variables: variable names as in the reader
        :return: valid variable names in translated nomenclature
        """
        newlist = []
        for x in variables:
            newvar = self.new_varname(x)
            if self.has_variable(newvar):
                newlist.append(newvar)
        return newlist

    def has_variable(self, variable) -> bool:
        """check if a variable-name is in the list of variables applying include and exclude

        :param variable: variable name in translated, i.e. new scheme
        :return: True or False
        """
        if len(self._include) > 0:
            if not variable in self._include:
                return False
        if variable in self._exclude:
            return False
        return True

    def has_reader_variable(self, variable) -> bool:
        """Check if variable-name is in the list of variables applying include and exclude

        :param variable: variable as returned from the reader
        :return: True or False
        """
        new_var = self.new_varname(variable)
        return self.has_variable(new_var)


class StationReductionFilter(DataIndexFilter):
    """Abstract method for all filters, which work on reducing the number of stations only.

    The filtering of stations has to be implemented by subclasses, while filtering of data
    is already implemented.
    """

    @abc.abstractmethod
    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        pass

    def filter_data_idx(self, data: Data, stations: dict[str, Station], variables: str):
        stat_names = self.filter_stations(stations).keys()
        dstations = data.stations
        stat_names = np.fromiter(stat_names, dtype=dstations.dtype)
        index = np.in1d(dstations, stat_names)
        return index


@registered_filter
class StationFilter(StationReductionFilter):
    def __init__(self, include: [str] = [], exclude: [str] = []):
        self._include = set(include)
        self._exclude = set(exclude)
        return

    def init_kwargs(self):
        return {"include": list(self._include), "exclude": list(self._exclude)}

    def name(self):
        return "stations"

    def has_station(self, station) -> bool:
        if len(self._include) > 0:
            if not station in self._include:
                return False
        if station in self._exclude:
            return False
        return True

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        return {s: v for s, v in stations.items() if self.has_station(s)}


@registered_filter
class CountryFilter(StationReductionFilter):
    def __init__(self, include: [str] = [], exclude: [str] = []):
        """Filter countries by ISO2 names (capitals!)

        :param include: countries to include, defaults to [], meaning all countries
        :param exclude: countries to exclude, defaults to [], meaning none
        """
        self._include = set(include)
        self._exclude = set(exclude)
        return

    def init_kwargs(self):
        return {"include": list(self._include), "exclude": list(self._exclude)}

    def name(self):
        return "countries"

    def has_country(self, country) -> bool:
        if len(self._include) > 0:
            if not country in self._include:
                return False
        if country in self._exclude:
            return False
        return True

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        return {s: v for s, v in stations.items() if self.has_country(v.country)}


class BoundingBoxException(Exception):
    pass


@registered_filter
class BoundingBoxFilter(StationReductionFilter):
    """Filter using geographical bounding-boxes"""

    def __init__(
        self,
        include: [(float, float, float, float)] = [],
        exclude: [(float, float, float, float)] = [],
    ):
        """Filter using geographical bounding-boxes. Coordinates should be given in the range
        [-180,180] (degrees_east) for longitude and [-90,90] (degrees_north) for latitude.
        Order of coordinates is clockwise starting with north, i.e.: (north, east, south, west) = NESW

        :param include: bounding boxes to include. Each bounding box is a tuple of four float for
            (NESW),  defaults to [] meaning no restrictions
        :param exclude: bounding boxes to exclude. Defaults to []
        :raises BoundingBoxException: on any errors of the bounding boxes
        """
        for tup in include:
            self._test_bounding_box(tup)
        for tup in exclude:
            self._test_bounding_box(tup)

        self._include = set(include)
        self._exclude = set(exclude)
        return

    def _test_bounding_box(self, tup):
        """_summary_

        :param tup: A bounding-box tuple of form (north, east, south, west)
        :raises BoundingBoxException: on any errors of the bounding box
        """
        if len(tup) != 4:
            raise BoundingBoxException(f"({tup}) has not four NESW elements")
        if not (-90 <= tup[0] <= 90):
            raise BoundingBoxException(f"north={tup[0]} not within [-90,90] in {tup}")
        if not (-90 <= tup[2] <= 90):
            raise BoundingBoxException(f"south={tup[2]} not within [-90,90] in {tup}")
        if not (-180 <= tup[1] <= 180):
            raise BoundingBoxException(f"east={tup[1]} not within [-180,180] in {tup}")
        if not (-180 <= tup[3] <= 180):
            raise BoundingBoxException(f"west={tup[3]} not within [-180,180] in {tup}")
        if tup[0] < tup[2]:
            raise BoundingBoxException(f"north={tup[0]} < south={tup[2]} in {tup}")
        if tup[1] < tup[3]:
            raise BoundingBoxException(f"east={tup[1]} < west={tup[3]} in {tup}")
        return True

    def init_kwargs(self):
        return {"include": list(self._include), "exclude": list(self._exclude)}

    def name(self):
        return "bounding_boxes"

    def has_location(self, latitude, longitude):
        """Test if the locations coordinates are part of this filter.

        :param latitude: latitude coordinate in degree_north [-90, 90]
        :param longitude: longitude coordinate in degree_east [-180, 180]
        """
        if len(self._include) == 0:
            inside_include = True
        else:
            inside_include = False
            for n, e, s, w in self._include:
                if not inside_include:  # one inside test is enough
                    if s <= latitude <= n:
                        if w <= longitude <= e:
                            inside_include = True

        if not inside_include:
            return False  # no more tests required

        outside_exclude = True
        for n, e, s, w in self._exclude:
            if (
                outside_exclude
            ):  # if known to be inside of any other exclude BB, no more tests
                if s <= latitude <= n:
                    if w <= longitude <= e:
                        outside_exclude = False

        return inside_include & outside_exclude

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        return {
            s: v
            for s, v in stations.items()
            if self.has_location(v.latitude, v.longitude)
        }


@registered_filter
class FlagFilter(DataIndexFilter):
    def __init__(self, include: [Flag] = [], exclude: [Flag] = []):
        """Filter data by Flags

        :param include: flags to include, defaults to [], meaning all flags
        :param exclude: flags to exclude, defaults to [], meaning none
        """
        self._include = set(include)
        if len(include) == 0:
            all_include = set([f for f in Flag])
        else:
            all_include = self._include
        self._exclude = set(exclude)
        self._valid = all_include.difference(self._exclude)
        return

    def name(self):
        return "flags"

    def init_kwargs(self):
        return {"include": list(self._include), "exclude": list(self._exclude)}

    def usable_flags(self):
        return self._valid

    def filter_data_idx(self, data: Data, stations: dict[str, Station], variables: str):
        validflags = np.fromiter(self._valid, dtype=data.flags.dtype)
        index = np.in1d(data.flags, validflags)
        return index


class TimeBoundsException(Exception):
    pass


@registered_filter
class TimeBoundsFilter(DataIndexFilter):
    def __init__(
        self,
        start_include: [(str, str)] = [],
        start_exclude: [(str, str)] = [],
        startend_include: [(str, str)] = [],
        startend_exclude: [(str, str)] = [],
        end_include: [(str, str)] = [],
        end_exclude: [(str, str)] = [],
    ):
        """Filter data by start and/or end-times of the measurements. Each timebound consists
        of a bound-start and bound-end (both included). Timestamps are given as YYYY-MM-DD HH:MM:SS

        :param start_include: list of tuples of start-times, defaults to [], meaning all
        :param start_exclude: list of tuples of start-times, defaults to []
        :param startend_include: list of tuples of start and end-times, defaults to [], meaning all
        :param startend_exclude: list of tuples of start and end-times, defaults to []
        :param end_include: list of tuples of end-times, defaults to [], meaning all
        :param end_exclude: list of tuples of end-times, defaults to []
        :raises TimeBoundsException: on any errors with the time-bounds
        """
        self._start_include = self._str_list_to_datetime_list(start_include)
        self._start_exclude = self._str_list_to_datetime_list(start_exclude)
        self._startend_include = self._str_list_to_datetime_list(startend_include)
        self._startend_exclude = self._str_list_to_datetime_list(startend_exclude)
        self._end_include = self._str_list_to_datetime_list(end_include)
        self._end_exclude = self._str_list_to_datetime_list(end_exclude)
        return

    def name(self):
        return "time_bounds"

    def _str_list_to_datetime_list(self, tuple_list: [(str, str)]):
        retlist = []
        for start, end in tuple_list:
            start_dt = datetime.strptime(start, self.time_format)
            end_dt = datetime.strptime(end, self.time_format)
            if start_dt > end_dt:
                raise TimeBoundsException(
                    f"(start later than end) for (f{start} > f{end})"
                )
            retlist.append((start_dt, end_dt))
        return retlist

    def _datetime_list_to_str_list(self, tuple_list) -> [(str, str)]:
        retlist = []
        for start_dt, end_dt in tuple_list:
            retlist.append(
                (start_dt.strftime(self.time_format), end_dt.strftime(self.time_format))
            )
        return retlist

    def init_kwargs(self):
        return {
            "start_include": self._datetime_list_to_str_list(self._start_include),
            "start_exclude": self._datetime_list_to_str_list(self._start_exclude),
            "startend_include": self._datetime_list_to_str_list(self._startend_include),
            "startend_exclude": self._datetime_list_to_str_list(self._startend_exclude),
            "end_include": self._datetime_list_to_str_list(self._startend_include),
            "end_exclude": self._datetime_list_to_str_list(self._startend_exclude),
        }

    def _index_from_include_exclude(self, times1, times2, includes, excludes):
        idx = times1.astype("bool")
        if len(includes) == 0:
            idx[:] = True
        else:
            idx[:] = False
            for start, end in includes:
                idx |= (start <= times1) & (times2 <= end)

        for start, end in excludes:
            idx &= (times1 < start) | (end < times2)

        return idx

    def has_envelope(self):
        """Check if this filter has an envelope, i.e. a earliest and latest time"""
        return (
            len(self._start_include)
            or len(self._startend_include)
            or len(self._end_include)
        )

    def envelope(self) -> (datetime, datetime):
        """Get the earliest and latest time possible for this filter.

        :return: earliest start and end-time (approximately)
        :raises TimeBoundsException: if has_envelope() is False, or internal errors
        """
        if not self.has_envelope():
            raise TimeBoundsException(
                "TimeBounds-envelope called but no envelope exists"
            )
        start = datetime.max
        end = datetime.min
        for s, e in self._start_include + self._startend_include + self._end_include:
            start = min(start, s)
            end = max(end, s)
        if end < start:
            raise TimeBoundsException(
                f"TimeBoundsEnvelope end < start: {end} < {start}"
            )
        return (start, end)

    def contains(self, dt_start, dt_end):
        """Test if datetimes in dt_start, dt_end belong to this filter

        :param dt_start: numpy array of datetimes
        :param dt_end: numpy array of datetimes
        :return: numpy boolean array with True/False values
        """
        idx = self._index_from_include_exclude(
            dt_start, dt_start, self._start_include, self._start_exclude
        )
        idx &= self._index_from_include_exclude(
            dt_start, dt_end, self._startend_include, self._startend_exclude
        )
        idx &= self._index_from_include_exclude(
            dt_end, dt_end, self._end_include, self._end_exclude
        )
        return idx

    def filter_data_idx(self, data: Data, stations: dict[str, Station], variables: str):
        return self.contains(data.start_times, data.end_times)


@registered_filter
class TimeVariableStationFilter(DataIndexFilter):
    def __init__(self, exclude=[], exclude_from_csvfile=""):
        """Exclude combinations of variable station and time from the data

        This filter is really a cleanup of the database, but sometimes it is not possible to
        modify the original database and the cleanup needs to be done on a filter basis.

        :param exclude: tuple of 4 elements: start-time, end-time, variable, station
        :param exclude_from_csvfile: this is a helper option to enable a large list of excludes
            to be read from a "\t" separated file with columns
                start \t end \t variable \t station
            where start and end are timestamps of format YYYY-MM-DD HH:MM:SS in UTC, e.g.
            the year 2020 is:
                2020-01-01 00:00:00 \t 2020-12-31 23:59:59 \t ...
        """
        csvexclude = self._excludes_from_csv(exclude_from_csvfile)
        self._exclude = self._order_exclude(exclude + csvexclude)

    def _excludes_from_csv(self, file):
        csvexcludes = []
        if file:
            with open(file, "rt", newline="") as fh:
                crd = csv.reader(fh, delimiter="\t")
                for row in crd:
                    try:
                        if len(row) == 0:
                            continue
                        if row[0].startswith("#"):
                            continue
                        if len(row) < 4:
                            raise Exception(f"need 4 elements in row, got {len(row)}")
                        datetime.strptime(row[0], self.time_format)
                        datetime.strptime(row[1], self.time_format)
                        csvexcludes.append((row[0], row[1], row[2], row[3]))
                    except Exception as ex:
                        raise Exception(
                            f"malformated TimeVariableStationFilter exclude file, row: {row}",
                            ex,
                        )
        return csvexcludes

    def _order_exclude(self, exclude):
        """Order excludes to a dict of: [variable][start_time][end_time] -> list[stations]

        :param excludes: tuples of start-time, end-time, variable, station
        """
        retval = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
        for start_time, end_time, variable, station in exclude:
            # make sure start and end_time can be parsed
            datetime.strptime(start_time, self.time_format)
            datetime.strptime(end_time, self.time_format)
            retval[variable][start_time][end_time].append(station)
        return retval

    def init_kwargs(self):
        retval = []
        for var, start_times in sorted(self._exclude.items()):
            for start_time, end_times in sorted(start_times.items()):
                for end_time, stations in sorted(end_times.items()):
                    for station in sorted(stations):
                        retval.append((start_time, end_time, var, station))
        # sort by start_time
        retval.sort(key=lambda x: x[1])
        return {"exclude": retval}

    def name(self):
        return "time_variable_station"

    def filter_data_idx(self, data: Data, stations: dict[str, Station], variables: str):
        idx = data.start_times.astype(bool)
        idx |= True
        if data.variable in self._exclude:
            for start_time, end_times in self._exclude[data.variable].items():
                start_time_dt = datetime.strptime(start_time, self.time_format)
                for end_time, stations in end_times.items():
                    end_time_dt = datetime.strptime(end_time, self.time_format)
                    dstations = data.stations
                    stat_names = np.fromiter(stations, dtype=dstations.dtype)
                    exclude_idx = np.in1d(dstations, stat_names)
                    exclude_idx &= (start_time_dt <= data.start_times) & (
                        end_time_dt > data.start_times
                    )
                    idx &= np.logical_not(exclude_idx)
        return idx


if __name__ == "__main__":
    for name, fil in filters._filters.items():
        assert name == fil.name()
        print(name, fil.args())
        print(fil)
