from typing import Iterator as _Iterator
import os as _os

class RotatingLogReader():
    def __init__(self, logPath: str):
        """
        :param logPath: the full path to a live log, such as /var/log/apache/access.log,
            The parser handles already rotated files behind the scenes
        """

        from simpleworkspace.io.path import PathInfo
        self.logPath = PathInfo(logPath)

    def __str__(self):
        """
        :returns: All logs dumped to a string
        """
        from io import StringIO

        strBuilder = StringIO()
        for line in self.ReadLines():
            strBuilder.write(line)
        return strBuilder.getvalue()

    def ExportToFile(self, outputPath):
        """
        Dumps all logs as one file
        """

        with open(outputPath, "w") as fp:
            for line in self.ReadLines():
                fp.write(line)
        return

    def GetRelatedLogFilePaths(self) -> list[str]:
        """
        :returns: list of paths to the log itself + all of its rotated files, sorted newest to oldest logs example [log.txt, log.txt.1, log.txt.2.gz]
        """
        import re
        import simpleworkspace.io.directory
        import simpleworkspace.utility.regex

        logFiles = {}
        def logFilesFiltering(path: str):
            currentLogname = _os.path.basename(path)
            if(self.logPath.Head not in currentLogname):
                return
            if(self.logPath.Head == currentLogname):
                logFiles[0] = path
                return
            escLogName = re.escape(self.logPath.Head)
            match = simpleworkspace.utility.regex.Match(f"/^{escLogName}\.(\d+)/", currentLogname)[0]
            logFiles[int(match[1])] = path
            return
        for filepath in simpleworkspace.io.directory.Scan(self.logPath.Tail, includeDirs=False, maxDepth=1):
            logFilesFiltering(filepath)
        

        sortedLogFiles = []
        sortedKeyList = sorted(logFiles.keys())
        for i in sortedKeyList:
            sortedLogFiles.append(logFiles[i])

        return sortedLogFiles

    def ReadLines(self) -> _Iterator[str]:
        """
        iterates loglines
        """
        import gzip

        oldestToNewestLogs = self.GetRelatedLogFilePaths()
        oldestToNewestLogs.reverse()

        for logPath in oldestToNewestLogs:
            fp = None
            if logPath.endswith(".gz"):
                fp = gzip.open(logPath, "rt")
            else:
                fp = open(logPath, "r")
            with fp:
                for line in fp:
                    yield line
        return
    

    
