import os
import sys
import json
import tempfile
import shutil
import subprocess
from setuptools.command.bdist_egg import bdist_egg
from dektools.file import read_text, write_file
from dektools.sys import sys_paths_relative, sure_command
from .tmpl import ProjectGenerator


class bdist_fullegg(bdist_egg):
    description = "create an full-egg (egg with dependencies) distribution"

    def run(self):
        requirements = 'requirements.txt'
        if requirements and os.path.exists(requirements):
            self._install(requirements, self.bdist_dir)
        super().run()

    @staticmethod
    def _install(requirements, target):
        target = os.path.normpath(os.path.abspath(target))
        if shutil.which('pdm'):
            path_dir = tempfile.mkdtemp(prefix='dekegg-pdm-install')
            dependencies = []
            if requirements:
                for line in read_text(requirements).splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dependencies.append(line)
            ProjectGenerator(path_dir, dict(
                dependencies=json.dumps(dependencies)
            )).render()
            write_file(os.path.join(path_dir, 'pdm.lock'), mi='requirements.lock')
            last_dir = os.getcwd()
            os.chdir(path_dir)
            sure_command('virtualenv .venv --no-pip --no-setuptools --no-wheel')
            sure_command(f'pdm install')
            path_platlib = sys_paths_relative(os.path.join(path_dir, '.venv'))['platlib']
            for file in os.listdir(path_platlib):
                if file.endswith('.dist-info'):
                    p = os.path.join(path_platlib, file, 'REFER_TO')
                    if os.path.exists(p):
                        pp = os.path.join(read_text(p).strip(), 'lib')
                        if os.path.exists(pp):
                            for f in os.listdir(pp):
                                write_file(os.path.join(target, f), c=os.path.join(pp, f))
            sure_command(f'{sys.executable} -m compileall {target}')
            os.chdir(last_dir)
        else:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install']
                + ['-U', '-t', target, '-r', requirements]
            )
