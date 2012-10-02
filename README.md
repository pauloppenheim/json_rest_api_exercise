JSON REST API exercise in Python using WSGI 
============================================================


Problem Description
------------------------------------------------------------

Create a simple REST JSON API that supports the following:

1) An Author resource, A Book resource
2) A book can have multiple authors
3) An author can have multiple books
4) Standard CRUD operations should work in typical RESTful fashion
5) A method that will return authors sorted by number of books published
6) Set up a test suite that will test the API

Author Model:
    name
    date of birth
    books

Book model:
    title
    publish date
    authors

Notes:

I dont care about how you back the data, you can keep it all in memory
or wherever you would prefer. Feel free to use any external libraries.
Please track your code using git or something similar. Email me a link
to the repository when you're done! If you have any questions, just make
your best guess at answering and note your assumptions with a code comment.
