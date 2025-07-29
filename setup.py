from setuptools import setup, find_packages

setup(
    name="tapered-capsule",
    version="1.0.0",
    author="Capsule Generation Team",
    description="Tapered capsule generation system for glTF2 skinned mesh skeletons",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chibifire/tapered_capsule_with_keypoint_detection",
    py_modules=["tapered_capsule"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "trimesh>=3.9.0",
        "minizinc>=0.10.0",
    ],
    entry_points={
        "console_scripts": [
            "tapered-capsule=tapered_capsule:main",
        ],
    },
)
