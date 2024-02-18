import argparse
import os

from .captions import Captions
from .microTime import MicroTime as MT
from .styling import changeStyleOption
from .options import save_extensions, style_options
from pycaptions import supported_extensions


def main():
    time_formats_help = {
        "time": "u (microseconds)",
        "microtime": "'h m s S u' (doesn't need all the values)",
        "vtt": "hh:mm:ss.SSS (e.g 00:00:04.000)",
        "srt": "hh:mm:ss,SSS (e.g 00:00:04,000)",
        "ttml": "same as vtt + extra, search online\nextra params: multiplier frameRate subFrameRate",
        "sub": "{start_frame}{end_frame} frame_rate\n(e.g {0}{25} 25)"
    }

    extensions = '\n'.join(f" - '{i.lstrip('.')}'" for i in supported_extensions)
    default_time_format = "vtt"
    time_formats = '\n'.join(f" - '{i}': {v}" for i, v in time_formats_help.items() if i != default_time_format)

    parser = argparse.ArgumentParser(prog='PyCaptions', description='Captions converter', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("filenames", nargs="+", help="List of input filenames.")
    parser.add_argument("-f", "--format", nargs="+", default="all", help=f"Specify output format(s).\nOptions:\n - 'all' (default): exports to all formats specified in FileExtensions\n{extensions}")
    parser.add_argument("-j", "--join", nargs="+", default="end_time", help="Specify join criteria.\nOptions:\n - 'end_time' (default): Adds next file to the end of previous\n - 'add': Adds new language to existing file\n - 'offset [TIME_FORMAT_FORMAT ...]': Specify length of each file")
    parser.add_argument("-tf", "--time-format", nargs="+", default=default_time_format, help=f"Specify time format.\nOptions:\n - '{default_time_format}' (default): {time_formats_help[default_time_format]}\n{time_formats}")
    parser.add_argument("-l", "--languages", nargs="+", help="List of languages. For more than one language in the\nsame file it's recomended to set '-li 1' for better visibility.")
    parser.add_argument("-o", "--output-filenames", nargs="+", help="List of output filenames.")
    parser.add_argument("-od", "--output-directory", help="Output directory path.\nCreates new directory in current working\ndirectory if it doesn't exist.")
    parser.add_argument("-li", "--lines", type=int, help="Number of lines per language.\nOptions:\n - '-1': preservs original\n - '0': auto format \n - n: positive integer")
    parser.add_argument("-s", "--style", help="Either 'full' (default) or 'none'", default="full")
    args = parser.parse_args()

    style_options.style = args.style
    if args.lines:
        style_options.lines = args.lines

    formats = None
    languages = None

    if args.output_directory and not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    if args.output_filenames:
        if args.output_directory:
            out_filenames = [os.path.join(args.output_directory, i) for i in args.out_filenames]
        else:
            out_filenames = args.out_filenames
        if args.format == "all":
            formats = []
            for i in args.filenames:
                _, ext = os.path.splitext(i)[0]
                if ext not in supported_extensions:
                    print(f"Incorect file format {ext} for {i}")
                    print(f"Supported extensions {supported_extensions}")
                    return -1
                formats.append(ext)

        languages = [Captions.getLanguagesFromFilename(i) or args.languages
                     for i in args.out_filenames]

    else:
        out_filenames = [Captions.getFilename(i, args.output_directory) for i in args.filenames]

    if not formats:
        if args.format == "all":
            formats = [supported_extensions for _ in args.filenames]
        else:
            formats = [args.format for _ in args.filenames]

    if not languages:
        languages = [args.languages for _ in args.filenames]

    if not args.join:
        for _in, _out, _lang, _format in zip(args.filenames, out_filenames, languages, formats):
            with Captions(_in) as c:
                for out_format in _format:
                    c.save(_out, _lang, out_format)
    elif args.join == "end_time":
        with Captions(args.filenames[0]) as c:
            for next_file in args.filenames[1:]:
                c.join(Captions(next_file), True)
            for out_format in formats[0]:
                c.save(out_filenames[0], languages[0], out_format)
    elif args.join == "add":
        with Captions(args.filenames[0]) as c:
            for next_file in args.filenames[1:]:
                c += Captions(next_file)
            for out_format in formats[0]:
                c.save(out_filenames[0], languages[0], out_format)
    elif args.join == "offset":
        with Captions(args.filenames[0]) as c:
            time_offset = MT()
            for next_file, offset in zip(args.filenames[1:], args.join[1:]):
                time_offset += MT.fromAnyFormat(args.time_format, *offset)
                c.join(Captions(next_file), False, time_offset)
            for out_format in formats[0]:
                c.save(out_filenames[0], languages[0], out_format)


if __name__ == "__main__":
    main()
