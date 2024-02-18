from setuptools import setup
from os import getenv, path, walk


URL = "https://github.com/OpenVoiceOS/ovos-testpkg"
SKILL_CLAZZ = "ReplaceSkillNameSkill"

AUTHOR, SKILL_NAME = URL.split(".com/")[-1].split("/")
ADDITIONAL_AUTHORS = []
AUTHORS = ADDITIONAL_AUTHORS + [AUTHOR]

SKILL_PKG = SKILL_NAME.lower().replace('-', '_')
PLUGIN_ENTRY_POINT = f'{SKILL_NAME.lower()}.{AUTHOR.lower()}={SKILL_PKG}:{SKILL_CLAZZ}'
BASE_PATH = path.abspath(path.dirname(__file__))
PKG_PATH = path.join(BASE_PATH, SKILL_PKG)


def get_version():
    """ Find the version of the package"""
    version = None
    version_file = path.join(PKG_PATH, 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


def get_requirements(rel_path: str):
    requirements_file = path.join(BASE_PATH, rel_path)
    with open(requirements_file, 'r', encoding='utf-8') as r:
        requirements = r.readlines()
    requirements = [r.strip() for r in requirements if r.strip()
                    and not r.strip().startswith("#")]

    for i in range(0, len(requirements)):
        r = requirements[i]
        if "@" in r:
            parts = [p.lower() if p.strip().startswith("git+http") else p
                     for p in r.split('@')]
            r = "@".join(parts)
        if getenv("GITHUB_TOKEN"):
            if "github.com" in r:
                requirements[i] = \
                    r.replace("github.com",
                              f"{getenv('GITHUB_TOKEN')}@github.com")
    return requirements


def find_resource_files():
    resource_base_dirs = ("locale", "ui", "vocab", "dialog", "regex", "res")
    package_data = []
    for res in resource_base_dirs:
        if path.isdir(path.join(PKG_PATH, res)):
            for (directory, _, files) in walk(path.join(PKG_PATH, res)):
                if files:
                    package_data.append(
                        path.join(directory.replace(PKG_PATH, "").lstrip('/'),
                                  '*'))
    return package_data


with open(path.join(BASE_PATH, "README.md"), "r") as f:
    long_description = f.read()


setup(
    name=SKILL_NAME,
    version=get_version(),
    url=URL,
    license='Apache-2.0',
    install_requires=get_requirements("requirements.txt"),
    author=",".join(AUTHORS),
    author_email='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[SKILL_PKG],
    package_data={SKILL_PKG: find_resource_files()},
    include_package_data=True,
    entry_points={"ovos.plugin.skill": PLUGIN_ENTRY_POINT}
)