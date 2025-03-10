import csv 
import pandas as pd
import csv_schema as schema
import person as Person

default_file_path = 'data/users.csv'

def read_csv(file_path) -> None:
    print(type(file_path))
    if file_path == None:
        file_path = default_file_path

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if "Yes," in "Y":
                print(row[2] + " " + row[3] + ", " + row[7])

def read_csv_pd(file_path) -> dict[str, Person.Person]:
    if file_path == None:
        file_path = default_file_path

    df = pd.read_csv(file_path)
    # Filter the "First Name" column where the name contains "nd" (case-insensitive)
    #filtered_names = df[df[schema.columns["q1"]].str.contains("Yes", case=False, na=False)]
    filtered_names = df
    
    result = filtered_names[["First name", "Last name"]]
    #Print each matching name
    i = 0
    for name in result.iterrows():
        i += 1
        if i > 10:
            break
        n = name
        print(n[1][0] + " " + n[1][1])

    p1 = Person.Person(1, "John", "Doe")
    return {"id": p1}
