"""
This module implements the main data analysis and visualisation functionality.

Author: Nicholas Holtzhausen
"""
import pandas as pd
import matplotlib.pyplot as plt
import subprocess


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

	Returns
	-------

	result_data : dictionary
		The statistics in a Python dictionary
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


def plot_against_date(df, col):
	"""
	Takes a specified column from the given df and plots it against the date column.

	Parameters
	----------

	df : pandas.DataFrame
		The dataframe containing the data
	col : str
		The name of the column to be plotted

	Returns
	-------
	plt : matplotlib.pyplot
		The plot of the specified column against the date

	"""

	plt.figure(figsize=(12, 6))
	plt.plot(df['Date'], df[col], label=col)
	plt.title('Stock Price Over Time')
	plt.xlabel('Date')
	plt.ylabel(col)
	plt.legend()

	return plt


def rolling_statistics(df, col, rolling_window):
	"""
	Returns a plot of the specified column, the rolling average and the rolling standard deviation
	against the date.

	Parameters
	----------

	df : pd.DataFrame
		A pandas dataframe representing the data
	col : str
		The column for which the rolling statistics must be calculated
	rolling_window : int
		The size (in days) of the rolling window
	"""

	new_df = df
	new_df['Rolling Mean'] = df[col].rolling(window=rolling_window).mean()
	new_df['Rolling Std'] = df[col].rolling(window=rolling_window).std()

	plt.figure(figsize=(12, 6))
	plt.plot(df['Date'], df[col], label=col)
	plt.plot(df['Date'], new_df['Rolling Mean'], label=f'Rolling Mean (window={rolling_window}')
	plt.plot(df['Date'], new_df['Rolling Std'], label=f'Rolling Std (window={rolling_window}')
	plt.title(f'Rolling Statistics of Column {col}')
	plt.xlabel('Date')
	plt.ylabel(col)
	plt.legend()

	return plt


def rsync_copy(source_file, destination_dir):
	"""
	Copies a specified file to a specified directory using the rsync function.

	Parameters
	----------

	source_file : str
		String representing the path to the source file
	destination_dir : str
		String representing path to the destination directory
	"""

	try:
		subprocess.run(['rsync', source_file, destination_dir], check=True)
		print(f'{source_file} successfully copied to directory {destination_dir}')
	except subprocess.CalledProcessError as e:
		print(f'Error copying file {e}')


