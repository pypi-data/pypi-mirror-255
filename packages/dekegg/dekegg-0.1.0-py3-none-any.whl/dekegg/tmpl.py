from pathlib import Path
from dekgen.code.python.generator import CodeGenerator


class GeneratorBasic(CodeGenerator):
    TEMPLATE_DIR = Path(__file__).resolve().parent / 'templatefiles'

    def variables_data(self):
        return self.instance


class ProjectGenerator(GeneratorBasic):
    template_name = 'project'
