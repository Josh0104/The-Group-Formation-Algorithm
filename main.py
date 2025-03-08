import csv_reader as cr
#import csv_schema as cs

def main():
    print("hello world")
    cr.read_csv("data/users.csv")
    cr.read_csv(None)

    cr.read_csv_pd("data/users.csv")
    #print(cs.columns["first_name"])

if __name__ == "__main__":
    main()

