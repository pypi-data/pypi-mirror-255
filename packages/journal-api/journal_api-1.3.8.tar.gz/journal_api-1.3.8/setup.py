from setuptools import setup

setup(name='journal_api',
      version='1.3.8',

      author="q_HelloWorld",
      author_email="alexberxin@gmail.com",

      description='Simple wrapper for edu.gounn.ru api',
      packages=['journal_api'],

      requires=['aiohttp', 'beautifulsoup4'],

      zip_safe=False)
