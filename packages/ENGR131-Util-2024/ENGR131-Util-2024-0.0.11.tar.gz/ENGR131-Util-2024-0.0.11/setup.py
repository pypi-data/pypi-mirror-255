import setuptools

setuptools.setup(
    name="ENGR131-Util-2024",
    version="0.0.11",
    author="Joshua C. Agar",
    description="Drexel Midterm Utility Functions",
    packages=["ENGR131_Util_2024"],
    install_requires=["cryptography", "drexel_jupyter_logger", "ipywidgets"],
)
