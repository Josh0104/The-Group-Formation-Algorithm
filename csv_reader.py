import pandas as pd
# Hello
import csv_schema as schema
import person as Person

default_file_path = 'data/users.csv'
dictPersons = {}

def read_csv_pd(file_path) -> dict[str, Person.Person]:
    # if file_path == None:
    #     file_path = default_file_path
    
    df = pd.read_csv(file_path)

    
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


    for i, row  in result.iterrows():

        uuid = row.iloc[0]
        first_name = row.iloc[1]
        last_name = row.iloc[2]
        birthday = row.iloc[3]
        gender = row.iloc[4]
        country = row.iloc[5]
        a1 = row.iloc[6]
        a2 = row.iloc[7]
        a3 = row.iloc[8]
        a4 = row.iloc[9]
        a5 = row.iloc[10]
        a6 = row.iloc[11]
        a7 = row.iloc[12]
        a8 = row.iloc[13]
        a9 = row.iloc[14] if str(row.iloc[14]) != "nan" else ""
        a10 = row.iloc[15] if str(row.iloc[15]) != "nan" else ""

        dictPersons[row.iloc[0]] = Person.Person(
        i, uuid, first_name, last_name, birthday, gender, country, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10)
        
        # Sort by first_name attribute of each Person object
    sorted_dict = dict(sorted(dictPersons.items(), key=lambda item: item[1].first_name.lower()))
    return sorted_dict

def read_relations_csv_pd(file_path) -> dict[str, Person.Relation]:
    if file_path == None:
        file_path = "data/relations1.csv"
    
    df = pd.read_csv(file_path)

    result = df[[
        schema.columns_relations["uuid_1"], # 0
        schema.columns_relations["name_1"], # 1
        schema.columns_relations["name_2"], # 2
        schema.columns_relations["uuid_2"], # 3
        schema.columns_relations["relation"], # 4
        schema.columns_relations["weight"], # 5
        schema.columns_relations["description"] # 6
        ]]

    dictRelations = {}
    for i, row  in result.iterrows():
        uuid_1 = row.iloc[0]
        name_1 = row.iloc[1]
        name_2 = row.iloc[2]
        uuid_2 = row.iloc[3]
        relation = row.iloc[4]
        weight = row.iloc[5]
        description = row.iloc[6]

        dictRelations[row.iloc[0]] = Person.Relation(
            i, uuid_1, name_1, name_2, uuid_2, relation, weight, description)

    return dictRelations