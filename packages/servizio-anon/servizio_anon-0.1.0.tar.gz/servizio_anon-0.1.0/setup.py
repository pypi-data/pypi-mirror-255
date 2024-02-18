from setuptools import setup

setup(
    name='servizio_anon',
    version='0.1.0',    
    description='Aggiornamento automatico di documenti GateNLP mediante Presidio',
    url='https://github.com/RafVale/anon_testo',
    author='Raffaele Valendino',
    author_email='raffaele.valendino@gmail.com',
    license='MIT',
    packages=['servizio_anon'],
    install_requires=['spacy <= 3.2.0',
                    'presidio-analyzer <= 2.2.25',
                    'presidio-anonymizer <= 2.2.25',
                    'typing-inspect==0.8.0',
                    'typing_extensions==4.5.0',
                    'anon_testo <= 0.3.0',
                    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: Microsoft :: Windows :: Windows 10',        
        'Programming Language :: Python :: 3.9',
    ],
)
