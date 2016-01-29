from setuptools import setup

setup(
    name="swailing",
    version="0.1.2",
    packages=['swailing'],
    author="Wes Chow",
    author_email="wes@chartbeat.com",
    description=("Logging library for apps that produce debilitating amounts of log output."),
    license="Apache",
    keywords="logging",
    url="https://github.com/chartbeat-labs/swailing",
    long_description="""
An opinionated logging library for applications that produce a debilitating amount of log output.

Swailing uses the token bucket algorithm and provides facilities for
PostgreSQL style error logs. See
https://github.com/chartbeat-labs/swailing for more details.
""",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Topic :: System :: Logging",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
    ],
)
