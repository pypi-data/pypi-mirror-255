import numpy as np

from pylick.__config__ import __table__

__all__ = ["IndexLibrary"]
    
class IndexLibrary(object):
    """Loads the index library.

    To show the full table of the available indices and assosiated keys use

    >>> from pylick.indices import IndexLibrary
    >>> lib = IndexLibrary()
    >>> print(lib)
        

    Args:
        index_keys (list, optional): identifiers of the indices to be loaded. First column of `file_table`. Defaults to None (all the available indices).
        file_table (str, optional): path to the file containing the indices definitions. Must be formatted as the default one located at `data/index_table.dat`.

    Returns: 
        IndexLibrary: Itself, to allow chaining calls.
    """

    def __init__(self, index_keys=None, file_table=None):

        if file_table is None:
            file_table = __table__
        self.source = file_table
        self._data  = self._read_index_list(file_table)

        if index_keys is not None:
            self._data  = self.__getitem__(index_keys)

        self.regions    = np.array([[v[j] for j in ['blue', 'centr', 'red']] for k, v in self._data.items()])
        self.names      = np.array([v[j] for j in ['name'] for k, v in self._data.items()])
        self.units      = np.array([v[j] for j in ['unit'] for k, v in self._data.items()])
        self.tex_names  = np.array([v[j] for j in ['tex_name'] for k, v in self._data.items()])
        self.tex_units  = np.array([v[j] for j in ['tex_unit'] for k, v in self._data.items()])


    def find(self, name):
        """Finds indices in the table.

        Args:
            name (str): the name (or part of it) of the index to search in the table.

        Returns:
            list: list of the indices found.
        """
        
        r = []
        for item in self._data.items():
            tabname = item[1]['name']
            if name in tabname:
                r.append(tabname)
        return r

    def add(self, center, blue, red, name, unit, tex_name, tex_unit):
        """.. note:: TO BE IMPLEMENTED
        Adds an index at the end of the file. Re-sorts(?) and saves(?) the library."""
        print("To be implemented")

    def pop(self, key):
        """.. note:: TO BE IMPLEMENTED
        Removes an index from the library. Re-sorts(?) the library."""
        print("To be implemented")

    @classmethod
    def _read_index_list(self, file_table):
        """Read index table

        Args:
            file_table (str): path to the file containing the indices definitions.

        Returns:
            dict: dictionary of indices and associated spectral regions (name, unit, centr, blue, red, tex_name, tex_unit).
        """

        data = {}

        with open(file_table, 'r') as f:
            data = {}
            for i, line in enumerate(f):
                if line[0] != '#':
                    l = line.split()
                    try:
                        attr = dict(
                            centr       = (float(l[3]), float(l[4])),
                            blue        = (float(l[5]), float(l[6])),
                            red         = (float(l[7]), float(l[8])),
                            name        = l[1],
                            unit        = l[2],
                            tex_name    = l[9],
                            tex_unit    = l[10]
                        )
                    except IndexError:
                        print("> Error while loading the index table at line: {:d}. Perhaps a `#` is missing?".format(i))
                    except:
                        print("> Error while loading the index table. It must be formatted as the default one located at `data/index_table.dat`.")
                    ID = int(l[0])
                    data[ID] = attr
        return data

    def __repr__(self):
        return "IndexLibrary(file_table='{:s}')".format(self.source)


    def __str__(self):
        msg = "{:4s}{:9s}{:10s}{:19s}{:19s}{:19s}{:10s}\n".format(
            "ID", "name", "unit", "blue", "centr", "red", "tex_name")
        msg = msg + '-'*len(msg) + '\n'
        for key, val in self._data.items():
            msg = msg + "{:<4d}{:9s}{:10s}{:8.3f}-{:8.3f}  {:8.3f}-{:8.3f}  {:8.3f}-{:8.3f}  {:s}\n".format(
                key,val['name'],val['unit'],val['blue'][0],val['blue'][1],val['centr'][0],val['centr'][1],
                val['red'][0],val['red'][1],val['tex_name'])
        return msg  


    def __len__(self):
        return len(self._data)


    def __getitem__(self, keys):
        d = self._data
        return {k:d[k] for k in keys if k in d}
