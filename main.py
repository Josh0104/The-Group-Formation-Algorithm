import csv_reader as cr

def main():

    dict_uuid_person = cr.read_csv_pd("data/users.csv")
    user = dict_uuid_person.get('565467ff-e888-4e40-a9f5-f9fdbf0fd704')
    print(user)

if __name__ == "__main__":
    main()
