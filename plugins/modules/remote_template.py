#!/usr/bin/python3

from __future__ import (absolute_import, division, print_function)
import os
import re
from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.basic import AnsibleModule
from jinja2 import Environment

__metaclass__ = type

def include_file(path):
    with open(path, 'r') as file:
        return file.read()

def regex_replace(value='', pattern='', replacement='', ignorecase=False, multiline=False):
    ''' Perform a `re.sub` returning a string '''

    value = to_text(value, errors='surrogate_or_strict', nonstring='simplerepr')

    flags = 0
    if ignorecase:
        flags |= re.I
    if multiline:
        flags |= re.M
    _re = re.compile(pattern, flags=flags)
    return _re.sub(replacement, value)

def get_file(path):
    with open(path, 'r') as file:
        return file.read()

def write_file(path,content):
    with open(path, "w") as file:
        file.write(content)

def run_module():

    module_args = dict(
        path=dict(type='str', required=True),
        template=dict(type='str', required=True),
        vars=dict(type='dict', required=False)
    )

    result = dict(
        changed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    module.sha256
    env = Environment(extensions=['jinja2_ansible_filters.AnsibleCoreFiltersExtension'])
    env.filters['regex_replace'] = regex_replace
    env.globals['include_file'] = include_file

    if not os.path.exists(module.params['template']):
        module.fail_json(msg='Template does not exist', **result)

    out_path = module.params['path']
    template_path = module.params['template']
    template_content =  get_file(template_path)
    result_file = env.from_string(template_content).render(**(module.params["vars"] or dict())) 
    exiting_content = get_file(out_path) if os.path.exists(out_path) else ""

    result["changed"] = exiting_content != result_file

    if module.check_mode:
        module.exit_json(**result)
    
    write_file(out_path,result_file)    
    
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()