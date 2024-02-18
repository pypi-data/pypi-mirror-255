from setuptools import find_packages, setup


def get_long_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="gemmail-python",
    version="1.0.15",
    description="A Gemmail (and Gembox) parser for misfin clients and servers",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Christian Lee Seibold",
    author_email="christian.seibold32@outlook.com",
    url="https://gitlab.com/clseibold/gemmail-python",
    project_urls={
        "GitHub Project": "https://gitlab.com/clseibold/gemmail-python",
        "Issue Tracker": "https://gitlab.com/clseibold/gemmail-python/-/issues",
    },
    packages=find_packages(
        include=["gemmail_python", "gemmail_python.*"],
    ),
    install_requires=[
        "requests==2.27.1",
    ],
    setup_requires=[
        "pytest-runner",
        "flake8==4.0.1",
    ],
    tests_require=[
        "pytest==7.1.2",
        "requests-mock==1.9.3",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "misfin",
        "gemini",
        "gembox",
        "gemtext",
        "gemmail",
        "mail",
        "email",
    ],
    license="BSD-3-Clause",
)