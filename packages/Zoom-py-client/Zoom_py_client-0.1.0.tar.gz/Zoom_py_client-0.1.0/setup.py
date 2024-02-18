from setuptools import setup, find_packages

setup(
    name='Zoom_py_client',
    version='0.1.0',
    packages=find_packages(),
    license='MIT',
    description='A python zoom client for generating links using python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Kaleb Abiy',
    author_email='kalebabiy2012@gmail.com',
    url='https://github.com/your_username/your_package',
    keywords=['Python', 'Zoom', 'Meeting', 'Link', 'Meeting Link'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        # Add more classifiers as needed
    ],
    python_requires='>=3.8',
    install_requires=[
        # Add any dependencies your package requires
    ],
)
