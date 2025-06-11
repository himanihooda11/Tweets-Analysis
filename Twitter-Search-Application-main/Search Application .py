#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import Libraries
import pymongo
import json
import time
from datetime import datetime
import mysql.connector as cnx
import pickle
import os
import csv
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')


# In[4]:


# connect to mysql server
mydb = cnx.connect(
  host="localhost",
  user="root",
  password="Adarsh20@",
  database="mydatabase"
)

mycursor = mydb.cursor(buffered=True)


# In[5]:


#connect to mongodb
client = pymongo.MongoClient("mongodb://localhost:27017/") 
db = client["Tweets"]
tweets_collec = db["Tweets_collection"]


# In[6]:


class Cache:
    def __init__(self, max_size=15000, evict_strategy='least_accessed', checkpoint_interval=30, ttl=None):
        self.max_size = max_size
        self.evict_strategy = evict_strategy
        self.checkpoint_interval = checkpoint_interval
        self.ttl = ttl
        self.cache = {}
        self.access_count = {}
        self.last_checkpoint = time.time()
    
        if os.path.exists('cache.checkpoint'):
            self.load_from_checkpoint('cache.checkpoint')

    def load_from_checkpoint(self, checkpoint_file):
        with open(checkpoint_file, 'rb') as f:
            self.cache, self.access_count = pickle.load(f)

    def save_to_checkpoint(self, checkpoint_file):
        with open(checkpoint_file, 'wb') as f:
            pickle.dump((self.cache, self.access_count), f)
            
    def get(self, key):
        
        if key[0].isdigit() or key.startswith('#'):
            if key not in self.cache:
                return None
            similar_keys = [key]
            
        else:
            similar_keys = []
            for k in self.cache:
                if key in k:
                    similar_keys.append(k)

            if len(similar_keys) == 0:
                return None
        
        if self.ttl is not None and (time.time() - self.cache[key]['timestamp']) > self.ttl:
            del self.cache[key]
            del self.access_count[key]
            return None
        
        for i in similar_keys:
            self.access_count[i] += 1
            
            if self.evict_strategy == 'least_accessed':
                least_accessed_key = min(self.access_count, key=self.access_count.get)
                if len(self.cache) > self.max_size and key != least_accessed_key:
                    del self.cache[least_accessed_key]
                    del self.access_count[least_accessed_key]
                
        return [self.cache[k]['value'] for k in similar_keys]

    def put(self, key, value):
        if not key.startswith('#'):
            key = key.lower()
        self.cache[key] = {'value': value, 'timestamp': time.time()}
        self.access_count[key] = 0
        if len(self.cache) > self.max_size:
            if self.evict_strategy == 'least_accessed':
                least_accessed_key = min(self.access_count, key=self.access_count.get)
                del self.cache[least_accessed_key]
                del self.access_count[least_accessed_key]
            elif self.evict_strategy == 'oldest':
                oldest_key = min(self.cache, key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest_key]
                del self.access_count[oldest_key]
                
        if (time.time() - self.last_checkpoint) > self.checkpoint_interval:
            self.save_to_checkpoint('cache.checkpoint')
            self.last_checkpoint = time.time()
            
    def print_cache(self):
        print('Cache:')
        for key, value in self.cache.items():
            print(f"{key}")
        used_space = len(self.cache)
        remaining_space = self.max_size - used_space
        print(f"Cache size: {used_space}")
        print(f"Remaining space: {remaining_space}")


# In[7]:


cache = Cache()


# In[8]:


# get tweet counte per each user
def count_tweets_per_user():
    tweet_counts = {}
    cursor = tweets_collec.aggregate([
        {"$group": {"_id": "$User_Id", "count": {"$sum": 1}}}
    ])
    for user in cursor:
        tweet_counts[user['_id']] = user['count']
    return tweet_counts


# In[9]:


# write the results to a csv file to load it into mysql database
def write_tweets_to_csv(filename, tweets_dict):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['User_ID', 'Tweets_Count'])
        for user_id, count in tweets_dict.items():
            writer.writerow([str(user_id), count])


# In[10]:


tweets_dict = count_tweets_per_user()
write_tweets_to_csv('tweets_counts.csv', tweets_dict)


# In[11]:


# check if the search term starts with '@'
def UserSearch(search_term):
    
    if search_term.startswith('@'):
    # remove the '@' symbol from the search term
        search_term = search_term[1:]
        
        if cache.get(search_term):
            print("getting")
            results = cache.get(search_term)
            
        else:
            print("putting")
            # execute the query to search for user details based on username
            query = """
                SELECT * FROM users 
                WHERE name LIKE %s 
                ORDER BY followers_count DESC, tweets_count DESC, verified DESC
                LIMIT 5
                """
            mycursor.execute(query, ('%' + search_term + '%',))
            results = mycursor.fetchall()
            for i in range(0,len(results)):
                cache.put(results[i][1], results[i])

        return results


# In[12]:


def get_user_tweets(user_id):
    
    if cache.get(user_id):
        print("getting tweet")
        tweet_details = cache.get(user_id)
    
    else:
        print("putting tweet")
        
        user_tweets = list(tweets_collec.find({'User_Id': user_id}).sort([('created_at', -1)]).limit(3))
        tweet_details = []
        
        for tweet in user_tweets:
            tweet_details.append({
                'created_at': tweet['created_at'],
                'text': tweet['Text'],
                'hashtags': tweet['Hashtag'],
                'retweet_count': tweet['Retweet_Count'],
                'likes_count': tweet['Likes_Count']
            })
        
        cache.put(user_id, tweet_details)
    return tweet_details


# In[13]:


def UserPrint(results):
    for result in results:
        user_id = result[0]
        tweets_cache[user_id] = get_user_tweets(user_id)
        if result[3]==1:
            verified_status="✅"
        else:
            verified_status="❌"
            ()
        line1 = "Name: {} | Verified: {}".format(result[1], verified_status)
        # format the remaining fields in another line
        line2 = "Followers: {} | Tweets: {}".format(result[4], result[8])
        line3 = "Description : {}".format(result[9])
        line4="Location : {} | Creation Date:{}".format(result[7],result[6])
        
        # print both lines
        print(line1)
        print(line2)
        print(line3)
        print(line4)
        print("--------------------------------------------")


# In[15]:


search_term = input("Enter the search term: ")

start_sql = time.perf_counter()
results=UserSearch(search_term)
end_sql = time.perf_counter()

sql_time = end_sql - start_sql


start_mongo = time.perf_counter()
tweets_cache = {}
UserPrint(results[:3])
end_mongo = time.perf_counter()
mongo_time = end_mongo - start_mongo

    # check if there are more results
if len(results) > 3:
        # prompt the user to load more results
    load_more = input("Load more results? (yes/no) ")
    if load_more.lower().startswith('y'):
        UserPrint(results[3:5])
user_choice = int(input("Enter the number of the user whose tweets you want to see: "))

# Get the user_id of the selected user
user_id = results[user_choice-1][0]

# Display the tweets of the selected user

if user_id in tweets_cache:
    print(f"Tweets of {results[user_choice-1][1]}:")
    for tweet in tweets_cache[user_id]:
        print(tweet)
else:
    print("No tweets found for the selected user.")
    
print("Time for getting user info: ", sql_time)
print("Time for getting tweets info: ", mongo_time)


# In[16]:


def get_top_hashtags(search_string, limit=5):
    
    if search_string.startswith('#'):
        search_string = search_string[1:]
        
        hashtags = tweets_collec.aggregate([
        { "$match": { "Hashtag": { "$regex": search_string, "$options": "i" } } },
        { "$unwind": "$Hashtag" },
        { "$group": { "_id": "$Hashtag", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } },
        { "$limit": limit }
        ])
        
        hashtag_dict = {}
        for hashtag in hashtags:
            hashtag_dict[hashtag['_id']] = hashtag['count']
            
        return hashtag_dict


# In[17]:


def tweets_of_hashtag(hashtag):
    
    if cache.get('#' + hashtag):
        tweets = cache.get(hashtag)[0]
    else:
        tweets = list(tweets_collec.find({'Hashtag': hashtag}).sort('created_at', -1).limit(3))
        cache.put('#' + hashtag, tweets)
    
    return tweets


# In[19]:


def Hashtag_print(hashtags):
    print()
    print("Top 5 hashtags matching the search string: ")
    print()
    for k,v in hashtags.items():
        print("------------------------------------------")
        print("Hashtag: {} | Tweets Count: {}\n".format(k, v))
    
    for hashtag in hashtags.keys():
        temp_hashtag[hashtag] = tweets_of_hashtag(hashtag)


# In[20]:


# level 1 display
search_hashtag = input("Enter the hashtag: ")
hashtags = get_top_hashtags(search_hashtag)

temp_hashtag = {}

start_hashtag = time.perf_counter()
Hashtag_print(hashtags)
end_hashtag = time.perf_counter()
hashtag_time = end_hashtag - start_hashtag


print()
hashtag_choice = input("Enter the hashtag whose tweets you want to see: ")

if hashtag_choice in temp_hashtag:
    print()
    print(f"Tweets of {hashtag_choice}:")
    for tweet in temp_hashtag[hashtag_choice]:
        line_1 = "User: {} | Retweets: {} | Likes: {} | Created at: {}".format(tweet['User_Name'], tweet['Retweet_Count'], tweet['Likes_Count'], tweet['created_at'])
        line_2 = "Text: {}".format(tweet['Text'])
        
        print("----------------------------------------------------------------------------------")
        print()
        print(line_1)
        print(line_2)
        print("Hashtags: {}".format(tweet['Hashtag']))
else:
    print("No tweets found for the selected hashtag.")
    
print("Time for getting tweets info: ", hashtag_time)


# In[21]:


tweets_collec.create_index([("Text", "text")])


# In[22]:


def search_tweets(search_string):

    stop_words = set(stopwords.words('english'))
    search_words = search_string.split()
    if len(set(search_words) - stop_words) == 0:
        return "Error"
    
    search_string = '"' + search_string + '"'
    # Search for tweets matching the search string
    query = {'$text': {'$search': search_string}}
    projection = {'_id': 0, 'Text': 1, 'ext': 1, 'created_at': 1, 'Retweet_Count': 1, 'favorite_count': 1, 'Hashtags': 1}
    matching_tweets = list(tweets_collec.find(query).sort([('retweeted_status', 1), ('created_at', -1)]).limit(5))


    # Print number of matching tweets and return the results
    print(f"Number of matching tweets: {len(matching_tweets)}")
    return matching_tweets


# In[23]:


start_string = time.perf_counter()
results = search_tweets('death on')
end_string = time.perf_counter()
string_time = end_string - start_string



if (results=="Error"):
    print("Error: Please provide a non stop word")
else:
    for tweet in results:
        print(tweet)
        print("------------------")

print("Time for getting tweets info for a string: ", string_time)


# In[24]:


# Top 10 users with most followers, tweets
query = """select id,name,screen_name,verified,followers_count,friends_count,location,tweets_count,Description from mydatabase.users 
order by followers_count DESC,tweets_count DESC 
limit 10"""

mycursor.execute(query)
top_10_users = mycursor.fetchall()
top_10_users
#cache.put('top_10_users', top_10_users)


# In[25]:


get_top_10_users = cache.get('top_10_users')


# In[26]:


# # Top 10 Tweets with most a composite score of Retweets*0.6 + Likes*0.4
# def get_top_tweets():
#     tweets = tweets_collec.find().sort([("Retweet_Count", -1), ("Likes_Count", -1)]).limit(10)
#     top_tweets = []
#     for tweet in tweets:
#         score = tweet['Retweet_Count'] * 0.6 + tweet['Likes_Count'] * 0.4
#         tweet['score'] = score
#         top_tweets.append(tweet)
#     top_tweets = sorted(top_tweets, key=lambda x: x['score'], reverse=True)
#     return top_tweets

# top_10_tweets = get_top_tweets()
# cache.put('top_10_tweets', top_10_tweets)


# In[27]:


get_top_10_tweets = cache.get('top_10_tweets')


# In[28]:


# # Top 10 hashtags with are present in most tweets
# def get_top_hashtags(limit=10):
#     pipeline = [
#         {"$unwind": "$Hashtag"},
#         {"$group": {"_id": "$Hashtag", "count": {"$sum": 1}}},
#         {"$sort": {"count": -1}},
#         {"$limit": limit}
#     ]
#     top_hashtags = list(tweets_collec.aggregate(pipeline))
#     top_hashtags_dict = {}
#     for hashtag in top_hashtags:
#         top_hashtags_dict[hashtag['_id']] = hashtag['count']
#     return top_hashtags_dict

# top_10_hashtags = get_top_hashtags()
# cache.put('top_10_hashtags', top_10_hashtags)


# In[29]:


get_top_10_hashtags = cache.get('top_10_hashtags')


# In[30]:





# In[ ]:




