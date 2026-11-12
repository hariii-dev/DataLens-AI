import pandas as pd


def analyze_dataset(dataset):
    dataset.file.open('rb')

    try:
        if dataset.file_type == 'csv':
            df = pd.read_csv(dataset.file)
        else:
            df = pd.read_excel(dataset.file, engine='openpyxl')

        missing_values = df.isnull().sum()
        duplicate_rows = int(df.duplicated().sum())

        column_details = []

        for column in df.columns:
            column_details.append({
                'name': str(column),
                'data_type': str(df[column].dtype),
                'missing_values': int(missing_values[column]),
                'unique_values': int(df[column].nunique()),
            })

        preview_df = df.head(10).astype(object)
        preview_df = preview_df.where(pd.notna(preview_df), None)

        dataset.row_count = len(df)
        dataset.column_count = len(df.columns)
        dataset.status = 'completed'

        dataset.save(update_fields=[
            'row_count',
            'column_count',
            'status',
            'updated_at'
        ])

        return {
            'columns': [str(col) for col in df.columns],
            'preview': preview_df.to_dict(orient='records'),
            'rows': dataset.row_count,
            'columns_count': dataset.column_count,
            'missing_values': int(missing_values.sum()),
            'duplicate_rows': duplicate_rows,
            'column_details': column_details,
            'data_quality': {
                'total_cells': int(df.size),
                'missing_cells': int(missing_values.sum()),
                'duplicate_rows': duplicate_rows,
                'complete_cells': int(df.size - missing_values.sum()),
            }
        }

    finally:
        dataset.file.close()
