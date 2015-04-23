import os
import flaskr
import requests
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

	def test_get_request(self):
		r = requests.get('http://localhost:5000/contacts/')
		assert 'contacts' in r.text

	def test_post_request(self):
		payload = {"name":"Putin","email":"putin@gmail.com","phone":"77777777"}
		r = requests.post('http://localhost:5000/contacts/', data=payload)
		assert r.status_code == requests.codes.ok

	def test_put_request(self):
		payload = {"name":"Putin","email":"putin@gmail.com","phone":"77777777"}
		r = requests.post('http://localhost:5000/contacts/', data=payload)
		payload = {"name":"Obama","email":"obama@gmail.com","phone":"55555555"}
		r = requests.put('http://localhost:5000/contacts/0', data=payload)
		assert r.status_code == requests.codes.ok

	def test_delete_request(self):
		payload = {"name":"Putin","email":"putin@gmail.com","phone":"77777777"}
		r = requests.post('http://localhost:5000/contacts/', data=payload)
		r = requests.delete('http://localhost:5000/contacts/0')
		assert "\"id\": 0" not in r.text
			
if __name__ == '__main__':
    unittest.main()