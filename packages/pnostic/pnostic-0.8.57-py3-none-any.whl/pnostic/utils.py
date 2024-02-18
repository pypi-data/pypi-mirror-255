import datetime, os,sys


def fancy_date(date: datetime.datetime) -> str:
    return date.strftime("%a %b %d %H:%M:%S %Z %Y")

def now() -> datetime.datetime:
    current:datetime.datetime = datetime.datetime.now(datetime.datetime.utc)
    current.str = lambda:fancy_date(current)
    return current

class bcolors:
    #https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def custom_msg(msg, color:bcolors):
    return "{0}{1}{2}".format(
        color, msg, bcolors.ENDC
    )

def convert_size_to_bytes(size_str):
    try:
        #https://stackoverflow.com/questions/44307480/convert-size-notation-with-units-100kb-32mb-to-number-of-bytes-in-python
        """Convert human filesizes to bytes.

        Special cases:
        - singular units, e.g., "1 byte"
        - byte vs b
        - yottabytes, zetabytes, etc.
        - with & without spaces between & around units.
        - floats ("5.2 mb")

        To reverse this, see hurry.filesize or the Django filesizeformat template
        filter.

        :param size_str: A human-readable string representing a file size, e.g.,
        "22 megabytes".
        :return: The number of bytes represented by the string.
        """
        multipliers = {
            'kilobyte':  1024,
            'megabyte':  1024 ** 2,
            'gigabyte':  1024 ** 3,
            'terabyte':  1024 ** 4,
            'petabyte':  1024 ** 5,
            'exabyte':   1024 ** 6,
            'zetabyte':  1024 ** 7,
            'yottabyte': 1024 ** 8,
            'kb': 1024,
            'mb': 1024**2,
            'gb': 1024**3,
            'tb': 1024**4,
            'pb': 1024**5,
            'eb': 1024**6,
            'zb': 1024**7,
            'yb': 1024**8,
        }

        for suffix in multipliers:
            size_str = size_str.lower().strip().strip('s')
            if size_str.lower().endswith(suffix):
                return int(float(size_str[0:-len(suffix)]) * multipliers[suffix])
        else:
            if size_str.endswith('b'):
                size_str = size_str[0:-1]
            elif size_str.endswith('byte'):
                size_str = size_str[0:-4]
        return int(size_str)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        msg = ":> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno)
        print(msg)
        return float("inf")

class clean_op_env(object):
    def __init__(self):
        pass

    @staticmethod
    def clean_operators():
        import shutil
        for x in ["runners","loggers","providers","envelopers","seclusion"]:
            try:
                shutil.rmtree("{0}/".format(x))
            except:
                pass

    def __enter__(self):
        clean_op_env.clean_operators()
        return self

    def __exit__(self,a=None,b=None,c=None):
        clean_op_env.clean_operators()