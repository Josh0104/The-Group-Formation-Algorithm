import csv_reader as cr
#import csv_schema as cs

def main():
    print("hello world")

    result = cr.read_csv_pd("data/users.csv")
    # print(result)
    #print(cs.columns["first_name"])

if __name__ == "__main__":
    main()

