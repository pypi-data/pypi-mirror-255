from setuptools import setup, find_packages

setup(
    name='ShellMate',
    version='1.0.6',
    author='Siddhant',
    author_email='siddhant@zodevelopers.com',
    description='ShellMate: A GPT-Powered CLI Tool for Explaining and Finding Shell Commands',
    long_description=open(r'C:\Users\jason\PycharmProjects\shell_mate\readme.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Mercurius13/ShellMate',
    packages=find_packages(),
    install_requires=[
        'openai',
        'argparse',

        'python-dotenv',


    ],
    entry_points={
        'console_scripts': [
            'shellmate=shellmate.shellmate:shellmate',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
