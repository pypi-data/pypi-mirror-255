
# df_to_rs

`df_to_rs` is a Python package that provides convenient methods to upload and upsert Pandas DataFrames to Amazon Redshift.

## Installation

Install the package using pip:

```bash
pip install df_to_rs
```

## Usage

### Initialization

```python
from df_to_rs import df_to_rs
import psycopg2

uploader = df_to_rs(
    region_name='ap-south-1',
    s3_bucket='your-s3-bucket',
    aws_access_key_id='your-access-key-id',
    aws_secret_access_key='your-secret-access-key',
    redshift_c=psycopg2.connect(dbname='more', host="hostname.ap-south-1.redshift.amazonaws.com", port=1433, user='username', password='password')
)
```

### Upload DataFrame to Redshift

```python
uploader.upload_to_redshift(df, dest='analytics.ship_pen')
```

### Upsert DataFrame to Redshift

Upsert (insert or update) the DataFrame into a specified destination table in Redshift. Matching rows are identified by the specified columns, and existing rows are deleted before new rows are inserted.

```python
uploader.upsert_to_redshift(df, dest_table='analytics.ship_pen', upsert_columns=['id', 'name'])
```

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
