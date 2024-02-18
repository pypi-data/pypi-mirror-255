from setuptools import setup, find_packages

setup(
    name='FH_AI_TOOL',
    version='1.0.0',
    description='FH,FJ Vision AI SYSTEM LIB',
    author='LEE_DH',
    author_email='ldh9616@nate.com',
    url='https://github.com/LEE-pyt/AI_Module.git',
    install_requires=['tqdm', 'pandas', 'scikit-learn','torch==2.0.1','torchvision==0.15.2','onnx','onnxruntime','pycocotools','anomalib'],
    packages=find_packages(exclude=[]),
    keywords=['FH_AI', 'FH_AI_TOOL', 'FH_AI_LIB', 'python tutorial', 'pypi'],
    python_requires='>=3.8',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)