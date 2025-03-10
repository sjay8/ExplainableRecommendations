import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, MapType, FloatType
from faker import Faker

# Initialize Faker
fake = Faker()

# Create a SparkSession
spark = SparkSession.builder \
    .appName("YourAppName") \
    .getOrCreate()

# Define the schema
item_schema = StructType([
    StructField("item_id", StringType(), False),
    StructField("name", StringType(), False),
    StructField("genre", StringType(), False)
])


# Create a list of dummy data
item_num = 100  # Number of rows
dummy_data = [(str(random.randint(0, item_num)), fake.name(), random.choice(["Action", "Drama", "Comedy"])) for _ in range(item_num)]


# Create an empty DataFrame with the specified schema
item_df = spark.createDataFrame(dummy_data, item_schema)

item_df.write.mode("overwrite").parquet("item_df.parquet")

# Show the DataFrame schema
item_df.printSchema()
item_df.show(10, truncate=False)

# Start user profile datafarme

schema = StructType([
    StructField("user_id", StringType(), False),
    StructField("watched_item_list", ArrayType(StringType()), False),
    StructField("exposed_item_list", ArrayType(StringType()), False), 
    StructField("liked_item_list", ArrayType(StringType()), True),
    StructField("completion_item_list", MapType(StringType(), FloatType()), False)
])

# Create a list of dummy data
num_users = 1000  # Number of users
dummy_data = []
for _ in range(num_users):
    watched_items = [str(random.randint(0, item_num)) for _ in range(random.randint(1, 5))]
    exposed_items = [str(random.randint(0, item_num)) for _ in range(random.randint(1, 5))]
    liked_items = [item for item in watched_items if random.random() < 0.3]
    completion_items = {item: random.choice([0.2, 0.5, 0.8, 1.0]) for item in watched_items}
    dummy_data.append((fake.uuid4(), watched_items, exposed_items, liked_items, completion_items))

# Create a PySpark DataFrame
user_df = spark.createDataFrame(dummy_data, schema=schema)
user_df.write.mode("overwrite").parquet("user_df.parquet")

user_df.show(truncate=False)

# Stop the SparkSession
spark.stop()