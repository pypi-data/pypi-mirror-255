from setuptools import setup, find_packages


requirements =[
        "rpaframework==28.2.0",
        "ta-bitwarden-cli==0.11.0",
        "boto3==1.26.129",
        "thoughtful==3.0.1",
        "python-docx==0.8.11",
        "retry==0.9.2",
        "pre-commit==2.17.0",
        "pandas==2.1.3",
        "pillow==10.2.0",
        "Office365-REST-Python-Client==2.5.2",
        "setuptools>=65.5.1",
        "google-api-python-client==2.108.0",
        "google-auth-oauthlib==1.1.0",
        "google-auth-httplib2==0.1.1",
        "urllib3==1.26.15",
        "ta-sites==0.4.14",
        "cryptography>=41.0.0",
        "openpyxl==3.0.10",
        "numpy==1.26.1",
        "requests==2.31.0"
    ]

setup(
    name="thoughtful-common-packages",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="The package contains all frequently used packages in Thoughtful",
    keywords="thoughtful-common-packages",
    url="https://www.thoughtful.ai/",
    version="0.0.9",
)
