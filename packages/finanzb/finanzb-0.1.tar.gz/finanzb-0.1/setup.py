from setuptools import setup, find_packages

setup(
    name='finanzb',
    version='0.1',
    author='Mario Rene Salazar Torres',
    author_email='mrsalazar@outlook.com',
    description='Paquete para realizar evaluacion financiera de proyectos',
    long_description='Obtiene VAN TIR IR Flujos con Normas Tributarias Bolivianas',
    long_description_content_type='text/markdown',
    url='https://github.com/msalaztor',
    packages=find_packages(),
     install_requires=[
        'numpy_financial',
        # otras dependencias aquí si es necesario
    ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)