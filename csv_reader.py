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
    
    result = df[[
        schema.columns["uuid"], # 0
        schema.columns["first_name"], # 1
        schema.columns["last_name"], # 2
        schema.columns["birthday"], # 3
        schema.columns["gender"], # 4
        schema.columns["country"], # 5
        schema.columns["q1"], # 6
        schema.columns["q2"], # 7
        schema.columns["q3"], # 8
        schema.columns["q4"], # 9
        schema.columns["q5"], # 10
        schema.columns["q6"], # 11
        schema.columns["q7"], # 12
        schema.columns["q8"], # 13
        schema.columns["q9"], # 14
        schema.columns["q10"], # 15
        ]]
    #Print each matching name
    i = 0
    for _, row  in result.iterrows():
        i += 1
        if i > 10:
            break
        print("n[0] "+row.iloc[0])
        print("n[1] "+row.iloc[1])
        print("n[2] " +row.iloc[2])

    p1 = Person.Person(1, "1234","John", "Doe", "01/01/2000", "M", "USA", "Yes", "No", "Yes", "No", "Yes", "No", "Yes", "No", "Yes")
    return {"id": p1}
