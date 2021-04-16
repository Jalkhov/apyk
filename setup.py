from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="APyK",
    version="0.0.1",
    description="APyK is a program with which you will be able to backup your applications from your computer.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pedro Torcatt",
    author_email="pedrotorcattsoto@gmail.com",
    url="https://github.com/Jalkhov/apyk",
    license="MIT",
    keywords="adb android apk backup apps",
    packages=['apyk'],
    include_package_data=True,
    install_requires=[
        'PyQt5',
        'google_play_scraper'
    ],
    entry_points={
        'console_scripts': [
            'apyk=apyk.win_main:main',
        ],
    },
    classifiers=[
        "Topic :: Utilities",
        "Environment :: Win32 (MS Windows)",
        "Topic :: System :: Archiving :: Backup",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 5 - Production/Stable",
    ],
)
