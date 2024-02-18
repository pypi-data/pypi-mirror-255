import csv
import io
import random
import string
import boto3
import time
import pandas as pd
import psycopg2

class df_to_rs:
    def __init__(self, region_name, s3_bucket, aws_access_key_id, aws_secret_access_key, redshift_c):
        """
        region_name: AWS region name, e.g., 'ap-south-1'.
        s3_bucket: Name of the S3 bucket to upload CSV files.
        aws_access_key_id: AWS access key ID.
        aws_secret_access_key: AWS secret access key.
        redshift_c: psycopg2 connection object to Redshift, e.g.,
        redshift_c = psycopg2.connect(dbname='more', host="hostname.ap-south-1.redshift.amazonaws.com", port=1433, user='ankit.goel', password='xxxx')
        redshift_c.set_session(autocommit=True)
        """
        self.region_name = region_name
        self.s3_bucket = s3_bucket
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.redshift_c = redshift_c

    def upload_to_redshift(self, df, dest):
        """
        Uploads the given DataFrame to the specified destination in Redshift.
        df: pandas DataFrame to be uploaded.
        dest: Redshift destination table, including schema, e.g., 'analytics.ship_pen'.
        """
        try:
            start_time = time.time()
            print("Generating randomized CSV filename...")
            csv_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.csv'
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            print("Converting DataFrame to CSV in-memory...")
            def escape_special_chars(s):
                if isinstance(s, str):
                    return s.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace(',', '\\,')
                return s  # Return as is if not a string

            string_columns = df.select_dtypes(include=['object']).columns
            df[string_columns] = df[string_columns].applymap(escape_special_chars)

            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, quoting=csv.QUOTE_ALL, quotechar='"', na_rep='')
            csv_buffer.seek(0)
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            print(f"Uploading CSV to S3 bucket '{self.s3_bucket}'...")
            s3 = boto3.resource('s3', region_name=self.region_name, aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            s3.Object(self.s3_bucket, csv_filename).put(Body=csv_buffer.getvalue())
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            print("Preparing Redshift COPY command...")
            columns = ','.join(df.columns)
            copy_query = f"""
            COPY {dest} ({columns})
            FROM 's3://{self.s3_bucket}/{csv_filename}'
            ACCESS_KEY_ID '{self.aws_access_key_id}'
            SECRET_ACCESS_KEY '{self.aws_secret_access_key}'
            DELIMITER ','
            IGNOREHEADER 1
            REMOVEQUOTES
            REGION '{self.region_name}';
            """
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            print("Executing Redshift COPY command...")
            self.redshift_c.cursor().execute(copy_query)
            print(f"Time taken: {int(time.time() - start_time)} seconds")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            try:
                print(f"Deleting CSV file '{csv_filename}' from S3...")
                s3.Object(self.s3_bucket, csv_filename).delete()
                print(f"Time taken: {int(time.time() - start_time)} seconds")
            except Exception as e:
                print(f"An error occurred during cleanup: {e}")

            print("Upload to Redshift process completed.")



    def upsert_to_redshift(self, df, dest_table, upsert_columns, clear_dest_table=False):
        """
        Upserts the given DataFrame to the specified destination table in Redshift.
        Optionally clears the destination table if clear_dest_table is True.
        
        Parameters:
        - df: pandas DataFrame to be upserted.
        - dest_table: Redshift destination table, including schema, e.g., 'analytics.ship_pen'.
        - upsert_columns: List of columns to use for the upsert condition, e.g., ['id', 'name'].
        - clear_dest_table: Boolean, if True, clears the destination table before upserting.
        """
        cursor = self.redshift_c.cursor()
        staging_table = dest_table + "_stgg"

        # Check if any upsert column has nulls
        has_nulls = df[[col.replace('"','') for col in upsert_columns]].isnull().any().any()

        try:
            start_time = time.time()
            print("Creating staging table...")
            create_staging_query = f"DROP TABLE IF EXISTS {staging_table}; CREATE TABLE {staging_table} AS SELECT * FROM {dest_table} WHERE 1 = 0;"
            cursor.execute(create_staging_query)
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            print("Uploading data to staging table...")
            self.upload_to_redshift(df, dest=staging_table)

            cursor.execute("BEGIN;")
            start_time = time.time()

            if clear_dest_table:
                print("Truncating destination table...")
                #cursor.execute(f"DELETE FROM {dest_table};")
                cursor.execute(f"TRUNCATE TABLE {dest_table};")
            else:
                print("Deleting matching rows from main table...")
                if has_nulls:
                    where_condition = " AND ".join([f"({dest_table}.{col} = staging.{col} OR ({dest_table}.{col} IS NULL AND staging.{col} IS NULL))" for col in upsert_columns])
                else:
                    where_condition = " AND ".join([f"({dest_table}.{col} = staging.{col})" for col in upsert_columns])
                delete_query = f"DELETE FROM {dest_table} USING {staging_table} AS staging WHERE {where_condition};"
                cursor.execute(delete_query)
                print(f"Time taken: {int(time.time() - start_time)} seconds")

            print("Inserting new rows from staging table into main table...")
            insert_query = f"INSERT INTO {dest_table} SELECT * FROM {staging_table};"
            cursor.execute(insert_query)
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            cursor.execute("COMMIT;")

        except Exception as e:
            print(f"An error occurred: {str(e)}. Rolling back transaction...")
            cursor.execute("ROLLBACK;")
            raise
        finally:
            try:
                start_time = time.time()
                print("Dropping staging table...")
                drop_staging_query = f"DROP TABLE IF EXISTS {staging_table};"
                cursor.execute(drop_staging_query)
                print(f"Time taken: {int(time.time() - start_time)} seconds")
            except Exception as e:
                print(f"An error occurred during staging table cleanup: {e}")

        print("Upsert to Redshift completed successfully.")
