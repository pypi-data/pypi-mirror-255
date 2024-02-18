import Oasys.gRPC


# Metaclass for static properties and constants
class UtilsType(type):

    def __getattr__(cls, name):

        raise AttributeError


class Utils(Oasys.gRPC.OasysItem, metaclass=UtilsType):


    def __del__(self):
        if not Oasys.REPORTER._connection:
            return

        Oasys.REPORTER._connection.destructor(self.__class__.__name__, self._handle)


    def __getattr__(self, name):
        raise AttributeError


    def __setattr__(self, name, value):
# Set the property locally
        self.__dict__[name] = value


# Static methods
    def Build():
        """
        Returns the build number

        Returns
        -------
        int
            integer
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "Build")

    def CallPromiseHandlers():
        """
        Manually call any promise handlers/callbacks in the job queue

        Returns
        -------
        None
            no return value
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "CallPromiseHandlers")

    def CheckinLicense(feature):
        """
        Checks a license for a feature back in

        Parameters
        ----------
        feature : string
            feature to check license back in for

        Returns
        -------
        None
            no return value
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "CheckinLicense", feature)

    def CheckoutLicense(feature):
        """
        Checks out a license for a feature

        Parameters
        ----------
        feature : string
            feature to check license for

        Returns
        -------
        bool
            True if license available, False if not
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "CheckoutLicense", feature)

    def GarbageCollect():
        """
        Forces garbage collection to be done. This should not normally need to be called
        but in exceptional circumstances it can be called to ensure that garbage collection is done to
        return memory

        Returns
        -------
        None
            no return value
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "GarbageCollect")

    def GetLSDYNAVersions():
        """
        Returns a list of all LS-DYNA output version names available in PRIMER

        Returns
        -------
        list
            A list of LS-DYNA version names
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "GetLSDYNAVersions")

    def HTMLBrowser():
        """
        Returns the path to the default HTML browser

        Returns
        -------
        str
            string of the path
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "HTMLBrowser")

    def HiResTimer():
        """
        A high resolution timer that can be used to time how long things take.
        The first time this is called the timer will start and return 0. Subsequent calls will return
        the time in nanoseconds since the first call. Note that the timer will almost certainly not have
        1 nanosecond precision but, depending on the platform, should should have a resolution of at least 1 microsecond.
        The resolution can be found by using Utils.TimerResolution()

        Returns
        -------
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "HiResTimer")

    def PdfReader():
        """
        Returns the path to the executable of the default pdf reader

        Returns
        -------
        str
            string of the path
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "PdfReader")

    def TimerResolution():
        """
        Returns the resolution (precision) of the Utils.HiResTimer() timer in nanoseconds

        Returns
        -------
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "TimerResolution")

    def Version():
        """
        Returns the version number

        Returns
        -------
        float
            real
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "Version")

