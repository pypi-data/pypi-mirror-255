from setuptools import setup, find_packages

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()

with open('README.md', 'r') as read_me_file:
    description = read_me_file.read()

setup(
    name='resize_img',
    version='0.7',
    packages=find_packages(),
    install_requires=[
        requirements
    ],
    entry_points = {
        'console_scripts': [
            'resize-img = img_resizer.main:main'
        ]
    },
    long_description = description,
    long_description_content_type = 'text/markdown'
)

# v0.6 - Better exception handle and chanes to description 