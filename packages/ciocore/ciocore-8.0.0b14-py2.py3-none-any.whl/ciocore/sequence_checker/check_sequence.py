import glob
from cioseq.sequence import Sequence
from ciocore.sequence_checker.bar_chart import BarChart
import os
import logging
import re

LOG_FORMATTER = logging.Formatter(
    "%(asctime)s  %(name)s%(levelname)9s %(filename)s-%(lineno)d %(threadName)s:  %(message)s"
)
STATUS_ENDPOINT = "/downloads/status"
FORMAT_SUMMARY = "summary"
FORMAT_ASCII_CHART = "ascii"
FORMAT_BAR_CHART = "bar"
FORMAT_OPTIONS = [FORMAT_SUMMARY, FORMAT_ASCII_CHART, FORMAT_BAR_CHART]
PATTERN_REGEX = re.compile(r"^(?P<prefix>[^\[\]]+)(?:\[(?P<spec>(?P<frame_spec>[0-9x\-,]+)(?P<hashes>#+))?\])?(?P<extension>[^\[\]]*)$")
BYTES_TO_MB = 1.0 / (1024 * 1024)
 
logger = logging.getLogger("conductor.check_sequence")


def run(pattern, format=FORMAT_OPTIONS[0], width=80):
    """
    Runs the check_sequence.py script to analyze and report sequence statistics.

    Args:
        pattern (str): The pattern of the expected file names.
      
        format (str, optional): The output format option. Defaults to "summary".
        width (int, optional): The width of the ASCII chart output. Defaults to 80.

    Raises:
        ValueError: If the provided expected value is invalid.

    Returns:
        None
    """

    logger.debug("Running check_sequence.py")

    match = PATTERN_REGEX.match(pattern)
    if not match:
        raise ValueError(
            f"Invalid pattern: '{pattern}'. Should be prefix[frame-spec][extension]. e.g. 'myfile[1-100####].png'"
        )

    prefix = match.group("prefix")
    extension = match.group("extension")
    if match.group("spec"):
        frame_spec = match.group("frame_spec")
        padding = len(match.group("hashes"))
        sequence = Sequence.create(frame_spec)
    else:
        sequence, padding = _infer_expected(prefix, extension)

    stats = _get_stats(prefix, extension, padding, sequence)

    logger.debug(f"Padding: {padding}")
    logger.debug(f"Sequence: {sequence}")
    logger.debug(f"Min Size: {stats['min_size']}")
    logger.debug(f"Max Size: {stats['max_size']}")

    exists_sequence, bad_sequence = _get_sequences(
        stats["files"]
    )

    expected_sequence_report = f"Expected: {sequence} ({len(sequence)} frames)"

    if exists_sequence:
        exists_sequence_report = (
            f"Exists: {exists_sequence} ({len(exists_sequence)} frames)"
        )
    else:
        exists_sequence_report = "Exists: None"

    if bad_sequence:
        bad_sequence_report = (
            f"Missing or Zero: {bad_sequence} ({len(bad_sequence)} frames)"
        )
    else:
        bad_sequence_report = "Missing or Zero: None"

    if format == FORMAT_ASCII_CHART:
        _make_ascii_chart(stats, width)
    elif format == FORMAT_BAR_CHART:
        _make_bar_chart(stats)

    print(expected_sequence_report)
    print(exists_sequence_report)
    print(bad_sequence_report)
    print("Min Size: {}".format(stats["min_size"]))
    print("Max Size: {}".format(stats["max_size"]))
    print("Padding: {}".format(padding))


def _get_stats(prefix, extension, padding, sequence):
    result = {
        "files": [],
        "max_size": 0,
        "min_size": 1024**4,
        "padding": padding,
        "prefix": prefix,
        "extension": extension,
        "sequence": str(sequence),
        "descriptor": f"{prefix}[{sequence}{'#'*padding}]{extension}",
    }
    for frame in sequence:
        file_path = f"{prefix}{frame:0{padding}}{extension}"
        size = 0
        exists = False
        try:
            stat = os.stat(file_path)
            exists = True
            size = stat.st_size
            if size > result["max_size"]:
                result["max_size"] = size
            if size < result["min_size"]:
                result["min_size"] = size
        except FileNotFoundError:
            pass
        result["files"].append(
            {
                "filepath": file_path,
                "frame": frame,
                "size": size,
                "exists": exists,
                "corrupt": False,
                "human_size": _human_file_size(size),
            }
        )
    return result


def _get_sequences(files):
    exist_frames = []
    bad_frames = []
    
    for file in files:
        if file["exists"]:
            exist_frames.append(file["frame"])

        if file["size"]  == 0:
            bad_frames.append(file["frame"])

    exist_sequence = Sequence.create(exist_frames) if exist_frames else None
    bad_sequence = Sequence.create(bad_frames) if bad_frames else None
    return exist_sequence, bad_sequence


def _infer_expected(prefix, extension):
    SEQUENCE_REGEX_PATTERN = re.compile(
        r"{}(\d+){}".format(re.escape(prefix), re.escape(extension))
    )
    SEQUENCE_GLOB_PATTERN = "{}*{}".format(prefix, extension)

    frames = []
    files = glob.glob(SEQUENCE_GLOB_PATTERN)
    # print("files", files)

    padding = 999
    start = 9999999999
    end = -start
    if not files:
        return None, 1
    for file in files:
        match = SEQUENCE_REGEX_PATTERN.match(file)
        # print("match",  match.group(1))
        if not match:
            # It should always match, but just in case
            continue
        digits = match.group(1)
        frame_number = int(digits)
        if frame_number < start:
            start = frame_number
        if frame_number > end:
            end = frame_number

        frame_number_length = len(digits)
        if padding > 1 and frame_number_length < padding:
            padding = frame_number_length

    return Sequence.create(f"{start}-{end}"), padding


def _make_ascii_chart(stats, width):
    mult = width / stats["max_size"]
    padding = stats["padding"]

    for file in stats["files"]:
        exists = file["exists"]
        nbytes = file["size"]
        size = file["human_size"]
        frame = file["frame"]

        fstr = f"{frame:0{padding}}"
        fstr = fstr.rjust(6)

        if exists:
            print("{}: {}| {}".format(fstr, "-" * int(nbytes * mult), size))
        else:
            print("{}: {}".format(fstr, "MISSING"))


def _make_bar_chart(stats):
    chart = BarChart()
    chart.update(stats)
    chart.show()

def _human_file_size(bytes):
    """
    Convert file size in bytes to human-readable format.

    Args:
        bytes (int): File size in bytes.

    Returns:
        str: Human-readable file size.

    """

    # Define the suffixes for different file sizes
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]

    # Get the closest matching suffix and the corresponding divisor
    for suffix in suffixes:
        if bytes < 1024:
            return f"{bytes:.2f} {suffix}"
        bytes /= 1024

    return f"{bytes:.2f} {suffixes[-1]}"
