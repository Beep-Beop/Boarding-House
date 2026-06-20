from setuptools import setup

setup(
    name="CTkScrollableDropdown",
    version="1.2",
    packages=["CTkScrollableDropdown"],
    package_dir={"CTkScrollableDropdown": "."},
    py_modules=["ctk_scrollable_dropdown", "ctk_scrollable_dropdown_frame"],
    install_requires=["customtkinter"],
)
