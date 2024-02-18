# inside pastebin_replace dir

"""
Package to replace a local file with a code from Pastebin.

You can use ``pbreplace(path, link)`` immediately after importing this package.
"""

PACKAGE_NAME = "pastebin_replace"

import os
import requests

class InvalidPath(Exception):
	def __init__(self, message):
		self.message = message
		super().__init__(self.message)

class InvalidLink(Exception):
	def __init__(self, message):
		self.message = message
		super().__init__(self.message)

class RequestsFails(Exception):
	def __init__(self, message):
		self.message = message
		super().__init__(self.message)

class PermissionDenied(Exception):
	def __init__(self, message):
		self.message = message
		super().__init__(self.message)

class WriteFailed(Exception):
	def __init__(self, message):
		self.message = message
		super().__init__(self.message)

def pbreplace(path : str, link : str, rename : str = ""):
	"""
	Replace the file provided with downloaded file from 

	Parameters:
	path (str): Absolute path of the file that would be replaced. The original file will be deleted.
	link (str): Pastebin link (URL) of the paste.
	rename (str): Optional. Rename the downloaded file (including the extension) to this string. When this is empty, uses the name of the replaced file.
	"""
	
	if not os.path.exists(path):
		raise InvalidPath("Path provided on pbreplace(-> path < -, link, rename) is invalid.")
	else:
		if os.path.isdir(path):
			raise InvalidPath("Path provided on pbreplace(-> path < -, link, rename) is a directory, not a file.")
		else:
			if not os.path.isfile(path):
				raise InvalidPath("Path provided on pbreplace(-> path < -, link, rename) is not a valid file.")

	if link.startswith("pastebin.com"):
		link += "https://"
	
	if not link.startswith("https://pastebin.com"):
		raise InvalidLink(f"Link {link} is not a valid Pastebin link.")
	else:
		splitted_link = link.split('/')
		if len(splitted_link) >= 4: # ['https:', '', 'pastebin.com', <randomwords>]
			if not splitted_link[3] == "raw":
				splitted_link.insert(3, 'raw')
				link = '/'.join(splitted_link)
		else:
			raise InvalidLink(f"Link {link} is not a valid Pastebin link.")

	response = requests.get(link)
	
	if response.status_code != 200: # fails
		raise RequestsFails(f"Download failed. Status code: {response.status_code}. Check the link or your internet connection.")
	else:
		if not os.access(path, os.W_OK):
			raise PermissionDenied("Cannot replace file. Not enough permission to remove the file on provided path.")
		else:
			os.remove(path)

			oldpath = ""
			if rename != "":
				oldpath = path
				path = os.path.join(os.path.dirname(path), rename)
				os.path.isvalid

			try:
				with open(path, 'wb') as f:
					f.write(response.content)
			except Exception as e:
				raise WriteFailed("Failed writing file to disk. Reason: " + str(e))

			print(f"File {path} replaced with the one downloaded from this Pastebin link: {link}")
			if rename != "":
				print("Downloaded file renamed to: " + rename)