from pymongo import MongoClient

# Change this if you're using MongoDB Atlas or custom host/port
# MONGODB_URL = "mongodb://localhost:27017/"
MONGO_URL = "mongodb+srv://nikitann2501:pPSQy2RdbCsPh5c5@cluster0.bjltkz1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URL)
db = client.farmer_feedback

members_collection = db.members
feedback_collection = db.feedbacks
