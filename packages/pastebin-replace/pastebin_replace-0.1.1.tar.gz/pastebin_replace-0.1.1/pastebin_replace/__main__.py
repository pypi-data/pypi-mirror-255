#!/usr/bin/env python

import click
from . import pbreplace

@click.command()
@click.argument('path', type=str)
@click.argument('link', type=str)
@click.argument('rename', type=str, default="", required=False)
def main(path, link, rename):
	"""
	Replace the file provided with downloaded file from 

	Parameters:
	path (str): Absolute path of the file that would be replaced. The original file will be deleted.
	link (str): Pastebin link (URL) of the paste.
	rename (str): Optional. Rename the downloaded file (including the extension) to this string. When this is empty, uses the name of the replaced file.
	"""
	
	if not path or not link:
		print("Path and link required for the command. See `pbreplace --help`.")
		return

	pbreplace(path, link, rename)

if __name__ == '__main__':
	main()