FROM bitnami/spark:3.2.4

WORKDIR /app

COPY requirements.txt ./

# Copy the PostgreSQL JDBC driver into the Spark jars folder
COPY postgresql-42.7.1.jar /opt/bitnami/spark/jars/

RUN pip install -r requirements.txt

COPY . .

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1", "./spark-analysis.py"]
