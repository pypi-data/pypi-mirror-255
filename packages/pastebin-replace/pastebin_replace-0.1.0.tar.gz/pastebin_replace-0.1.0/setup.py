from setuptools import setup, find_packages

def readme():
    with open('Readme.md') as f:
        return f.read()

setup(
    name = 'pastebin_replace',
    version = '0.1.0',
    description = 'Replace local files with code from a pastebin link',
    long_description = readme(),
    long_description_content_type='text/markdown',
    keywords = 'pastebin file python code productivity development dev shortcut download',
    url = 'https://github.com/etherealxx/pastebin-replace',
    author = 'Etherealxx',
    author_email = 'gwathon3@gmail.com',
    license = 'MIT',
    packages = find_packages(),
    zip_safe = False,
    install_requires = [
        'requests'
    ])