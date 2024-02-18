from setuptools import setup, find_packages

setup(
    
    name='RIML',
    version='0.3.2',
    packages=find_packages('src'),
    author='Laboratory of Systems Biology and Bioinformatics (LBB)',
    author_email='amasoudin@ut.ac.ir',
    description='Empower Your Tomorrow, Conquer the Future!',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    package_dir={'': 'src'},

)