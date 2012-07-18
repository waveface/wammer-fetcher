from setuptools import setup

def main():
    setup(
        name = 'wffetcher',
        version = '0.2',
        packages = ['wffetcher'],
        include_package_data = True,
        description = "web fetch for offline access",
        license = 'copyright reserved',
        maintainer = 'Steven Shen',
        maintainer_email = 'steven.shen@waveface.com',
        install_requires = ['lxml', 'zipfile', 'uuid', 'shutil']
        zip_safe = False,
        url = "https://waveface.com"
    )


if __name__ == '__main__':
    main()


