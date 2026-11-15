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
        column_quality = {}

        for column in df.columns:
            series = df[column]
            name = str(column)

            missing = int(series.isna().sum())

            column_quality[name] = {
                'missing_values': missing,
                'missing_percentage': round(
                    missing / len(df) * 100, 2
                ) if len(df) else 0,
                'data_type': str(series.dtype),
            }

            if pd.api.types.is_numeric_dtype(series):
                numeric_stats[name] = {
                    'mean': float(series.mean()) if pd.notna(series.mean()) else None,
                    'median': float(series.median()) if pd.notna(series.median()) else None,
                    'mode': float(series.mode().iloc[0]) if not series.mode().empty else None,
                    'minimum': float(series.min()) if pd.notna(series.min()) else None,
                    'maximum': float(series.max()) if pd.notna(series.max()) else None,
                    'standard_deviation': float(series.std()) if pd.notna(series.std()) else None,
                    'q1': float(series.quantile(0.25)) if series.notna().any() else None,
                    'q3': float(series.quantile(0.75)) if series.notna().any() else None,
                }

                chart_data[name] = [
                    {
                        'label': str(index),
                        'value': float(value) if pd.notna(value) else None
                    }
                    for index, value in series.head(100).items()
                ]

            elif pd.api.types.is_datetime64_any_dtype(series):
                continue

            else:
                counts = series.value_counts().head(10)

                categorical_stats[name] = {
                    'unique_values': int(series.nunique()),
                    'most_common': str(series.mode().iloc[0]) if not series.mode().empty else None,
                    'most_common_count': int(counts.iloc[0]) if not counts.empty else 0,
                }

                chart_data[name] = [
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
            'missing_values': int(df.isna().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum()),
            'numeric_columns': int(len(numeric_stats)),
            'categorical_columns': int(len(categorical_stats)),
            'numeric_statistics': numeric_stats,
            'categorical_statistics': categorical_stats,
            'column_quality': column_quality,
            'correlation': correlation.to_dict(),
            'chart_data': chart_data,
        }

    finally:
        dataset.file.close()
