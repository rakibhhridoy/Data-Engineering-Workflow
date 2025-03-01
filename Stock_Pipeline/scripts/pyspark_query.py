from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("StockDataQuery") \
    .config("spark.jars", "/app/postgresql-42.6.0.jar") \
    .getOrCreate()

# PostgreSQL connection details
postgres_url = "jdbc:postgresql://postgres:5432/mydatabase"
postgres_properties = {
    "user": "admin",
    "password": "password",
    "driver": "org.postgresql.Driver"
}

# Read data from PostgreSQL
df = spark.read.jdbc(url=postgres_url, table="stock_data", properties=postgres_properties)

# Show the data
df.show()

# Perform a query (e.g., filter data for a specific symbol)
df_filtered = df.filter(df.symbol == "IBM")
df_filtered.show()

# Stop the Spark session
spark.stop()