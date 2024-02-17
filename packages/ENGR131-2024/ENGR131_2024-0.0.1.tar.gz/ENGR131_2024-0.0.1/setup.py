import setuptools

# Open and read the contents of the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="ENGR131_2024",
    version="0.0.1",
    author="Joshua C. Agar",
    description="ENGR131_2024 package",
    packages=["ENGR131_2024"],
    install_requires=requirements,  # Use the list of requirements here
)
