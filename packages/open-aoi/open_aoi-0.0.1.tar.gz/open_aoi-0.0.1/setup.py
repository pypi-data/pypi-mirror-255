from setuptools import setup, find_packages

setup(
    name="open_aoi",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "opencv-python",
        "nicegui",
        "roslibpy",
        "sqlalchemy",
        "pymysql",
        "cryptography",
        "bcrypt",
    ],
)


import os
from glob import glob
from setuptools import setup

package_name = "open_aoi"

setup(
    name=package_name,
    version="0.0.1",
    # Packages to export
    packages=[package_name],
    # Files we want to install, specifically launch files
    data_files=[
        # Install marker file in the package index
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        # Include our package.xml file
        (os.path.join("share", package_name), ["package.xml"]),
        # Include all launch files.
        (
            os.path.join("share", package_name, "launch"),
            glob(os.path.join("launch", "*.launch.py")),
        ),
    ],
    # This is important as well
    install_requires=["setuptools"],
    zip_safe=True,
    author="Cherniaev Egor",
    author_email="chrnyaevek@gmail.com",
    maintainer="Cherniaev Egor",
    maintainer_email="chrnyaevek@gmail.com",
    keywords=["automated optical inspection", "pcb", "computer vision"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: MIT",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    description="Support package for Open AOI system.",
)
