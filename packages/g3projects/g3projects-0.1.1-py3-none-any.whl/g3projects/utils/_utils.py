import os
import re
# import inspect

from jinja2 import Environment


# def get_template(template_name: str) -> str:
#     if (current_frame := inspect.currentframe()) is None:
#         raise RuntimeError("Cannot determine caller frame")
#     if (caller_frame := current_frame.f_back) is None:
#         err = f'Unexpected error while fetching template "{template_name}"'
#         raise RuntimeError(err)
#     caller_filename = caller_frame.f_globals["__file__"]
#     file_dir = os.path.dirname(os.path.abspath(caller_filename))
#     file_path = os.path.join(file_dir, 'templates', template_name)
#     with open(file_path, 'r') as file:
#         return file.read()


def combine_str(*strings: str) -> str:
    return "\n".join(s for s in strings if s) + '\n'


def remove_multiple_newlines(string: str) -> str:
    return re.sub('\n{3,}', '\n', string).strip()


def format_template(env: Environment, tpl_name: str, **kwargs) -> str:
    template = env.get_template(tpl_name)
    rendered = template.render(kwargs)
    return remove_multiple_newlines(rendered)


def write_to_file(path: str, name: str, contents: str) -> None:
    with open(os.path.join(path, name), 'w', encoding='utf-8') as file:
        file.write(contents)
