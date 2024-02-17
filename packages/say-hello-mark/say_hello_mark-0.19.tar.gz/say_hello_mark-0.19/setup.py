from setuptools import setup, find_packages

setup(
  name="say_hello_mark",
  version="0.19",
  author="Mark Toledo",
  author_email="mark@onebyzero.ai",
  # url="www.google.com",
  packages=find_packages(),
  long_description="Test long description",
  long_description_content_type='text/markdown',
  install_requires=[

  ],
  entry_points={
    "console_scripts": [
      "say-hello-mark = say_hello_mark:hello" 
    ]
  }
)