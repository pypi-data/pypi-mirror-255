from pymongo import MongoClient
from uuid_extensions import uuid7str

# Initialize and return the MongoDB collection.
# Uses try-except block to handle connection errors.
initialize_collection = lambda uri, db_name, collection_name: MongoClient(uri)[db_name][collection_name]

# Insert data into the MongoDB collection.
set_data = lambda collection, data: collection.insert_one(data)

# Retrieve data from the MongoDB collection where 'available' is True.
get_data = lambda collection: collection.find({'available': True})

# Retrieve all data from the MongoDB collection.
get_all_data = lambda collection: collection.find()

# Retrieve a single document from the MongoDB collection by its ID.
get_data_one = lambda collection, id_data: collection.find_one({'_id': id_data})

# Remove data from the MongoDB collection by its ID and set 'available' to False.
remove_data_bool = lambda collection, id_data: collection.update_one({'_id': id_data}, {'$set': {'available': False}})

# Remove data from the MongoDB collection by its ID.
remove_data = lambda collection, id_data: collection.delete_one({'_id': id_data})

# Update data in the MongoDB collection by its ID.
update_data = lambda collection, id_data, data: collection.update_one({'_id': id_data}, {'$set': data})

# Delete all data from the MongoDB collection.
delete_db = lambda collection: collection.delete_many({})

# Count documents in the MongoDB collection where 'available' is True.
count_db_bool = lambda collection: collection.count_documents({'available': True})

# Count all documents in the MongoDB collection.
count_all_db = lambda collection: collection.count_documents({})

# Retrieve data from the MongoDB collection based on a specific field and its value.
search_data_by_field = lambda collection, field_name, field_value: collection.find({field_name: field_value})

# Update existing data if found, or insert new data if not found.
upsert_data = lambda collection, query, data: collection.update_one(query, {'$set': data}, upsert=True)

# Search across all fields of the MongoDB collection and return matching documents.
search_across_fields = lambda collection, search_query: collection.find({ "$or": [{field: { "$regex": search_query, "$options": "i" }} for field in collection.find_one().keys()]})

# Search for the given term in all fields of the MongoDB collection.
search_all_fields = lambda collection, search_term: collection.find({ "$or": [{key: {"$regex": search_term.lower(), "$options": "i"}} for key in collection.find_one().keys()]})

# Generate a UUID using the UUID7 strategy.
uuid_id = lambda: uuid7str()
