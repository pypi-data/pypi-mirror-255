import os, time
from pathlib import Path, PurePath

import mhi.common.path
from mhi.common.remote import Application
from mhi.common.collection import IndexableDict

from .remote import Remotable, rmi, rmi_property, deprecated, requires

#===============================================================================
# Datafiles indexable dictionary
#===============================================================================

class Datafiles(IndexableDict):
    """
    An indexable dictionary of datafiles.

    Adds full pathname aliases, to allow datafiles with the same names
    but different paths to be retrieved, in addition to retrieving
    datafiles by just their final path component (if unique).
    """

    def __init__(self, datafiles):
        super().__init__((Path(df.filename), df) for df in datafiles)
        self._aliases = {Path(df.name): Path(df.filename)
                         for df in self.values()}

    def __getitem__(self, key):
        """
        If key is a string, convert to a path for case-insensitve lookup.
        """

        if isinstance(key, str):
            key = Path(key)

        key = self._aliases.get(key, key)
        return super().__getitem__(key)

    def __repr__(self):
        paths = list(self.keys())
        if len(paths) == 0:
            return "Datafiles[]"

        root = next((parent for parent in paths[0].parents
                     if all(path.is_relative_to(parent) for path in paths)),
                    None)
        if root:
            dfs = ", ".join("{!s}={!r}".format(path.relative_to(root), df)
                            for path, df in self.items())
            dfs += ", root={!s}".format(root)
        else:
            dfs = ", ".join("{!s}={!r}".format(path, df)
                            for path, df in self.items())

        return "Datafiles[" + dfs + "]"


#===============================================================================
# Enerplot Application
#===============================================================================

class Enerplot(Application, Remotable):

    """
    The Enerplot Application

    This object is a proxy object, used to communicate with a running
    Enerplot Application.
    """

    #-----------------------------------------------------------------------
    # Properties
    #-----------------------------------------------------------------------

    @rmi_property
    def version(self):
        """
        The Enerplot application version. (Read-only)

        .. versionadded:: 2.2
        """

    @rmi_property
    def examples(self):
        """
        The Enerplot "Examples directory". (Read-only)

        .. versionadded:: 2.2
        """

    #-----------------------------------------------------------------------
    # Expand environment variables
    #-----------------------------------------------------------------------

    @rmi
    def _substitute(self, value):
        pass

    @requires('1.1')
    def substitute(self, value: str) -> str:
        """
        Substitute Enerplot workspace and environment variables in the given
        string.

        Returns:
            str: The string with known variables substituted.

        Example::

            >>> enerplot.substitute('Running Enerplot version $(Version)')
            'Running Enerplot version 1.1'

        .. versionadded:: 2.3
        """
        return self._substitute(value)


    #-----------------------------------------------------------------------
    # Status / Progress
    #-----------------------------------------------------------------------

    @rmi
    def status(self, message, window=0):
        """
        Display a message in a status bar message window

        Parameters:
            message (str): Message to display in status bar
            window (int): Status bar message window number (0, 1, or 2)
        """

    @rmi
    def _progress(self, guid, amount, total, status, priority, text):
        pass

    def progress(self, text="", total=100, status=0, priority=0):
        """
        Create and return a Progress Bar

        Parameters:
            text (str): Message to display in progress bar
            total (int): Maximum progress value (default: 100)
            status (int): 0 = running, 1 = waiting, 2 = stopped
            priority (int): priority for the progress bar display

        Returns:
            Progress: a progress bar
        """

        return self._progress(0, 0, total, status, priority, text)


    #-----------------------------------------------------------------------
    # Load files
    #-----------------------------------------------------------------------

    @staticmethod
    def _expandpaths(files, folder=None):
        if folder:
            folder = mhi.common.path.expand_path(folder, abspath=True)
            files = [os.path.join(folder, file) for file in files]

        return mhi.common.path.expand_paths(files, abspath=True)

    @rmi
    def _load_files(self, *files):
        pass


    #-----------------------------------------------------------------------
    # Workspace
    #-----------------------------------------------------------------------

    @rmi
    def _new_workspace(self):
        """Create a new workspace"""

    def new_workspace(self, default_book=True):
        """
        Create a new workspace

        The workspace will contain an 'Untitled' book, unless
        default_book is set to False.

        Parameters:
            default_book (bool): Create an 'Untitled' book in the new workspace
        """

        self._new_workspace()
        time.sleep(0.1)
        if not default_book:
            for _ in range(5):
                books = self.books()
                if len(books) == 1 and books[0].name in {"Untitled", "MyBook"}:
                    books[0].unload()
                    break
                else:
                    # May still be unloading previous workspace ...
                    # ... wait a bit & try again
                    time.sleep(0.1)


    def load_workspace(self, workspace, folder=None):
        """
        Load an existing Enerplot workspace

        Parameters:
            workspace (str): pathname to the workspace to load.  The extension
                .epwx is appended if not present.

            folder (str): If provided, the path to the workspace is resolved
                relative to this folder.
        """

        if isinstance(workspace, PurePath):
            workspace = str(workspace)

        if not workspace.endswith(".epwx"):
            workspace += '.epwx'

        workspace = mhi.common.path.expand_path(workspace, folder=folder,
                                                abspath=True)
        self._load_files(workspace)

    @rmi
    def _save_workspace(self, save_projects, path=None):
        pass

    def save_workspace(self, *, save_projects=True):
        """
        Save the current Enerplot workspace

        Parameters:
            save_projects (bool): Set to ``False`` if only the workspace
                should be saved, and not any unsaved projects.
        """

        return self._save_workspace(save_projects)

    def save_workspace_as(self, workspace, *, folder=None, save_projects=True):
        """
        Save the current Enerplot workspace

        Parameters:
            workspace (str): pathname to save the workspace as.  The extension
                .epwx is appended if not present.

            folder (str): If provided, the path to the workspace is resolved
                relative to this folder.

            save_projects (bool): Set to ``False`` if only the workspace
                should be saved, and not any unsaved projects.
        """

        if isinstance(workspace, PurePath):
            workspace = str(workspace)

        if not workspace.endswith('.epwx'):
            workspace += '.epwx'

        if folder:
            workspace = os.path.join(folder, workspace)

        workspace = mhi.common.path.expand_path(workspace, abspath=True)

        return self._save_workspace(save_projects, workspace)


    @property
    @requires('1.1')
    def workspace_dir(self) -> str:
        """
        Return the current workspace directory

        .. versionadded:: 2.3
        """
        return self.substitute('$(WorkspaceDir)')

    @property
    @requires('1.1')
    def workspace_name(self) -> str:
        """
        Return the current workspace name

        .. versionadded:: 2.3
        """
        return self.substitute('$(WorkspaceName)')

    @property
    @requires('1.1')
    def workspace_path(self) -> str:
        """
        Return the current workspace path

        .. versionadded:: 2.3
        """
        return self.substitute(r'$(WorkspaceDir)\$(WorkspaceName).epwx')

    @requires('1.1')
    @rmi
    def is_dirty(self) -> bool:
        """
        Determine whether the workspace has been modified since the last time
        it was saved.

        Returns:
            `True` if the workspace has unsaved changes, `False` otherwise.

        .. versionadded: 2.3
        """

    @requires('1.1')
    @rmi
    def reload(self) -> None:
        """
        Reload the workspace

        Discard all unsaved changes and reload the workspace.

        .. versionadded: 2.4
        """

    #-----------------------------------------------------------------------
    # Books
    #-----------------------------------------------------------------------

    @rmi
    def _books(self):
        """List currently loaded books"""

    def books(self):
        """
        Returns:
            IndexableDict[str,Book]: an indexable dictionary of all currently
            loaded books
        """

        books = self._books()
        return IndexableDict((book.name, book) for book in books)

    @rmi
    def book(self, name):
        """
        Retrieve a book reference, by name

        Parameters:
            name (str): The simple name of the book.  No punctuation characters.

        Returns:
            Book: the book proxy object
        """

    def load_books(self, *files, folder=None):
        """
        Load one or more books into the workspace.

        Arguments:
            *files (str): pathnames to one or more project book files.  A ``~``
                or ``~user`` prefix, as well as any ``$var``, ``${var}`` and
                ``%var%`` patterns in the pathnames are expanded, and the
                resulting pathnames are converted to absolute paths before
                being passed to the remote application.

            folder (str): If provided, the relative paths to the files are
                resolved relative to this folder.
        """

        if len(files) == 0:
            raise ValueError("No files given")

        files = self._expandpaths(files, folder)

        return self._load_files(*files)

    @rmi
    def _new_book(self, path):
        """Create a new book"""

    def new_book(self, path, folder=None):
        """
        Create a new book

        Parameters:
            path (str): location to store the book.
                The extension .epbx is appended if not present.

            folder (str): If provided, the path to the book is resolved
                relative to this folder.

        Returns:
            Book: the book proxy object
        """

        if isinstance(path, PurePath):
            path = str(path)

        if not path.endswith(".epbx"):
            path += '.epbx'

        if folder:
            path = os.path.join(folder, path)

        path = mhi.common.path.expand_path(path, abspath=True)

        name = os.path.splitext(os.path.basename(path))[0]
        try:
            book = self.book(name)
            raise ValueError("Book %r already exists" % name)
        except Exception:
            pass

        self._new_book(path)

        return self.book(name)


    #-----------------------------------------------------------------------
    # Data Files (aka Journals)
    #-----------------------------------------------------------------------

    _UNIQUE_EXT = {".inf", ".infx", ".csv", ".cfg", ".cff", ".asc", ".outx"}

    @rmi
    def _load_datafiles(self, files):
        """Load data files"""

    def load_datafiles(self, *files, folder=None, load_data=True, fmt=0):
        """
        Load data files

        Parameters:
            *files (str): One or more pathnames to datafiles.

            folder (str): If provided, the datafile paths are resolved
                relative to this folder.

            load_data (bool): Set to False to delay loading of the data until
                it is needed.

            fmt (int): If the extensions do not indicate a unique format,
                a format code is required.

        Returns:
            IndexableDict[str,DataFile]: An indexable dictionary of data files

        .. table:: "File Load Type" Format Codes

            ============================  ===================================
            Format Code                   Description
            ============================  ===================================
            DataFile.FLT_EMTDC            PSCAD/EMTDC
            DataFile.FLT_CSV              Comma Separated Files
            DataFile.FLT_CSV_UNFORMATTED  Comma Separated Files (Unformatted)
            DataFile.FLT_COMTRADE         COMTRADE Files
            DataFile.FLT_PSSE             PSS/E Files
            DataFile.FLT_HFS              Harmonic Frequency Scanner Files
            DataFile.FLT_RSCAD            RSCAD Files
            ============================  ===================================
        """

        if len(files) == 0:
            raise ValueError("No files given")

        files = self._expandpaths(files, folder)

        if fmt is None:
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in Enerplot._UNIQUE_EXT:
                    raise ValueError("Format required for %s files" % ext)

        for file in files:
            if not os.path.isfile(file):
                raise FileNotFoundError(file)

        if self.version == '1.0.0':
            self._load_datafiles(files, load_data, fmt)
        else:
            self._load_datafiles(files)

        return Datafiles(self._datafile(filename=file) for file in files)


    @rmi
    def _datafiles(self):
        """List currently loaded data files"""

    def datafiles(self):
        """
        List the currently loaded data files

        Returns:
            IndexableDict[str,DataFile]: an indexable dictionary of data files
        """

        return Datafiles(self._datafiles())

    @rmi
    def _datafile(self, id=0, name=None, filename=None):
        """Retrieve a data file reference, by id, name or filename"""

    def datafile(self, name):
        """
        Retrieve a data file reference, by name.

        Parameters:
            name (str): The name or label of the data file

        Returns:
            DataFile: the named data file
        """
        return self._datafile(name=name)

    @rmi
    def _new_datafile(self, path):
        pass

    def new_datafile(self, path="External_Data", folder=None, label=None):
        """
        Create a new ".mod.csv" datafile

        Parameters:
            path (str): The name and location to store the datafile.

            folder (str): If provided, the datafile is located relative to
                this folder.

            label (str): If provided, a label for the new datafile

        Returns:
            DataFile: the created data file
        """

        if isinstance(path, PurePath):
            path = str(path)

        if label:
            self.main.requires("1.0.1", "label parameter")
        elif self.main.minimum_version("1.0.1"):
            label = os.path.basename(path)
            if label.endswith(".mod.csv"):
                label = label[:-8]
            print(label)
        else:
            print("No label: ver =", self.main._version)

        if not path.endswith(".mod.csv"):
            path += '.mod.csv'

        if folder:
            path = os.path.join(folder, path)

        path = mhi.common.path.expand_path(path, abspath=True)

        df = self._new_datafile(path)

        if label:
            print("Setting label")
            df.label = label

        return df


    #-----------------------------------------------------------------------
    # Print
    #-----------------------------------------------------------------------

    @rmi
    def _print(self):
        pass

    @requires('1.1')
    def print(self):
        """
        Print the currently selected book

        .. versionadded:: 2.5
        """
        self._print()
