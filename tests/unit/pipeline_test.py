def test_get_cloud_files_options(mock_pipeline, mock_cloud_files_options):
    result = mock_pipeline.get_cloud_files_options(file_format='parquet', schema_location='sample/schema_location_path')
    expected = mock_cloud_files_options
    assert result == expected


def test_create_group_by_field_list(mock_pipeline, mock_dataframe, mock_primary_key, mock_aggregation_fields):
    result = mock_pipeline.create_group_by_field_list(dataframe=mock_dataframe, primary_key=mock_primary_key)
    expected = mock_aggregation_fields
    assert all(str(result[i].name) == str(expected[i].name) for i in range(len(result)))


def test_create_pk_is_not_null_condition(mock_pipeline, mock_primary_key_multiple_fields):
    result = mock_pipeline.create_pk_is_not_null_condition(primary_key=mock_primary_key_multiple_fields)
    expected = 'FIRST_ID IS NOT NULL AND SECOND_ID IS NOT NULL'
    assert result == expected

