import pandas as pd
import numpy as np
import csv
import sys

def main():
    if len(sys.argv) == 5:
        input_file = sys.argv[1]
        weights = sys.argv[2]
        impacts = sys.argv[3]
        result_file = sys.argv[4]
        topsis(input_file, weights, impacts, result_file)
    else:
        print("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        print("Example: python 101556-topsis.py 101556-data.csv \"1,1,1,2\" \"+,+,-,+\" 101556-result.csv")

def topsis(input_file, weights, impacts, result_file):
    try:
        df = pd.read_csv(input_file)
        print(df)

        ## Checking for the correct number of parameters
        if len(weights.split(',')) != len(df.columns) - 1 or len(impacts.split(',')) != len(df.columns) - 1:
            raise ValueError("Number of weights, impacts, and columns must be the same.")

        ## Convert weights and impacts to lists
        weights = [float(w) for w in weights.split(',')]
        # print(weights)
        
        impacts = [1 if i == '+' else 0 for i in impacts.split(',')]
        # print(impacts)
        
        ## Check for numeric values in the columns
        if not df.iloc[:, 1:].applymap(lambda x: isinstance(x, (int, float))).all().all():
            raise ValueError("Columns from 2nd to last must contain numeric values only.")

        ## Normalize the data
        normalized_df = df.iloc[:, 1:] / np.sqrt((df.iloc[:, 1:] ** 2).sum())
        # print(normalized_df)

        ## Calculate weighted normalized decision matrix
        weighted_normalized_df = normalized_df * weights
        print(weighted_normalized_df)

        ## Calculate ideal positive and negative solutions
        ideal_positive = (np.array(weighted_normalized_df.max()) * np.array(impacts)) + (np.array(weighted_normalized_df.min()) * (1 - np.array(impacts)))
        # print("error")
        print(ideal_positive)
        ideal_negative = (np.array(weighted_normalized_df.max()) * (1 - np.array(impacts))) + (np.array(weighted_normalized_df.min()) * (np.array(impacts)))
        print(ideal_negative)

        # Calculate separation measures
        separation_positive = ((weighted_normalized_df - ideal_positive) ** 2).sum(axis=1) ** 0.5
        separation_negative = ((weighted_normalized_df - ideal_negative) ** 2).sum(axis=1) ** 0.5
        # print(separation_positive, separation_negative)

        # Calculate TOPSIS score
        topsis_score = separation_negative / (separation_negative + separation_positive)

        # Calculate rank
        rank = topsis_score.rank(ascending=False)

        # Create result dataframe
        result_df = pd.concat([df, pd.DataFrame({'Topsis Score': topsis_score, 'Rank': rank})], axis=1)

        # Save result to CSV with quotes around each value
        result_df.to_csv(result_file, index=False, quoting=csv.QUOTE_ALL, quotechar='"')

        print(f"TOPSIS completed successfully. Result saved to {result_file}")

    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
    
