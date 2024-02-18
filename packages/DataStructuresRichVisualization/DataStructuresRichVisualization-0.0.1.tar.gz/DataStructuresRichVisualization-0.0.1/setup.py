import setuptools

setuptools.setup(
    name="DataStructuresRichVisualization",
    version="0.0.1",
    author="Jackylee",
    author_email="jieli.work@qq.com",
    packages=setuptools.find_packages(exclude=["tests", "data"]),
    description="A Python package for data structures and rich visualization",
    long_description=open("README.md", encoding='utf-8').read()
)
