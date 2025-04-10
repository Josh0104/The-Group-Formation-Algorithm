import os
import csv_reader as cr
import formation as fm
import argparse
import gui

# Reading arguments
def args_parser():
    parser = argparse.ArgumentParser() 
    
    parser.add_argument("-i","--input", help="File input to read", type=str)
    parser.add_argument("-g", "--group", help="Number of groups", type=int)
    parser.add_argument("-p", "--print", help="Print the output", action="store_true")
    parser.add_argument("-o", "--output", help="path for output file, default is ./output", type=str)
    parser.add_argument("-n","--no-output", help="Do not generate an output file", action="store_true")  
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("--no-gui", help="Do not run the GUI", action="store_true")
    
    args = parser.parse_args()
    file_path = args.input
    number_of_groups = args.group
    print_output = args.print
    output_file = args.output
    no_output = args.no_output
    verbose = args.verbose
    no_gui = args.no_gui
    
    # If user does not specify a file input
    if file_path == None:
        raise TypeError(
            f'Please specify a file input with -i or --input\n'
            f'Example usage: python3 main.py -i <path/to/file>'
            )
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f'Error: File "{file_path}" not found.\n'
            f'- Make sure the file is in the correct directory.\n'
            f'- If the file name has changed, update the path accordingly.'
        ) 
    
    if number_of_groups == None:
        number_of_groups = 5
        print(f'Number of groups not specified. Defaulting to 5 groups.')

    return file_path, number_of_groups, print_output, output_file, no_output, verbose,no_gui
    

def main():

    try:     
        path, number_of_groups, is_printing_output, args_output_file, args_no_output, args_verbose, args_no_gui = args_parser()
        dict_uuid_person = cr.read_csv_pd(path)
        
        if args_no_gui:
            fm.form_teams(dict_uuid_person, number_of_groups, is_printing_output, args_output_file, args_no_output, args_verbose) 
        else:
            gui.run_view(dict_uuid_person, number_of_groups, is_printing_output, args_output_file, args_no_output, args_verbose)

    except FileNotFoundError as fnfe:
        print(fnfe) # Print the error message
        exit(1)
    except TypeError as te:
        print(te) # Print the error message
        exit(1)

if __name__ in {"__main__", "__mp_main__"}:
    main()