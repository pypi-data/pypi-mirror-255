class AsciiColReader(FileFormat, SpectralFileFormat):
    """ Reader for files with multiple columns of numbers. The first column
    contains the wavelengths, the others contain the spectra. """
    EXTENSIONS = ('.dat', '.dpt', '.xy', '.csv')
    DESCRIPTION = 'Spectra ASCII'

    PRIORITY = CSVReader.PRIORITY + 1

    def read_spectra(self):
        tbl = None
        delimiters = [None, ";", ":", ","]
        for d in delimiters:
            try:
                comments = [a for a in [";", "#"] if a != d]
                tbl = np.loadtxt(self.filename, ndmin=2, delimiter=d, comments=comments)
                break
            except ValueError:
                pass
        if tbl is None:
            raise ValueError('File should be delimited by <whitespace>, ";", ":", or ",".')
        wavenumbers = tbl.T[0]  # first column is attribute name
        datavals = tbl.T[1:]
        return wavenumbers, datavals, None

    @staticmethod
    def write_file(filename, data):
        xs = getx(data)
        xs = xs.reshape((-1, 1))
        table = np.hstack((xs, data.X.T))
        np.savetxt(filename, table, delimiter="\t", fmt="%g")