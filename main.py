import os
import argparse
import csv_reader as cr
import formation as fm
import gui.main_view as gui
import app_config

def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="File input to read", type=str)
    parser.add_argument("-g", "--group", help="Number of groups", type=int)
    parser.add_argument("-p", "--print", help="Print the output", action="store_true")
    parser.add_argument("-o", "--output", help="Path for output file, default is ./output", type=str)
    parser.add_argument("-n", "--no-output", help="Do not generate an output file", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("--no-gui", help="Do not run the GUI", action="store_true")

    args = parser.parse_args()
    app_config.args = args 

    # Validation
    if args.input is None:
        args.input = "data/people/people.csv"
        # raise TypeError(
        #     '❌ Please specify a file input with -i or --input\n'
        #     'Example usage: python3 main.py -i <path/to/file>'
        # )

    if not os.path.exists(args.input):
        raise FileNotFoundError(
            f'❌ File "{args.input}" not found.\n'
            f'- Make sure the file is in the correct directory.\n'
            f'- If the file name has changed, update the path accordingly.'
        )

    if args.group is None:
        args.group = 5
        if args.verbose:
            print("⚠️  Number of groups not specified. Defaulting to 5 groups.")

    return args


def run_formation(relations_data):
    from app_config import args  # access shared args
    print("relations_data", relations_data)
    try:
        dict_uuid_person = cr.read_csv_pd(args.input)
    except FileNotFoundError as fnfe:
        print(fnfe)
        exit(1)
    except TypeError as te:
        print(te)
        exit(1)

    return fm.form_teams(
        dict_uuid_person,
        args.group,
        args.print,
        args.output,
        args.no_output,
        args.verbose,
        relations_data
    )


def main():
    args = args_parser()

    if args.no_gui:
        run_formation([])
    else:
        gui.run_gui()


if __name__ in {"__main__", "__mp_main__"}:
    main()