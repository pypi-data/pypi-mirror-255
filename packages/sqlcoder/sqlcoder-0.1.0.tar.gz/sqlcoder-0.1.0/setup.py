import os
from setuptools import find_packages, setup

extras = {
    "llama-cpp": ["llama-cpp-python"]
}

def package_files(directory):
    paths = []
    for path, directories, filenames in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths

# next_static_files = package_files("sqlcoder/static")
next_static_files = []

setup(
    name="sqlcoder",
    packages=find_packages(),
    package_data={"sqlcoder": next_static_files},
    version="0.1.0",
    description="SQLCoder is a large language model for converting text questions in SQL queries.",
    author="Defog, Inc",
    license="Apache-2",
    install_requires=[
        "requests>=2.28.2",
        "psycopg2-binary>=2.9.5",
        "prompt-toolkit>=3.0.38",
        "fastapi",
        "uvicorn",
    ],
    entry_points={
        "console_scripts": [
            "sqlcoder=sqlcoder.cli:main",
        ],
    },
    author_email="founders@defog.ai",
    url="https://github.com/defog-ai/sqlcoder",
    long_description="SQLCoder is a large language model for converting text questions in SQL queries.",
    long_description_content_type="text/markdown",
    extras_require=extras,
)