from setuptools import setup, find_packages

setup(
    name="anyagent-ai",
    version="1.0.5",
    description="A standardized framework for building gRPC-based Telegram agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="AnyAgent Team",
    author_email="astexlab@gmail.com",
    url="https://anyagent.app",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'anyagent': ['proto/*.proto', 'proto/*.py'],
    },
    install_requires=[
        "grpcio>=1.68.0",
        "grpcio-tools>=1.68.0", 
        "protobuf>=5.28.2",
        "pydantic>=2.10.1",
        "aiohttp>=3.11.10",
        "requests>=2.31.0",
        "chatgpt-md-converter>=0.3.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'anyagent-init=anyagent.cli:init_agent',
            'anyagent-serve=anyagent.cli:serve_agent',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    keywords="telegram, agent, grpc, framework, chatbot, ai",
) 