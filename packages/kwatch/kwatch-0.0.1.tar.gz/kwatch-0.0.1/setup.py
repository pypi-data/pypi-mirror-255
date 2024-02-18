from setuptools import setup

setup(
    name='kwatch',
    version='0.0.1',
    description='Python client for the KWatch.io webhooks',
    long_description="KWatch.io allows you to receive instants alerts when specific keywords appear on social media like Reddit, Twitter, and Hacker News. This package allows you to interact with the KWatch.io webhooks.",
    packages=['kwatch'],
    author='Arthur Delerue',
    author_email='arthur@kwatch.io',
    license='MIT',
    keywords=['webhooks','reddit','twitter','hackernews'],
    url='https://kwatch.io'
)
