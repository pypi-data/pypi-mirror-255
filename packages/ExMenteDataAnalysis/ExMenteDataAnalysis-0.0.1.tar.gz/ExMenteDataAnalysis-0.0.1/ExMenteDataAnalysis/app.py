"""
This module implements the main data analysis and visualisation functionality.

Author: Nicholas Holtzhausen
"""
import pandas
import pandas as pd
import matplotlib as plt


def csv_to_df(file_loc):
	"""
	Reads a CSV file and returns a pandas DataFrame containing the data.

	Parameters
	----------
	file_loc : str
		The file location of the CSV data

	Returns
	-------
	df : pd.DataFrame
		The original data represented as a dataframe
	"""

	df = pd.read_csv(file_loc)

	return df


def df_to_csv(df):
	"""
	Reads a pandas dataframe and returns a CSV file containing the data.

	Parameters
	----------
	df : pandas.Dataframe
		The dataframe representation of the data

	Returns
	-------
	csv_file : str
		The original data represented as a CSV file
	"""

	file = df.to_csv()
	return file


def basic_analysis(df, col, df_type='cat'):
	"""
	Reads a pandas dataframe and calculates basic summary and descriptive statistics,
	and provides some basic data visualisation.

	Parameters
	----------

	df : pandas.DataFrame
		A dataframe containing the data
	col : str
		The column for which statistics must be calculated
	df_type : str
		The type of df being passed to the function.
		Options:
			'cat' (default): a df with categorical columns
			'num': a df with numerical columns
	"""

	result_data = {}
	if df_type == 'num':
		mean = df[col].mean()
		median = df[col].median()
		std = df[col].std()

		result_data = {
			'Mean': mean,
			'Median': median,
			'Standard Deviation': std
		}

	elif df_type == 'cat':
		count = df[col].count()
		unique = df[col].unique()

		result_data = {
			'Count': count,
			'Unique': unique
		}

	return result_data




