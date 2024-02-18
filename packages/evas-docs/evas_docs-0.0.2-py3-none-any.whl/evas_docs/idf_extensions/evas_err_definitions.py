# Extension to generate evas-err definition as .rst
from ..util.util import call_with_python, copy_if_modified


def setup(app):
    app.connect('project-build-info', generate_err_defs)
    return {'parallel_read_safe': True, 'parallel_write_safe': True, 'version': '0.1'}


def generate_err_defs(app, project_description):
    # Generate 'evas-err_defs.inc' file with ESP_ERR_ error code definitions from inc file
    evas-err_inc_path = '{}/inc/evas-err_defs.inc'.format(app.config.build_dir)
    call_with_python('{}/tools/gen_evas-err_to_name.py --rst_output {}.in'.format(app.config.project_path, evas-err_inc_path))
    copy_if_modified(evas-err_inc_path + '.in', evas-err_inc_path)
