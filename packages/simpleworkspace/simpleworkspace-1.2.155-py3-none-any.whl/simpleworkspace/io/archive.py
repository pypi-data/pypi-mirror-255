import os as _os

class GZIP:
    @staticmethod
    def Compress(inputPath:str, outputPath:str=None):
        """Compresses one file to a GZIP archive

        :param inputPath: filepath to compress
        :param outputPath: desired full output path, by default adds format suffix to inputpath
        :return: the path to the compressed archive
        """
        import gzip
        if(outputPath is None):
            outputPath = inputPath + '.gz'
        with open(inputPath, mode='rb') as f_in:
            with gzip.open(outputPath, mode='wb') as f_out:
                f_out.writelines(f_in)
        return outputPath

    @staticmethod
    def Extract(inputPath:str, outputPath:str=None):
        """Extracts one file to a GZIP archive

        :param inputPath: filepath to extract
        :param outputPath: desired full output path, by default removes format suffix from inputpath
        :return: the path to the extracted content
        """
        import gzip
        if(outputPath is None):
            outputPath = inputPath.removesuffix('.gz')
        with gzip.open(inputPath, mode='rb') as f_in:
            with open(outputPath, mode='wb') as f_out:
                f_out.writelines(f_in)
        return outputPath

class TAR_GZIP:
    @staticmethod
    def Compress(inputPath:str, outputPath:str=None, ignoreErrors=False):
        """Compresses file or folder to Tar+GZIP archive

        :param inputPath: file or folder path to compress
        :param outputPath: desired full output path, by default adds format suffix to inputpath
        :param ignoreErrors: continue compressing next entry when encountering errors
        :return: the path to the compressed archive
        """
        import tarfile
        if outputPath is None:
            outputPath = inputPath + '.tar.gz'
        with tarfile.open(outputPath, mode='w:gz') as tar:
            try:
                if _os.path.isfile(inputPath):
                    tar.add(
                        inputPath,
                        arcname=_os.path.basename(inputPath)
                    )
                elif _os.path.isdir(inputPath):
                    for root, dirs, files in _os.walk(inputPath):
                        for file in files:
                            currentFilePath = _os.path.join(root, file)
                            tar.add(
                                currentFilePath,
                                arcname=_os.path.relpath(currentFilePath, inputPath)
                            )
            except Exception as ex:
                if not ignoreErrors:
                    raise ex
        return outputPath

    @staticmethod
    def Extract(inputPath:str, outputPath:str=None):
        """Extracts Tar+GZIP archive

        :param inputPath: filepath to extract
        :param outputPath: desired full output path, by default removes format suffix from inputpath
        :return: the path to the extracted content
        """
        import tarfile
        if outputPath is None:
            oldLen = len(outputPath)
            outputPath = inputPath.removesuffix('.tar.gz')
            if(oldLen == len(outputPath)): #try this one aswell
                outputPath = inputPath.removesuffix('.tgz')

        with tarfile.open(inputPath, mode='r:gz') as tar:
            tar.extractall(outputPath)
        return outputPath

class ZIP:
    @staticmethod
    def Compress(inputPath:str, outputPath:str=None, compressionLevel:int=None, ignoreErrors=False):
        """Compresses file or folder to zip archive

        :param inputPath: file or folder path to compress
        :param outputPath: desired full output path, by default adds format suffix to inputpath
        :param compressionLevel: 0-9, where 0 uses no compression(only stores files), and 9 has max compression. \
                                 When None is supplied use default in zlib(usually 6)
        :param ignoreErrors: continue compressing next entry when encountering errors
        :return: the path to the compressed archive
        """
        import zipfile
        if(outputPath is None):
            outputPath = inputPath + '.zip'
        compressionType = zipfile.ZIP_DEFLATED
        if(compressionLevel is not None) and (compressionLevel < 1):
            compressionType = zipfile.ZIP_STORED #use no compression
            compressionLevel = None
        with zipfile.ZipFile(outputPath, mode='w', compression=compressionType, compresslevel=compressionLevel) as zipf:
            try:
                if _os.path.isfile(inputPath):
                    zipf.write(
                        inputPath,
                        arcname=_os.path.basename(inputPath)
                    )
                elif _os.path.isdir(inputPath):
                    for root, dirs, files in _os.walk(inputPath):
                        for file in files:
                            currentFilePath = _os.path.join(root, file)
                            zipf.write(
                                currentFilePath,
                                arcname=_os.path.relpath(currentFilePath, inputPath)
                            )
            except Exception as ex:
                if not ignoreErrors:
                    raise ex
        return outputPath

    @staticmethod
    def Extract(inputPath:str, outputPath:str=None):
        """Extracts ZIP archive

        :param inputPath: filepath to extract
        :param outputPath: desired full output path, by default removes format suffix from inputpath
        :return: the path to the extracted content
        """
        import zipfile
        if(outputPath is None):
            outputPath = inputPath.removesuffix('.zip')
        with zipfile.ZipFile(inputPath, mode='r') as zipf:
            zipf.extractall(outputPath)
        return outputPath