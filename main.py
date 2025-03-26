import csv_reader as cr
import formation as fm
import argparse

# Reading arguments
def args_parser():
    parser = argparse.ArgumentParser() 
    
    parser.add_argument("-i","--input", help="File input to read", type=str)
     
    args = parser.parse_args()
    if args.input:
        print("File input: ",args.input)
    else:
        print("Please speicify a file input with -i or --input")
    return args.input
    
    

def main():
    path = args_parser()
    dict_uuid_person = cr.read_csv_pd(path)
    fm.form_teams(dict_uuid_person) 


if __name__ == "__main__":
    main()
