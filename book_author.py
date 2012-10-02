#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
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

"""


"""
Author      Book           Entity
    name        title          idstr    --+--> primary key composite
    dob         pubdate        date     -/
    books       authors        rels     -----> foreign key list

Since both Author and Book effectively have the same data model, I refer to
both with the Entity model above.

Data design decisions, whether schema constraints or distributed storage
planning, require a business case to evaluate. I've used a combination of
common-sense about the publishing industry and development complexity.

* Entities require both an idstr and date, which uniquely identify that
    entity. (No two authors may have the same name and birthday; the name
    will need to be modified for disambiguation before entry.)
* Relations are required for existence. No books without authors, no authors
    without books.
* Surrogate keys offend not only my design sensibilities, but some of the
    premise of REST (ie, that a representation of an entity is enough to
    re-create it) so the (idstr, date) pair itself is the key instead of an
    int or UUID.
* Dates will be represented by years. The first few pages of a book typically
    has filing information, including the author's birth year, but only
    typically the year. Similarly, some books only have year of publication.
    This will be an integer, positive or negative, in the Gregorian calendar,
    with negative corresponding to BC. (There is no AD year 0.)
* Authors without birth years cannot be added. As such, if they are listed
    on the cover but not in the filing information on the inside of the
    book with years, they will be removed in this system.
* Similarly, books without publish years cannot be added.
* Author names and book titles are not normalized. "Edward Tufte" and
    "Edward R. Tufte" would be considered different; it is up to the user
    to use the correct key.


URL: /entity/idstr/date/

PUT - (idempotent) make sure the entity keyed by the URL exists with the
    relations included in a JSON body. (As stated above, no relations, no
    entity)
    ie: PUT /author/Edward R. Tufte/1942
    with content-type "application/json"
    with HTTP body:
    [
        {"title": "The Visual Display of Quantitative Information",
        "pubdate": 1983}
    ]
GET - (nullipotent) list the relations that entity has (with links to them)
    ie: GET /author/Edward R. Tufte/1942
    returns:
    [
        {"title": "The Visual Display of Quantitative Information",
        "pubdate": 1983},
        {"title": "Envisioning Information", "pubdate": 1990}
    ]
DELETE - (idempotent) make sure the entity keyed by the URL does *not* exist
POST - (non-idempotent) add the relations specified in the JSON body to the
    keyed entity. Essentially the same as a PUT.


URL: /query/entity/order_by_prolific

GET - list the entities sorted by the number of relations each has.

"""


import wsgiref.util
import cgi
import json


# ------------------------------------------------------------
# ------------------------------------------------------------
# HTTP Interface
# ------------------------------------------------------------
# ------------------------------------------------------------

class BookAuthor(object):
    
    def __init__(self):
        self.storage = BookAuthorMemStorage()
    
    
    def __call__(self, environ, start_response):
        path = []
        # shift_path_info is destructive, pass it a copy
        pathenv = {'PATH_INFO': environ.get('PATH_INFO')}
        p = wsgiref.util.shift_path_info(pathenv)
        while p is not None:
            path.append(p)
            p = wsgiref.util.shift_path_info(pathenv)
        
        entity, idstr, date = None, None, None
        if len(path) > 0:
            entity = path[0]
        if len(path) > 1:
            idstr = path[1]
        if len(path) > 2:
            date = path[2]
        
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        in_rels = []
        if 0 < form.length:
            in_rels = json.loads(form.value)
        
        created, updated, deleted = False, False, False
        request_method = environ.get("REQUEST_METHOD", "")
        status = '200 OK'
        rels = []
        entities = ['author', 'book']
        
        # dispatch
        if (entity is not None and
                idstr is not None and
                date is not None and
                entity in entities):
            if "author" == entity:
                if "PUT" == request_method or "POST" == request_method:
                    created, updated = self.storage.author_create(idstr, date, in_rels)
                    rels = self.storage.author_read_items(idstr, date)
                elif "GET" == request_method:
                    rels = self.storage.author_read_items(idstr, date)
                elif "DELETE" == request_method:
                    rels = self.storage.author_read_items(idstr, date)
                    deleted = self.storage.author_delete(idstr, date)
            elif "book" == entity:
                if "PUT" == request_method or "POST" == request_method:
                    created, updated = self.storage.book_create(idstr, date, in_rels)
                    rels = self.storage.book_read_items(idstr, date)
                elif "GET" == request_method:
                    rels = self.storage.book_read_items(idstr, date)
                elif "DELETE" == request_method:
                    rels = self.storage.book_read_items(idstr, date)
                    deleted = self.storage.book_delete(idstr, date)
        else:
            status  = '404 Not Found'
        
        # this needs to be a hint more complicated...
        if 0 == len(rels):
            status = '404 Not Found'
        
        if created:
            status = '201 Created'
        
        headers = [('Content-type', 'application/json')]
        start_response(status, headers)
        r_str = json.dumps(
            rels,
            sort_keys=True,
            indent=4
        )
        # wsgi: return iterable
        return [r_str]



# ------------------------------------------------------------
# ------------------------------------------------------------
# Data Model
# ------------------------------------------------------------
# ------------------------------------------------------------


def entity_create(idstr, date, additional_rels, entities, entities_opposite):
    # a = entities.get((str(idstr), int(date)), set())
    # have to use non-idiomatic code to track if created for HTTP status
    id_key = (str(idstr), int(date))
    if len(additional_rels) < 1:
        return (False, False)
    id_rels = set()
    created = True
    updated = False
    if entities.has_key(id_key):
        id_rels = entities[id_key]
        created = False
    for opposite_id in additional_rels:
        opposite_id_key = (str(opposite_id[0]), int(opposite_id[1]))
        if not opposite_id_key in id_rels:
            id_rels.add(opposite_id_key)
            updated = True
            # add linkback to the opposite entity
            inverse_rels = entities_opposite.get(opposite_id_key, set())
            inverse_rels.add(id_key)
            entities_opposite[opposite_id_key] = inverse_rels
    entities[id_key] = id_rels
    return (created, updated)


def entity_read(idstr, date, entities):
    return entities.get((str(idstr), int(date)), set())


def entity_delete(idstr, date, entities, entities_opposite):
    # a = entities.get((str(idstr), int(date)), set())
    # have to use non-idiomatic code to track if created for HTTP status
    id_key = (str(idstr), int(date))
    if not entities.has_key(id_key):
        return False
    id_rels = entities[id_key]
    
    # delete id_key's entry in opposite entities
    for opposite_id in id_rels:
        if entities_opposite.has_key(opposite_id):
            inverse_rels = entities_opposite[opposite_id]
            inverse_rels.discard(id_key)
            if 0 == len(inverse_rels):
                del entities_opposite[opposite_id]
            else:
                entities_opposite[opposite_id] = inverse_rels
    
    del entities[id_key]
    return True


def entity_by_rels(entities):
    a = map(lambda x: (x, len(entities[x])), entities.iterkeys())
    ent_cmp = lambda a,b: cmp(a[1], b[1])
    a.sort(ent_cmp)
    a.reverse()
    return a



class BookAuthorMemStorage(object):
    def __init__(self):
        self.books = {}
        self.authors = {}
    
    def author_create(self, author, dob, bookset):
        rels = []
        for d in bookset:
            rels.append( (d['title'], d['pubdate']) )
        return entity_create(author, dob, rels, self.authors, self.books)
    
    def book_create(self, title, pubdate, authorset):
        rels = []
        for d in authorset:
            rels.append( (d['name'], d['dob']) )
        return entity_create(title, pubdate, rels, self.books, self.authors)
    
    
    def author_read(self, author, dob):
        return entity_read(author, dob, self.authors)
    
    def book_read(self, title, pubdate):
        return entity_read(title, pubdate, self.books)
    
    def author_read_items(self, author, dob):
        s = entity_read(author, dob, self.authors)
        # unpack set of tuples
        a = []
        for i in s:
            a.append({'title': i[0], 'pubdate': i[1]})
        return a
    
    def book_read_items(self, title, pubdate):
        s = entity_read(title, pubdate, self.books)
        # unpack set of tuples
        a = []
        for i in s:
            a.append({'name': i[0], 'dob': i[1]})
        return a
    
    
    def author_delete(self, author, dob):
        return entity_delete(author, dob, self.authors, self.books)
    
    def book_delete(self, title, pubdate):
        return entity_delete(title, pubdate, self.books, self.authors)
    
    
    def author_by_books(self):
        return entity_by_rels(self.authors)
    
    def book_by_authors(self):
        return entity_by_rels(self.books)





