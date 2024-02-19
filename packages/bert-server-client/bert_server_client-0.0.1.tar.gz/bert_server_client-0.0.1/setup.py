from setuptools import setup, find_packages

setup(
    name="bert_server_client",
    version="0.0.1",
    packages=find_packages(),
    package_data={'bert_server_client': ['schema/*']},
    author="Anil Aydiner",
    author_email="a.aydiner@qimia.de",
    description="A ZMQ client interface for Bert server",
    long_description="A ZMQ client interface for Bert server",
    url="https://gitlab.com/qimiaio/qimia-ai-dev/bert-server-client",
    python_requires=">=3.11",
    install_requires=[
        "pyzmq>=25.1.1",
        "msgpack>=1.0.7",
        "dacite>=1.8.1"
    ],
    extras_require={
        "tests": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.2",
            "polyfactory>=2.5.0",
        ]
    }
)
