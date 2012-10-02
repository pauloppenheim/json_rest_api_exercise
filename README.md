JSON REST API exercise in Python using WSGI 
============================================================


Problem Description
------------------------------------------------------------

Create a simple REST JSON API that supports the following:

1. An Author resource, A Book resource
2. A book can have multiple authors
3. An author can have multiple books
4. Standard CRUD operations should work in typical RESTful fashion
5. A method that will return authors sorted by number of books published
6. Set up a test suite that will test the API


Author Model:

    * name
    * date of birth
    * books


Book model:

    * title
    * publish date
    * authors


Notes:

I dont care about how you back the data, you can keep it all in memory
or wherever you would prefer. Feel free to use any external libraries.
Please track your code using git or something similar. Email me a link
to the repository when you're done! If you have any questions, just make
your best guess at answering and note your assumptions with a code comment.



Overly Short Example
------------------------------------------------------------

Terminal 1:

	$ python book_author.py 127.0.0.1 8080
	Serving on port 8080...
	using wsgiref

Terminal 2:

	$ curl -v 'http://localhost:8080/query/author_by_books'
	$ echo '[{"title": "The Visual Display of Quantitative Information", "pubdate": "1983"}]' > bk.json
	$ curl -v -T bk.json 'http://localhost:8080/author/Edward%20R.%20Tufte/1942'

ahh, forgot the content-type!

	$ curl -v -H "Content-Type: application/json" -T bk.json 'http://localhost:8080/author/Edward%20R.%20Tufte/1942'
	$ curl -v -H "Content-Type: application/json" -d '[{"title": "Envisioning Information", "pubdate": 1990}]' 'http://localhost:8080/author/Edward%20R.%20Tufte/1942'
	$ curl -v 'http://localhost:8080/query/author_by_books'
	$ curl -v -H "Content-Type: application/json" -d '[{"title": "The Republic", "pubdate": -360}]' 'http://localhost:8080/author/Plato/-424'
	$ curl -v 'http://localhost:8080/query/author_by_books'
	$ curl -v -H "Content-Type: application/json" -d '[{"name": "James D. Foley", "dob": 1942},{"name": "Andries van Dam", "dob": 1938}]' 'http://localhost:8080/book/Computer%20Graphics%3A%20Principles%20and%20Practice%20in%20C%20%282nd%20Edition%29/1995'
	$ curl -v 'http://localhost:8080/query/author_by_books'
	$ curl -v -X "DELETE" 'http://localhost:8080/author/Edward%20R.%20Tufte/1942'
	$ curl -v 'http://localhost:8080/query/author_by_books'
	$ curl -v 'http://localhost:8080/query/book_by_authors'

And that's the API. (You can hit ctrl-c in Terminal 1 now.)


