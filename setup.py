import setuptools

pkg_name="spikeforest"

setuptools.setup(
    name=pkg_name,
    version="0.4.0",
    author="Jeremy Magland",
    author_email="jmagland@flatironinstitute.org",
    description="",
    url="https://github.com/magland/spikeforest",
    packages=setuptools.find_packages(),
    install_requires=[
        'pybind11',
        'ml_ms4alg',
        'numpy',
        'matplotlib',
        'spikeextractors',
        'spikewidgets',
        'spiketoolkit',
        'kbucket',
        'pillow',
        'mlprocessors',
        'pandas',
        'vdomr'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    )
)
