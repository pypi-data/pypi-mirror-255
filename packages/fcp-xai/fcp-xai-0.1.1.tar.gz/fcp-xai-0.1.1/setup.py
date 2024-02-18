from setuptools import setup

setup(
    name='fcp-xai',
    version='0.1.1',
    description='Forward Composition Propagation',
    long_description="Forward Composition Propagation (FCP) is a post-hoc XAI method for explaining the " +
                     "predictions of feed-forward neural networks " +
                     "trained on structured classification problems. Each neuron is described by a composition " +
                     "vector indicating the role of each problem feature in that neuron.",
    url='https://github.com/igraugar/fcp',
    author='Isel Grau, Gonzalo Nápoles',
    author_email='i.d.c.grau.garcia@tue.nl, g.r.napoles@uvt.nl',
    license='Apache License 2.0',
    packages=['fcp'],
    install_requires=['numpy', 'tensorflow'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.8',
    ],
)