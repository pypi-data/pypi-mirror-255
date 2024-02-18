from setuptools import setup, find_packages

setup(
    name="tls_session",
    version="0.0.1",
    packages=['tls_client'],
    install_requires = [
        "requests==2.31.0"
    ],
    author="tls_session",
    description="tls_session"
)