from setuptools import setup, find_packages

setup(
    name='treinta_ms_utils',
    version='1.0.0',  # Incremento de la versión
    author='cristian.pinela',
    author_email='cristian.pinela@treinta.co',
    packages=find_packages(),
    license='LICENSE',
    description='paquete que permite a los microservicios interaccionar con otros MS',
    long_description=open('README.md').read(),  # Asegurarse de que README.md no tiene errores de sintaxis
    long_description_content_type='text/markdown',  # Especifica que la descripción larga está en Markdown
    install_requires=[
        'boto3',
        'botocore',
        'pytz'
    ]
)
