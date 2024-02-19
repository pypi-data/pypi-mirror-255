from setuptools import setup, find_packages

# Read the contents of your README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='password_generator2024',  # This can stay with 
    
    version='0.6',  # Increment the version
    packages=find_packages(),
    description='Simple Python Password Generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Pierre',
    author_email='pierre@gode.one',
    url='https://github.com/PierreGode/password_generator',
    install_requires=[],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    # Add other arguments to setup() as needed
)
