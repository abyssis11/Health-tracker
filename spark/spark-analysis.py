from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, monotonically_increasing_id, get_json_object, from_json
from pyspark.sql.types import StringType, StructField, StructType, TimestampType

# Define the schema of the Kafka messages
schema = StructType([
    StructField("trigger", StringType()),
    StructField("groupBy", StringType())
])

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Health-Data-Analysis") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1") \
    .getOrCreate()

# Read data from Kafka
df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "spark_trigger") \
    .load()

# Deserialize the value
df_values = df_kafka.selectExpr("CAST(value AS STRING)")


schema_ddl = schema.simpleString()

# Apply the schema to the data
df_structured = df_values.selectExpr(f"from_json(value, '{schema_ddl}') as data").select("data.*")
#df_structured = df_kafka.selectExpr("CAST(value AS STRING) as jsonStr") \
#    .select(from_json(col("jsonStr"), schema).alias("data")) \
#    .select("data.*")

def process_trigger(df, epoch_id):
    # JDBC URL
    jdbc_url = "jdbc:postgresql://postgres_db:5432/postgres"
    properties = {
        "user": "postgres",
        "password": "postgres",
        "driver": "org.postgresql.Driver"
    }

    group_by_values = df.select("groupBy").collect()

    if group_by_values:
        group_by_column = group_by_values[0]["groupBy"]
    else:
        # Handle the case when there are no rows
        group_by_column = None
    # Read data from PostgreSQL
    df_health_metrics = spark.read.jdbc(url=jdbc_url, table="health_metrics", properties=properties)
    df_user_goals = spark.read.jdbc(url=jdbc_url, table="user_health_goals", properties=properties)

    # Join the tables on user_id
    df_joined = df_health_metrics.join(df_user_goals, "user_id")

    if group_by_column == "age" or group_by_column == None:
        # Group by Age, Weight, and Height and calculate averages
        df_age_analysis = df_joined.groupBy("age").agg(
            avg("calorie_intake").alias("calorie_intake"),
            avg("exercise_duration").alias("exercise_duration"),
            avg("sleep_hours").alias("sleep_hours"),
            avg("water_consumed").alias("water_consumed")
        ).withColumn("id", monotonically_increasing_id())
        # Write the results back to PostgreSQL
        df_age_analysis.write.jdbc(url=jdbc_url, table="age_analysis", mode="overwrite", properties=properties)

    elif group_by_column == "weight" or group_by_column == None:
        df_weight_analysis = df_joined.groupBy("weight").agg(
            avg("calorie_intake").alias("calorie_intake"),
            avg("exercise_duration").alias("exercise_duration"),
            avg("sleep_hours").alias("sleep_hours"),
            avg("water_consumed").alias("water_consumed")
        ).withColumn("id", monotonically_increasing_id())
        # Write the results back to PostgreSQL
        df_weight_analysis.write.jdbc(url=jdbc_url, table="weight_analysis", mode="overwrite", properties=properties)

    elif group_by_column == "height" or group_by_column == None:
        df_height_analysis = df_joined.groupBy("height").agg(
            avg("calorie_intake").alias("calorie_intake"),
            avg("exercise_duration").alias("exercise_duration"),
            avg("sleep_hours").alias("sleep_hours"),
            avg("water_consumed").alias("water_consumed")
        ).withColumn("id", monotonically_increasing_id())
        # Write the results back to PostgreSQL
        df_height_analysis.write.jdbc(url=jdbc_url, table="height_analysis", mode="overwrite", properties=properties)


# Start the streaming query
query = df_structured.writeStream \
    .foreachBatch(process_trigger) \
    .start()

query.awaitTermination()
