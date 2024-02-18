# Project Description
- for: Assignment-1(UCS654)
- Submitted by: Ishan Mathur
- Roll no: 102103408
- Group: 3COE15

# TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)

This Python script implements the TOPSIS method for multi-criteria decision-making. It takes a CSV file containing a decision matrix, weights, and impacts as input, and produces a ranked result based on the TOPSIS score.

## Installation
```bash
pip install Topsis-Ishan-102103408
```

## Usage

```bash
from Topsis_Ishan_102103408.topsis import topsis 
inputFile="sample.csv"
weights="1,1,1,1"
impacts="-,+,+,+"
resultFile="result.csv" 
topsis(inputFile, weights, impacts, resultFile)
```

OR 

You can use this package via command line as:
```bash
python -m Topsis_Ishan_102103408.topsis [InputDataFile as .csv] [Weights as a string] [Impacts as a string] [ResultFileName as .csv]
```

- `InputDataFile`: Path to the CSV file containing the input data.
- `Weights`: Comma-separated weights for each criterion.
- `Impacts`: Comma-separated impact direction for each criterion (`+` for maximization, `-` for minimization).
- `ResultFileName`: Name of the file to save the TOPSIS results.

## Requirements

- Python 3
- pandas
- numpy

## Input File Format
The input data should be in a CSV format with the following structure:

| Fund Name | P1   | P2   | P3   | P4   | P5    |
|-----------|------|------|------|------|-------|
| M1        | 0.84 | 0.71 | 6.7  | 42.1 | 12.59 |
| M2        | 0.91 | 0.83 | 7    | 31.7 | 10.11 |
| M3        | 0.79 | 0.62 | 4.8  | 46.7 | 13.23 |
| M4        | 0.78 | 0.61 | 6.4  | 42.4 | 12.55 |
| M5        | 0.94 | 0.88 | 3.6  | 62.2 | 16.91 |
| M6        | 0.88 | 0.77 | 6.5  | 51.5 | 14.91 |
| M7        | 0.66 | 0.44 | 5.3  | 48.9 | 13.83 |
| M8        | 0.93 | 0.86 | 3.4  | 37   | 10.55 |


## Output

The script generates a CSV file containing the TOPSIS score and rank for each object:

| Fund Name | P1   | P2   | P3   | P4   | P5    | Topsis Score         | Rank |
|-----------|------|------|------|------|-------|----------------------|------|
| M1        | 0.84 | 0.71 | 6.7  | 42.1 | 12.59 | 0.41855328299643013 | 7.0  |
| M2        | 0.91 | 0.83 | 7.0  | 31.7 | 10.11 | 0.4663977143091959  | 5.0  |
| M3        | 0.79 | 0.62 | 4.8  | 46.7 | 13.23 | 0.5374784843237046  | 3.0  |
| M4        | 0.78 | 0.61 | 6.4  | 42.4 | 12.55 | 0.4295182212044884  | 6.0  |
| M5        | 0.94 | 0.88 | 3.6  | 62.2 | 16.91 | 0.5453066145383307  | 2.0  |
| M6        | 0.88 | 0.77 | 6.5  | 51.5 | 14.91 | 0.39814192807166954 | 8.0  |
| M7        | 0.66 | 0.44 | 5.3  | 48.9 | 13.83 | 0.4743648907682155  | 4.0  |
| M8        | 0.93 | 0.86 | 3.4  | 37.0 | 10.55 | 0.6392872727749049  | 1.0  |


## Error Handling

- If the input file is not found, an error message will be displayed.
- If the number of weights, impacts, or columns in the decision matrix is incorrect, a `ValueError` will be raised.
- If the columns from the 2nd to the last do not contain numeric values, a `ValueError` will be raised.
- Any unexpected errors during the execution will be displayed.

## LICENSE

(c) 2024 Ishan Mathur

This project is licensed under the [MIT License](LICENSE).