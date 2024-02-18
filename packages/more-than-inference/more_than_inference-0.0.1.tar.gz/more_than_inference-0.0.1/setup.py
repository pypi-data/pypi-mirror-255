import os

import setuptools
from setuptools.command.install import install

PACKAGE_NAME = "more_than_inference"


def build_proto(dist_dir, proto_dir):
    os.system(f'protoc --python_out={dist_dir} --proto_path={dist_dir} {proto_dir}/*.proto')


class InstallCommand(install):
    def run(self):
        install.run(self)
        self.compile_protos()

    def compile_protos(self):
        from pathlib import Path
        install_dir = Path(self.install_lib, PACKAGE_NAME)
        proto_dir = install_dir / 'protos'
        build_proto(install_dir.parent, proto_dir)


setuptools.setup(
    packages=setuptools.find_namespace_packages("src"),
    package_dir={"": "src"},
    package_data={PACKAGE_NAME: ["protos/*"]},
    cmdclass={
        'install': InstallCommand,
    },
)
