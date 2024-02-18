import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import unittest
import pandas as pd
from mtbp3.util.cdt import diff_2cols_in_1df, diff_2cols_in_2df

class TestCdt(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({'ARM': [1, 2, 3, 4], 'ACTARM': [1, 2, 5, 4]})
        self.df1 = pd.DataFrame({'col': [1, 2, 3, 4], 'gp': ['1', '1', '3', '3']})
        self.df2 = pd.DataFrame({'col': [1, 2, 3, 6], 'gp': ['1', '2', '3', '3']})

    def test_diff_2cols_in_1df_with_difference(self):
        expected_output = pd.DataFrame({'ARM': [3], 'ACTARM': [5], 'diff': ['True']})
        result = diff_2cols_in_1df(self.df)
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(len(result), len(self.df))

    def test_diff_2cols_in_1df_without_difference(self):
        expected_output = "The two columns are the same."
        tmpdf = self.df[['ARM', 'ARM']]
        tmpdf.columns = ['ARM', 'ACTARM']
        result = diff_2cols_in_1df(tmpdf)
        self.assertEqual(result, expected_output)

    def test_diff_2cols_in_1df_invalid_input(self):
        expected_output = "Input is not a DataFrame."
        result = diff_2cols_in_1df("not a dataframe")
        self.assertEqual(result, expected_output)

    def test_diff_2cols_in_1df_missing_column(self):
        expected_output = "Column 'COL' does not exist in the DataFrame."
        result = diff_2cols_in_1df(self.df, col1='COL')
        self.assertEqual(result, expected_output)

    def test_diff_2cols_in_2df_with_existing_column(self):
        expected_output = pd.DataFrame({'gp_1': ['1', '3'], 'gp_2': ['1', '3'], 'source_1': ['True', 'True'], 'source_2': ['True', 'True'], 'count': [1, 2]})
        result = diff_2cols_in_2df(self.df1, self.df2, 'col', 'gp')
        self.assertTrue(isinstance(result, pd.DataFrame))
        # self.assertEqual(result.to_dict(), expected_output.to_dict())

    def test_diff_2cols_in_2df_with_non_existing_column(self):
        expected_output = "Column 'non_existing_col' not found in both dataframes."
        result = diff_2cols_in_2df(self.df1, self.df2, 'non_existing_col', 'gp')
        self.assertEqual(result, expected_output)

    def test_diff_2cols_in_2df_with_non_existing_group(self):
        expected_output = "Group 'non_existing_gp' not found in both dataframes."
        result = diff_2cols_in_2df(self.df1, self.df2, 'col', 'non_existing_gp')
        self.assertEqual(result, expected_output)

    def test_diff_2cols_in_2df_with_same_group_and_column(self):
        expected_output = "Columns 'gp' and 'col' should be different columns."
        result = diff_2cols_in_2df(self.df1, self.df2, 'gp', 'gp')
        self.assertEqual(result, expected_output)

    #def test_diff_2cols_in_2df_with_non_unique_values_in_df1(self):
    #    expected_output = "All values in column 'col' of df1 should be unique."
    #    result = diff_2cols_in_2df(self.df1.append({'col': 1, 'gp': '4'}, ignore_index=True), self.df2, 'col', 'gp')
    #    self.assertEqual(result, expected_output)

    #def test_diff_2cols_in_2df_with_non_unique_values_in_df2(self):
    #    expected_output = "All values in column 'col' of df2 should be unique."
    #    result = diff_2cols_in_2df(self.df1, self.df2.append({'col': 1, 'gp': '4'}, ignore_index=True), 'col', 'gp')
    #    self.assertEqual(result, expected_output)

if __name__ == "__main__":
    unittest.main()