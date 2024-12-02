// 1. A basic search query on an attribute value
// Find all books with the language set to "en"
db.books.find({ "language": "en" });

// 2. A query that provides some aggregate data (i.e., number of entities satisfying a criteria)
// Find the total number of books per genre
db.books.aggregate([
    { $unwind: "$genres" },  // Decompose genres array
    { $group: { _id: "$genres.name", count: { $sum: 1 } } }  // Group by genre and count
]);

// 3. Find top n entities satisfying a criteria, sorted by an attribute
// Find the top 5 books with the most user ratings
db.books.find(
    { "ratings_count": { $ne: null } },  // Exclude books without ratings
    { "title": 1, "ratings_count": 1 }  // Project title and ratings count
).sort({ "ratings_count": -1 }).limit(5);

// 4. Simulate a relational group by query in NoSQL (aggregate per category)
// Find the average page count and total books grouped by language
db.books.aggregate([
    {
        $group: {
            _id: "$language",  // Group by language
            total_books: { $sum: 1 },  // Count total books per language
            avg_page_count: { $avg: "$page_count" }  // Calculate average page count
        }
    },
    {
        $sort: { total_books: -1 }  // Sort by total books in descending order
    }
]);

// 5. Build the appropriate indexes for previous queries, report the index creation statement
// and the query execution time before and after you create the index
// Create an index on the "language" field
db.books.createIndex({ "language": 1 });

// Measure query execution time before and after creating the index
db.books.find({ "language": "en" }).explain("executionStats");

// 6. Demonstrate a full-text search. Show the performance improvement by using indexes.
// Create a text index on the "title" field
db.books.createIndex(
    { "title": "text" },
    { "default_language": "en" }  // Specify default language as English
);

// Test the text index with a search query
db.books.find({ $text: { $search: "adventure" } });
