import unittest
import pandas as pd
import numpy as np
import mlops

class TestCustomTukeyTransformer(unittest.TestCase):

    def setUp(self):
        # Create a sample DataFrame for testing
        data = {'value': [10, 15, 20, 25, 30, 100, 110, 120, 130, 200]}
        self.df = pd.DataFrame(data)
        self.transformer_inner = CustomTukeyTransformer(target_column='value', fence='inner')
        self.transformer_outer = CustomTukeyTransformer(target_column='value', fence='outer')
    
    def test_basic_transform_inner(self):
        # Test basic transformation with 'inner' fence
        transformed_inner = self.transformer_inner.fit_transform(self.df)
    
        # Verify that outliers are clipped correctly for 'inner' fence
        self.assertTrue((transformed_inner['value'] == [10, 15, 20, 25, 30, 100, 110, 120, 130, 130]).all())
    
    def test_basic_transform_outer(self):
        # Test basic transformation with 'outer' fence
        transformed_outer = self.transformer_outer.fit_transform(self.df)
    
        # Verify that outliers are clipped correctly for 'outer' fence
        self.assertTrue((transformed_outer['value'] == [10, 15, 20, 25, 30, 100, 110, 120, 130, 200]).all())
    
    def test_edge_case_inner_fence(self):
        # Test with a dataset where all data points are within the inner fence
        data = {'value': [15, 20, 25, 30, 35]}
        df_inner = pd.DataFrame(data)
        transformed_inner = self.transformer_inner.fit_transform(df_inner)
    
        # Verify that no data points are clipped
        self.assertTrue((transformed_inner['value'] == [15, 20, 25, 30, 35]).all())
    
    def test_edge_case_outer_fence(self):
        # Test with a dataset where all data points are outside the outer fence
        data = {'value': [500, 600, 700]}
        df_outer = pd.DataFrame(data)
        transformed_outer = self.transformer_outer.fit_transform(df_outer)
    
        # Verify that all data points are clipped to the outer fence boundaries
        self.assertTrue((transformed_outer['value'] == [130, 130, 130]).all())
    
    def test_mixed_data_inner(self):
        # Test with a dataset that contains a mix of data points within and outside the inner fence
        data = {'value': [10, 15, 20, 25, 30, 100, 110, 120, 700]}
        df_mixed = pd.DataFrame(data)
        transformed_inner = self.transformer_inner.fit_transform(df_mixed)
    
        # Verify that outliers are clipped correctly for 'inner' fence
        self.assertTrue((transformed_inner['value'] == [10, 15, 20, 25, 30, 100, 110, 120, 130]).all())
    
    def test_mixed_data_outer(self):
        # Test with a dataset that contains a mix of data points within and outside the outer fence
        data = {'value': [10, 15, 20, 25, 30, 100, 110, 120, 700]}
        df_mixed = pd.DataFrame(data)
        transformed_outer = self.transformer_outer.fit_transform(df_mixed)
    
        # Verify that outliers are clipped correctly for 'outer' fence
        self.assertTrue((transformed_outer['value'] == [10, 15, 20, 25, 30, 100, 110, 120, 130, 200]).all())
    
    def test_change_fence_type(self):
        # Test changing the fence type after fitting
        transformed_inner = self.transformer_inner.fit_transform(self.df)
        self.transformer_inner.fence = 'outer'
        transformed_outer = self.transformer_inner.transform(self.df)
    
        # Verify that the transformer adapts to the new fence type correctly
        self.assertTrue((transformed_outer['value'] == [10, 15, 20, 25, 30, 100, 110, 120, 130, 200]).all())
    
    def test_unrecognized_fence_value(self):
        # Test initializing the transformer with an unrecognized fence value
        with self.assertRaises(AssertionError):
            transformer = CustomTukeyTransformer(target_column='value', fence='invalid_fence')
    
    def test_non_numeric_data(self):
        # Test with a DataFrame containing non-numeric data
        data = {'category': ['A', 'B', 'C', 'D']}
        df_non_numeric = pd.DataFrame(data)
    
        with self.assertRaises(AssertionError):
            transformed = self.transformer_inner.fit_transform(df_non_numeric)
    
    def test_empty_dataframe(self):
        # Test with an empty DataFrame
        empty_df = pd.DataFrame(columns=['value'])
        transformed_inner = self.transformer_inner.fit_transform(empty_df)
        transformed_outer = self.transformer_outer.fit_transform(empty_df)
    
        # Verify that the transformer handles empty DataFrame without errors
        self.assertTrue(empty_df.empty)
        self.assertTrue(transformed_inner.empty)
        self.assertTrue(transformed_outer.empty)
    
    def test_single_data_point(self):
        # Test with a DataFrame containing a single data point
        single_data = {'value': [42]}
        df_single = pd.DataFrame(single_data)
        transformed_inner = self.transformer_inner.fit_transform(df_single)
        transformed_outer = self.transformer_outer.fit_transform(df_single)
    
        # Verify that the transformer correctly handles a single data point
        self.assertTrue((transformed_inner['value'] == [42]).all())
        self.assertTrue((transformed_outer['value'] == [42]).all())
    
    def test_identical_data_points(self):
        # Test with a DataFrame where all data points are identical
        identical_data = {'value': [25, 25, 25, 25, 25]}
        df_identical = pd.DataFrame(identical_data)
        transformed_inner = self.transformer_inner.fit_transform(df_identical)
        transformed_outer = self.transformer_outer.fit_transform(df_identical)
    
        # Verify that the transformer handles identical data points without changes
        self.assertTrue((transformed_inner['value'] == [25, 25, 25, 25, 25]).all())
        self.assertTrue((transformed_outer['value'] == [25, 25, 25, 25, 25]).all())
    
    def test_data_points_on_inner_fence_boundary(self):
        # Test with data points that are exactly on the inner fence boundary
        boundary_data = {'value': [self.transformer_inner.inner_low, 10, 15, self.transformer_inner.inner_high, 30]}
        df_boundary = pd.DataFrame(boundary_data)
        transformed_inner = self.transformer_inner.fit_transform(df_boundary)
    
        # Verify that the transformer handles data points on the inner fence boundary correctly
        self.assertTrue((transformed_inner['value'] == [self.transformer_inner.inner_low, 10, 15, self.transformer_inner.inner_high, 30]).all())
    
    def test_data_points_on_outer_fence_boundary(self):
        # Test with data points that are exactly on the outer fence boundary
        boundary_data = {'value': [self.transformer_outer.outer_low, 10, 15, self.transformer_outer.outer_high, 30]}
        df_boundary = pd.DataFrame(boundary_data)
        transformed_outer = self.transformer_outer.fit_transform(df_boundary)
    
        # Verify that the transformer handles data points on the outer fence boundary correctly
        self.assertTrue((transformed_outer['value'] == [self.transformer_outer.outer_low, 10, 15, self.transformer_outer.outer_high, self.transformer_outer.outer_high]).all())
    
    def test_multiple_target_columns(self):
        # Test with a DataFrame containing multiple columns
        data = {'value1': [10, 15, 20, 25, 30],
                'value2': [100, 110, 120, 130, 140]}
        df_multiple = pd.DataFrame(data)
        transformer_multi = CustomTukeyTransformer(target_column='value1', fence='inner')
        transformed_multi = transformer_multi.fit_transform(df_multiple)
    
        # Verify that the transformer works correctly for each target column
        self.assertTrue((transformed_multi['value1'] == [10, 15, 20, 25, 30]).all())
    
    def test_different_iqr_multipliers(self):
        # Test with different IQR multipliers for inner and outer fences
        transformer_custom = CustomTukeyTransformer(target_column='value', fence='inner')
        transformer_custom.outer_low = self.transformer_outer.outer_low
        transformer_custom.outer_high = self.transformer_outer.outer_high
        transformer_custom.inner_low = self.transformer_inner.inner_low * 0.5  # Smaller multiplier for inner fence
        transformer_custom.inner_high = self.transformer_inner.inner_high * 0.5  # Smaller multiplier for inner fence
    
        transformed_custom = transformer_custom.fit_transform(self.df)
    
        # Verify that the transformer adapts to custom IQR multipliers correctly
        self.assertTrue((transformed_custom['value'] == [10, 15, 20, 25, 30, 100, 110, 120, 130, 130]).all())
    
    def test_data_with_nan_values(self):
        # Test with a DataFrame containing NaN values in the target column
        data_with_nan = {'value': [10, 15, np.nan, 25, 30]}
        df_with_nan = pd.DataFrame(data_with_nan)
        transformed_inner = self.transformer_inner.fit_transform(df_with_nan)
        transformed_outer = self.transformer_outer.fit_transform(df_with_nan)
    
        # Verify that the transformer handles missing values gracefully
        self.assertTrue(np.isnan(transformed_inner['value']).all())
        self.assertTrue(np.isnan(transformed_outer['value']).all())
    
    def test_change_target_column(self):
        # Test changing the target column after fitting
        transformed_inner = self.transformer_inner.fit_transform(self.df)
        self.transformer_inner.target_column = 'new_column'
        df_new_column = pd.DataFrame({'new_column': [10, 15, 20, 25, 30, 100, 110, 120, 130, 200]})
        transformed_new_column = self.transformer_inner.transform(df_new_column)
    
        # Verify that the transformer adapts to the new target column correctly
        self.assertTrue((transformed_new_column['new_column'] == [10, 15, 20, 25, 30, 100, 110, 120, 130, 130]).all())
    
    def test_negative_iqr(self):
        # Test with a dataset where the IQR is negative
        data = {'value': [5, 10, 15, 20, 25]}
        df_negative_iqr = pd.DataFrame(data)
        transformed_inner = self.transformer_inner.fit_transform(df_negative_iqr)
        transformed_outer = self.transformer_outer.fit_transform(df_negative_iqr)
    
        # Verify that the transformer handles negative IQR without
    
    def test_zero_iqr(self):
        # Test with a dataset where the IQR is 0
        data = {'value': [20, 20, 20, 20, 20]}
        df_zero_iqr = pd.DataFrame(data)
        transformed_inner = self.transformer_inner.fit_transform(df_zero_iqr)
        transformed_outer = self.transformer_outer.fit_transform(df_zero_iqr)
    
        # Verify that the transformer handles zero IQR without clipping the entire column to 0
        self.assertTrue((transformed_inner['value'] == [20, 20, 20, 20, 20]).all())
        self.assertTrue((transformed_outer['value'] == [20, 20, 20, 20, 20]).all())


unittest.main()


