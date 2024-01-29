from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType, StructField, StructType, TimestampType

# Define the schema of the Kafka messages
schema = StructType([
    StructField("timestamp", TimestampType()),
    StructField("data", StringType())
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


def process_trigger(df, epoch_id):
    # JDBC URL
    jdbc_url = "jdbc:postgresql://postgres_db:5432/postgres"
    properties = {
        "user": "postgres",
        "password": "postgres",
        "driver": "org.postgresql.Driver"
    }

    # Read data from PostgreSQL
    df_user_goals = spark.read.jdbc(url=jdbc_url, table="user_health_goals", properties=properties)

    # Perform your analysis, join with Kafka data if needed
    # Example: Group by 'age' and calculate average 'height' and 'weight'
    result = df_user_goals.groupBy("age").avg("height", "weight")

    # Write the result back to PostgreSQL
    result.write.jdbc(url=jdbc_url, table="analysis", mode="append", properties=properties)

# Start the streaming query
query = df_structured.writeStream \
    .foreachBatch(process_trigger) \
    .start()

query.awaitTermination()
