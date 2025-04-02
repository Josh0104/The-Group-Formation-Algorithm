# The Group Formation Algorithm
 
## About
 This bachelor project is aiming to generate fair teams for an annual church camp based on the skills that the users have inputted themselves through a Google form.

The algorithm is to output five teams with the use of the different constraints it has been given.

You can read more about the project and how we handle the data: [link](https://camp.cbmbc.org/group-form)

## How to start the project


Create a virtual environment with the python version 3.10
```bash
python3.10 -m venv venv
```

On macOS and Linux
```bash 
source venv/bin/activate
```

On Windows
```bash
venv\Scripts\activate
```

To run the Python script with a file as input, use the following command:
```bash
python3 main.py --input <path/to/file>
```

### Command-line Arguments

| Argument         | Alternative       | Value Format          | Required | Default Value  | Description                                                  |
|------------------|-------------------|-----------------------|--------------------------------------|----------|----------------------------------------|
| `-i`             | `--input`         | `path/to/input.csv`   | Yes      | -              | File input to read                                           |
| `-g`             | `--group`         | `int`                 | No       | `5`              | Number of groups to form                                   |
| `-p`             | `--print`         | `flag`                | No       | `False`        | Print the output to console                                  |
| `-o`             | `--output`        | `path/to/output.csv`  | No       | `./output`     | Path for output file                                         |
| `-n`             | `--no-output`     | `flag`                | No       | `False`        | Do not generate an output file                               |
| `-v`             | `--verbose`       | `flag`                | No       | `False`        | Generate gurobi solution to console                          |
| `--no-gui`       |   -               | `flag`                | No       | `False`        | Prevent the program to create a graphical user interface     |



<details>
<summary> Alternative method  </summary>

Direct Execution Without Activation

macOS and Linux 
```bash
venv/bin/python main.py
```

Windows
```bash
venv\Scripts\python.exe main.py
```
</details>

### To deactivate the Virtual Environment

```bash
deactivate
```

### Required Packages  

The dependencies for this project are listed in the [`requirements.txt`](requirements.txt) file.  

### Gurobi License  
To obtain results, a **Gurobi license** is required. You can find instructions on how to get a license on their [official website](https://www.gurobi.com/).


## Additional Notes

To create a virtual environment, run the following command
```bash
python3 -m venv venv
```

## For the developers of the project

## Branch Naming Convention
<details>
  <summary>📌 Click to expand branch categories</summary>

- **feature/** → New feature development  
- **debug/** → Fixing bugs in development  
- **improvement/** → Enhancements and optimizations  
- **refactor/** → Code refactoring without changing functionality  
- **docs/** → Documentation updates  
- **experiment/** → Experimental features or prototypes  
- **test/** → Adding or improving tests  
- **release/** → Preparing a new software release  

</details>
