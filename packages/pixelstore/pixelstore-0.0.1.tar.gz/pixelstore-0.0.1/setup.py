from setuptools import setup,find_packages


setup(
    name="pixelstore",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        #add packages here
        "charset-normalizer>=3.3.2",
        "ffmpeg-python>=0.2.0",
        "future>=0.18.3",
        "idna>=3.6",
        "pillow>=10.2.0",
        "python-dotenv>=1.0.1",
    ],
)
