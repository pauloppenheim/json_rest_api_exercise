#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_author

import unittest
import json

import webtest


"""
Some data from books nearby, see book_author.py for info on data model

Edward R. Tufte/1942
    The Visual Display of Quantitative Information/1983
    Envisioning Information/1990
    The Visual Display of Quantitative Information/2001

Plato/-424
    The Republic/-360

Computer Graphics: Principles and Practice in C (2nd Edition)/1995
    James D. Foley/1942
    Andries van Dam/1938
    Steven K. Feiner - no year, drop ;_;
    John F. Hughes - no year, drop

"""



class TestBookAuthorAcceptance(unittest.TestCase):
    
    def setUp(self):
        book_author.storage.reset_storage()
        self.app = webtest.TestApp(book_author.application)
        self.ctype = "application/json"
    
    
    def test_sanity(self):
        #Quite simple existence test - set expected WSGI things.
        # root returns 404
        res = self.app.get('/', status=404)
        self.assertNotEqual(res, None)
        self.assertTrue(len(res.headerlist) > 0)
    
    
    def test_url_author_get(self):
        #Test GET an entity url - /entity/idstr/date/
        # empty DB still - should be 404
        path = '/author/Edward R. Tufte/1942'
        res = self.app.get(path, status=404)
        self.assertTrue(len(res.headerlist) > 0)
        self.assertNotEqual(res.body, '')
        self.assertEqual(res.json, [])
    
    
    def test_url_author_put(self):
        # Test PUT an entity url - /entity/idstr/date/
        d = [{"title": "The Visual Display of Quantitative Information", "pubdate": 1983}]
        path = '/author/Edward R. Tufte/1942'
        s = json.dumps(d)
        res = self.app.put(path, s, content_type=self.ctype, status=201)
        self.assertTrue(len(res.headerlist) > 0)
        self.assertNotEqual(res.body, '')
        self.assertEqual(res.json, d)
    
    
    def test_url_author_put_get(self):
        # PUT, then make sure GET matches
        d = [{"title": "The Visual Display of Quantitative Information", "pubdate": 1983}]
        path = '/author/Edward R. Tufte/1942'
        s = json.dumps(d)
        res = self.app.put(path, s, content_type=self.ctype, status=201)
        res = self.app.get(path)
        self.assertTrue(len(res.headerlist) > 0)
        self.assertNotEqual(res.body, '')
        self.assertEqual(res.json, d)
    
    
    def test_url_author_put_idempotence(self):
        # PUT, then PUT again, make sure no change
        d = [{"title": "The Visual Display of Quantitative Information", "pubdate": 1983}]
        path = '/author/Edward R. Tufte/1942'
        s = json.dumps(d)
        res = self.app.put(path, s, content_type=self.ctype, status=201)
        res = self.app.put(path, s, content_type=self.ctype, status=200)
        self.assertTrue(len(res.headerlist) > 0)
        self.assertNotEqual(res.body, '')
        self.assertEqual(res.json, d)
    
    
    def test_url_author_put_two(self):
        # PUT base, then PUT additional row, make sure both returned
        d1 = [{"title": "The Visual Display of Quantitative Information", "pubdate": 1983}]
        d2 = [{"title": "Envisioning Information", "pubdate": 1990}]
        path = '/author/Edward R. Tufte/1942'
        s1 = json.dumps(d1)
        s2 = json.dumps(d2)
        res1 = self.app.put(path, s1, content_type=self.ctype, status=201)
        res2 = self.app.put(path, s2, content_type=self.ctype, status=200)
        self.assertEqual(res1.json, d1)
        self.assertTrue(d2[0] in res2.json)
        self.assertTrue(d1[0] in res2.json)
        res3 = self.app.get(path)
        self.assertTrue(d2[0] in res3.json)
        self.assertTrue(d1[0] in res3.json)
    
    
    def test_url_author_delete(self):
        # PUT two, DELETE one, GET to verify deletion
        d1 = [{"title": "The Visual Display of Quantitative Information", "pubdate": 1983}]
        d2 = [{"title": "Envisioning Information", "pubdate": 1990}]
        author = '/author/Edward R. Tufte/1942'
        book = '/book/Envisioning Information/1990'
        s1 = json.dumps(d1)
        s2 = json.dumps(d2)
        res = self.app.put(author, s1, content_type=self.ctype, status=201)
        res = self.app.put(author, s2, content_type=self.ctype, status=200)
        res = self.app.delete(book, status=200)
        self.assertTrue(len(res.headerlist) > 0)
        self.assertNotEqual(res.body, '')
        self.assertEqual(res.json, d1)
        res = self.app.get(author)
        self.assertTrue(d2[0] not in res.json)
        self.assertTrue(d1[0] in res.json)




class TestBookAuthorInternals(unittest.TestCase):
    
    def setUp(self):
        self.store = book_author.BookAuthorMemStorage()
    
    
    def test_author_create(self):
        bi = [{"title": "b1", "pubdate": 1}]
        created, updated = self.store.author_create("a1", 1, bi)
        self.assertTrue(len(self.store.authors) > 0)
        self.assertTrue(created)
        self.assertTrue(updated)
        # is author created?
        b = self.store.authors.values()[0].pop()
        self.assertEqual(b[0], "b1")
        self.assertEqual(b[1], 1)
        # is symmetric book created?
        a = self.store.books.values()[0].pop()
        self.assertEqual(a[0], "a1")
        self.assertEqual(a[1], 1)
    
    
    def test_book_create(self):
        ai = [{"name": "a1", "dob": 1}]
        created, updated = self.store.book_create("b1", 1, ai)
        self.assertTrue(len(self.store.books) > 0)
        self.assertTrue(created)
        self.assertTrue(updated)
        # is book created?
        a = self.store.books.values()[0].pop()
        self.assertEqual(a[0], "a1")
        self.assertEqual(a[1], 1)
        # is symmetric author created?
        b = self.store.authors.values()[0].pop()
        self.assertEqual(b[0], "b1")
        self.assertEqual(b[1], 1)
    
    
    def test_author_read(self):
        b = self.store.author_read("a1", 1)
        self.assertEqual(len(b), 0)
    
    
    def test_author_create_read(self):
        bi = [{"title": "b1", "pubdate": 1}]
        created, updated = self.store.author_create("a1", 1, bi)
        # is author created? Gettable?
        b = self.store.author_read("a1", 1).pop()
        self.assertEqual(b[0], "b1")
        self.assertEqual(b[1], 1)
        # is symmetric book created? Gettable?
        a = self.store.book_read("b1", 1).pop()
        self.assertEqual(a[0], "a1")
        self.assertEqual(a[1], 1)
    
    
    def test_author_delete(self):
        deleted = self.store.author_delete("a1", 1)
        self.assertEqual(len(self.store.authors), 0)
        self.assertFalse(deleted)
    
    
    def test_author_create_delete(self):
        bi = [{"title": "b1", "pubdate": 1}]
        created, updated = self.store.author_create("a1", 1, bi)
        # assume author and opposite book created, as above
        deleted = self.store.author_delete("a1", 1)
        # is author deleted?
        b = self.store.author_read("a1", 1)
        self.assertEqual(len(b), 0)
        # is symmetric book deleted?
        a = self.store.book_read("b1", 1)
        self.assertEqual(len(a), 0)
    
    
    def test_author_create_no_books_fails(self):
        created, updated = self.store.author_create("a1", 1, [])
        self.assertEqual(len(self.store.authors), 0)
        self.assertFalse(created)
        self.assertFalse(updated)






if __name__ == '__main__':
    unittest.main()


