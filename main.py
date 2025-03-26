import os
import csv_reader as cr
import formation as fm
import argparse

# Reading arguments
def args_parser():
    parser = argparse.ArgumentParser() 
    
    parser.add_argument("-i","--input", help="File input to read", type=str)
     
    args = parser.parse_args()
    file_path = args.input
    
    if file_path == False:
        print("Please speicify a file input with -i or --input")
        exit(1)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f'Error: File "{file_path}" not found.\n'
            f'- Make sure the file is in the correct directory.\n'
            f'- If the file name has changed, update the path accordingly.'
        ) 

    return file_path
    
    

def main():

    try:     
        path = args_parser()
        dict_uuid_person = cr.read_csv_pd(path)
        fm.form_teams(dict_uuid_person) 
    except FileNotFoundError as fnfe:
        print(fnfe) # Print the error message
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
