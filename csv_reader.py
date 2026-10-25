import pandas as pd
# Hello
import csv_schema as schema
import person as Person
import app_config


dictPersons = {}

def read_csv_pd(file_path) -> dict[str, Person.Person]:
    global dictPersons
    df = pd.read_csv(file_path)

    size_column = schema.columns.get("size")
    has_size = size_column in df.columns if size_column else False

    selected_columns = [
        schema.columns["uuid"],        # 0
        schema.columns["first_name"],  # 1
        schema.columns["last_name"],   # 2
        schema.columns["birthday"],    # 3
        schema.columns["gender"],      # 4
        schema.columns["country"],     # 5
        schema.columns["q1"],          # 6
        schema.columns["q2"],          # 7
        schema.columns["q3"],          # 8
        schema.columns["q4"],          # 9
        schema.columns["q5"],          # 10
        schema.columns["q6"],          # 11
        schema.columns["q7"],          # 12
        schema.columns["q8"],          # 13
        schema.columns["q9"],          # 14
        schema.columns["q10"],         # 15
    ]

    if has_size:
        selected_columns.insert(6, size_column)  # put size after country

    result = df[selected_columns]

    dictPersons = {}

    for i, row in result.iterrows():
        uuid = row.iloc[0]
        first_name = row.iloc[1]
        last_name = row.iloc[2]
        birthday = row.iloc[3]
        gender = row.iloc[4]
        country = row.iloc[5]

        if has_size:
            size = row.iloc[6]
            offset = 1
        else:
            size = None
            offset = 0

        a1 = row.iloc[6 + offset]
        a2 = row.iloc[7 + offset]
        a3 = row.iloc[8 + offset]
        a4 = row.iloc[9 + offset]
        a5 = row.iloc[10 + offset]
        a6 = row.iloc[11 + offset]
        a7 = row.iloc[12 + offset]
        a8 = row.iloc[13 + offset]
        a9 = row.iloc[14 + offset] if str(row.iloc[14 + offset]) != "nan" else ""
        a10 = row.iloc[15 + offset] if str(row.iloc[15 + offset]) != "nan" else ""

        dictPersons[uuid] = Person.Person(
            i, uuid, first_name, last_name, birthday, gender, country, size,
            a1, a2, a3, a4, a5, a6, a7, a8, a9, a10
        )

    return dictPersons
        # Sort by first_name attribute of each Person object
    # sorted_dict = dict(sorted(dictPersons.items(), key=lambda item: item[1].first_name.lower()))
    # return sorted_dict 

def read_relations_csv_pd(file_path) -> list[dict]:
    global dictPersons
    relations_list = []

    try:
        df = pd.read_csv(file_path)

        result = df[[
            schema.columns_relations["uuid_1"],
            schema.columns_relations["name_1"],
            schema.columns_relations["uuid_2"],
            schema.columns_relations["name_2"],
            schema.columns_relations["relation"],
            schema.columns_relations["weight"],
            schema.columns_relations["description"],
        ]]

        skipped = 0

        for i, row in result.iterrows():
            uuid_1 = row.iloc[0]
            name_1 = row.iloc[1]
            uuid_2 = row.iloc[2]
            name_2 = row.iloc[3]
            relation = row.iloc[4]
            weight = row.iloc[5]
            description = row.iloc[6]

            if uuid_1 not in dictPersons:
                print(f"Skipping relation row {i}: uuid_1 not found in people CSV -> {uuid_1}")
                skipped += 1
                continue

            if uuid_2 not in dictPersons:
                print(f"Skipping relation row {i}: uuid_2 not found in people CSV -> {uuid_2}")
                skipped += 1
                continue

            id_1 = dictPersons[uuid_1].id
            id_2 = dictPersons[uuid_2].id

            relations_list.append({
                "id": i,
                "uuid_1": uuid_1,
                "name_1": name_1,
                "name_2": name_2,
                "uuid_2": uuid_2,
                "relation": relation,
                "weight": weight,
                "description": description,
                "id_1": id_1,
                "id_2": id_2,
            })

        print(f"Loaded {len(relations_list)} relations")
        if skipped > 0:
            print(f"Skipped {skipped} invalid relation rows")

    except Exception as e:
        print(f"Something went wrong in read_relations_csv_pd with file {file_path}")
        print(f"Error: {e}")

    return relations_list

def read_sizes_csv_pd(file_path) -> list[dict]:
    """
    Returns a flat list like:
    [
        {("Medium",1) : 4},
        {("Medium",1) : 2},
        ...
    ]
    """
    df = pd.read_csv(file_path, delimiter=';')

    size_label_column = schema.columns_sizes["size_label"]

    if size_label_column not in df.columns:
        raise ValueError(f"Missing required column: {size_label_column}")

    team_columns = [col for col in df.columns if col != size_label_column]

    result = {}

    for _, row in df.iterrows():
        size_label = row[size_label_column]

        for team_index, team_name in enumerate(team_columns, start=1):
            value = row[team_name]
            result[(size_label,team_index - 1)] = int(value) if pd.notna(value) else 0
    
    return result