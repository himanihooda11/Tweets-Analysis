# Twitter Search Application Team-2--ADBMS




## Course
16:954:694:01 - Advanced Database Management System

## Team Members
- Sai Adarsh Kasula ([SK2837))
- Krit Shreeram Gupta ([KSG124]))
- Himani Hooda ([HH660))
- Vanshika Ram Gurbani ([VG460])

## Department
Department of Statistics & Data Science, Rutgers University, New Brunswick, NJ

## Supervised by
Prof. Ajita John

## Note
Presentation to Cohort is completed (Cohort -1)

## 1. Introduction
Twitter is one of the most popular social media platforms globally, with millions of active users posting tweets daily. The Twitter search application harnesses the power of Twitter's vast database to provide users with a simple yet powerful tool to find relevant information quickly. This version of the Twitter search application allows users to search for tweets based on username, hashtag, or part of a tweet, with further drill-downs available for each search case.

## 2. Dataset & Exploratory Analysis (By Vanshika Gurbani)
- Approximately 134k documents were present in the JSON files.
- All tweets belonged to April 2020 (Covid period).
- Net sentiment was found to be 0.02, indicating an overall negative skewness.
- The dataset contained approximately 90k unique users.
- Top 10 most common languages used in tweets were analyzed.
- Top 10 most mentioned users in the tweets.

## 3. System Architecture
- The system architecture establishes the overall flow of the application, including key components and their coordination.
- Final architecture includes a Flask-based user interface, core functionalities for searching by User, Hashtag, and Search String/Term, and caching system for efficient search performance.

## 4. Data Storage
### 4.1. User Data Storage (By Krit S Gupta)
- User data was extracted and transferred using Python to a MySQL database.
- MySQL was chosen for its reliability, scalability, and community support.
- 90k unique users were identified and stored in a MySQL database.

### 4.2. Tweets Data Storage (By Krit S Gupta)
- Tweets data was stored in MongoDB due to its dynamic structure and suitability for storing tweets.
- About 112,000 unique tweets and retweets were extracted and stored in MongoDB.
- Indexes were created on "User_Id" and "Text" fields for better query performance.

## 5. Search Implementation( By Sai Adarsh Kasula)
- Core functionalities include searching by User, Hashtag, and Search String/Term.
- Trending Searches (Users, Tweets, Hashtags) feature is available.
- Efficient caching mechanism is implemented to improve search performance.

## 6. Caching (By Himani Hooda)
- Caching is implemented using a Python dictionary to store user information and tweets.
- Cache class provides efficient caching mechanisms with methods for managing the cache.
- Caching significantly improves system performance by reducing response time and database load.

## 7. Search Application Design (By Sai Adarsh Kasula)
- User interface is built using CSS styling, HTML, and Flask framework.
- Multiple pages are created for various search functionalities.
- Drill-downs are available for each search query.

## 8. Results
### 8.1. User Searching
- Users can search for usernames and view their recent tweets.

### 8.2. Hashtag Searching
- Users can search for hashtags and view top tweets containing the hashtag.

### 8.3. String Searching
- Users can search for part of a tweet and view relevant tweets.

### 8.4. Trending Searches
- Trending Users, Tweets, and Hashtags are displayed based on popularity.

### 8.5. Caching
- Caching significantly improves data retrieval performance.

## 9. Conclusion
- The project offers insights into data ingestion, storage, and retrieval using MySQL, MongoDB, and Flask.
- Caching and indexing are essential for optimizing query performance and improving system efficiency.
- Overall, the project demonstrates the importance of database design and optimization in building efficient applications.

