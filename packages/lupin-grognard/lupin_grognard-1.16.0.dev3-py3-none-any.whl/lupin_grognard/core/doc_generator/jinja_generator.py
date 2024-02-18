import os

from jinja2 import (
    Environment,
    PackageLoader,
    Template,
    TemplateError,
    TemplateNotFound,
    TemplateRuntimeError,
    select_autoescape,
)

from lupin_grognard.core.tools.log_utils import die, info
from lupin_grognard.core.tools.utils import write_file


class JinjaGenerator:
    def __init__(self, *args):
        super().__init__(*args)

    def _get_local_template(self, template_name: str) -> Template:
        try:
            package_loader = PackageLoader("lupin_grognard", "templates")
            env = Environment(
                loader=package_loader,
                autoescape=select_autoescape(),
                trim_blocks=True,  # Removes unnecessary spaces before and after blocks and loop
                lstrip_blocks=True,  # Removes unnecessary spaces before blocks and loop
            )
            return env.get_template(template_name)
        except TemplateNotFound:
            die(msg=f"Template 'lupin_grognard/templates/{template_name}' not found")

    def _replace_extension_to_j2(self, file_name: str) -> str:
        assert file_name.count(".") == 1
        base_name = file_name.rsplit(".", 1)[0]
        return f"{base_name}.j2"

    def _generate_file(self, path: str, file_name: str, context={}) -> None:
        template_name = self._replace_extension_to_j2(file_name=file_name)
        template = self._get_local_template(template_name=template_name)
        try:
            content = template.render(context)
        except (TemplateError, TemplateRuntimeError) as e:
            die(msg=f"Error rendering Jinja2 template: {e}")
        if not path:
            info(msg=f"Generating {file_name} file")
            write_file(file=f"{file_name}", content=content)
        else:
            self._generate_path(path=path)
            info(msg=f"Generating {path}/{file_name} file")
            write_file(file=f"{path}/{file_name}", content=content)
        info(msg="File generated")

    def _generate_path(self, path: str) -> None:
        if not os.path.exists(path):
            path = path[:-1] if path.endswith(os.path.sep) else path
            os.makedirs(path)
