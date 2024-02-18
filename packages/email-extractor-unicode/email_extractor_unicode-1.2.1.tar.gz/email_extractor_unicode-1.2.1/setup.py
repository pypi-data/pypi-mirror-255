from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

with open('README.rst', encoding='utf-8') as readme_file:
    readme_content = readme_file.read()

with open('LICENSE.rst', encoding='utf-8') as license_file:
    license_content = license_file.read()


setup(
    name='email_extractor_unicode',
    version='1.2.1',
    description='Extract Emails Using Phone Number',
    long_description=readme_content + '\n\n' + license_content,
    long_description_content_type='text/markdown',
    url='https://t.me/iamunicode',
    author='Unicode',
    license='MIT',
    classifiers=classifiers,
    keywords='emails',
    packages=find_packages(),
    install_requires=['undetected-chromedriver', 'beautifulsoup4', 'setuptools'],
    python_requires='>=3.12',
)
