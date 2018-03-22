from setuptools import setup

setup(
    setup_requires=['libsass >= 0.6.0'],
    sass_manifests={
        'src': ('static/scss', 'static/css/compiled', '/static/css/compiled')
    }
)