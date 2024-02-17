import setuptools

setuptools.setup(
    name="python-to-1c",
    version="0.0.4",
    author="Andrey Galkin",
    author_email="justscoundrel@yandex.ru",
    description="API for odata 1C",
    long_description="API for odata 1C 8",
    long_description_content_type="text/markdown",
    url="https://github.com/kmvit/odatapython",
    packages=['python1c'],
    install_requires=[
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
