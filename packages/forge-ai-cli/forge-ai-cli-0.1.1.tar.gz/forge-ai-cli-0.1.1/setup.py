from setuptools import setup, find_packages

setup(
    name='forge-ai-cli',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'octoai-sdk',
    ],
    entry_points={
        'console_scripts': [
            'forge = forge.main:execute',
        ],
    },
    author='Amal Vivek',
    author_email='avivek99@gmail.com',
    description='A CLI AI Agent to execute shell commands',
    url='https://github.com/amalvivek/forge-cli',
)