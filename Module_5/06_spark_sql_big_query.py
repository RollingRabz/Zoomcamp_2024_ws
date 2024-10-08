#!/usr/bin/env python
# coding: utf-8


import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--input_green', required=True)
parser.add_argument('--input_yellow', required=True)
parser.add_argument('--output', required=True)

args = parser.parse_args()

input_green = args.input_green
input_yellow = args.input_yellow
output = args.output

spark = SparkSession.builder \
    .appName('test') \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.23.2") \
    .getOrCreate()

spark.conf.set('temporaryGcsBucket', 'dataproc-temp-asia-southeast1-355180390910-i9e7zgqu')

df_green = spark.read.parquet(input_green)

df_yellow = spark.read.parquet(input_yellow)

df_green = df_green.withColumnRenamed('lpep_pickup_datetime', 'pickup_datetime').withColumnRenamed('lpep_dropoff_datetime', 'dropoff_datetime')

df_yellow = df_yellow.withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime').withColumnRenamed('tpep_dropoff_datetime', 'dropoff_datetime')

# preserve order
common_colums = [
    'VendorID',
    'pickup_datetime',
    'dropoff_datetime',
    'store_and_fwd_flag',
    'RatecodeID',
    'PULocationID',
    'DOLocationID',
    'passenger_count',
    'trip_distance',
    'fare_amount',
    'extra',
    'mta_tax',
    'tip_amount',
    'tolls_amount',
    'improvement_surcharge',
    'total_amount',
    'payment_type',
    'congestion_surcharge'
]


# add new column name service type and give green as value
df_green_sel = df_green.select(common_colums).withColumn('service_type', F.lit('green'))

df_yellow_sel = df_yellow.select(common_colums).withColumn('service_type', F.lit('yellow'))

#combine 2 data
df_trips_data = df_green_sel.unionAll(df_yellow_sel)

#register df to table which enable sql query table name is trips_data
df_trips_data.registerTempTable('trips_data')

#try use query in module 4 here
df_result = spark.sql("""
SELECT 
    -- Reveneue grouping 
    PULocationID AS revenue_zone,
    date_trunc('month', pickup_datetime) AS revenue_month, 
    service_type, 

    -- Revenue calculation 
    SUM(fare_amount) AS revenue_monthly_fare,
    SUM(extra) AS revenue_monthly_extra,
    SUM(mta_tax) AS revenue_monthly_mta_tax,
    SUM(tip_amount) AS revenue_monthly_tip_amount,
    SUM(tolls_amount) AS revenue_monthly_tolls_amount,
    SUM(improvement_surcharge) AS revenue_monthly_improvement_surcharge,
    SUM(total_amount) AS revenue_monthly_total_amount,
    SUM(congestion_surcharge) AS revenue_monthly_congestion_surcharge,

    -- Additional calculations
    AVG(passenger_count) AS avg_montly_passenger_count,
    AVG(trip_distance) AS avg_montly_trip_distance
FROM
    trips_data
GROUP BY
    1, 2, 3
""")


df_result.write.format('bigquery') \
    .option('table', output) \
    .save()

