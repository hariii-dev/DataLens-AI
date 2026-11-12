import pandas as pd


def generate_analytics(dataset):
    dataset.file.open('rb')

    try:
        if dataset.file_type == 'csv':
            df = pd.read_csv(dataset.file)
        else:
            df = pd.read_excel(
                dataset.file,
                engine='openpyxl'
            )

        numeric_stats = {}
        categorical_stats = {}
        chart_data = {}

        for column in df.columns:
            series = df[column]

            if pd.api.types.is_numeric_dtype(series):
                numeric_stats[str(column)] = {
                    'mean': float(series.mean()) if pd.notna(series.mean()) else None,
                    'median': float(series.median()) if pd.notna(series.median()) else None,
                    'minimum': float(series.min()) if pd.notna(series.min()) else None,
                    'maximum': float(series.max()) if pd.notna(series.max()) else None,
                    'standard_deviation': float(series.std()) if pd.notna(series.std()) else None,
                }

                chart_data[str(column)] = [
                    {
                        'label': str(index),
                        'value': float(value) if pd.notna(value) else None
                    }
                    for index, value in series.head(100).items()
                ]

            else:
                counts = series.value_counts().head(10)

                categorical_stats[str(column)] = {
                    'unique_values': int(series.nunique()),
                    'most_common': str(series.mode().iloc[0]) if not series.mode().empty else None,
                    'most_common_count': int(counts.iloc[0]) if not counts.empty else 0,
                }

                chart_data[str(column)] = [
                    {
                        'label': str(label),
                        'value': int(value)
                    }
                    for label, value in counts.items()
                ]

        correlation = df.corr(numeric_only=True)
        correlation = correlation.astype(object).where(
            pd.notna(correlation), None
        )

        return {
            'dataset': dataset.name,
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'numeric_statistics': numeric_stats,
            'categorical_statistics': categorical_stats,
            'correlation': correlation.to_dict(),
            'chart_data': chart_data,
        }

    finally:
        dataset.file.close()
