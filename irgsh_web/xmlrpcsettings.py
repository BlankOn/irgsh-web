from irgsh_web.basesettings import *

ROOT_URLCONF = 'irgsh_web.xmlrpcurls'

XMLRPC_METHODS = (
    ('irgsh_web.jobs.xmlrpc.get_new_tasks', 'get_new_tasks'),
    ('irgsh_web.jobs.xmlrpc.get_task_info', 'get_task_info'),
    ('irgsh_web.jobs.xmlrpc.populate_debian_info', 'populate_debian_info'),
    ('irgsh_web.jobs.xmlrpc.set_debian_copy', 'set_debian_copy'),
    ('irgsh_web.jobs.xmlrpc.set_orig_copy', 'set_orig_copy'),
    ('irgsh_web.jobs.xmlrpc.xstart_assigning', 'start_assigning'),
    ('irgsh_web.jobs.xmlrpc.set_orig_copy', 'set_orig_copy'),
    ('irgsh_web.jobs.xmlrpc.task_init_failed', 'task_init_failed'),
    ('irgsh_web.jobs.xmlrpc.xstart_running', 'start_running'),
    ('irgsh_web.jobs.xmlrpc.assign_task', 'assign_task'),
    ('irgsh_web.jobs.xmlrpc.assignment_download', 'assignment_download'),
    ('irgsh_web.jobs.xmlrpc.assignment_environment', 'assignment_environment'),
    ('irgsh_web.jobs.xmlrpc.assignment_building', 'assignment_building'),
    ('irgsh_web.jobs.xmlrpc.assignment_upload', 'assignment_upload'),
    ('irgsh_web.jobs.xmlrpc.assignment_complete', 'assignment_complete'),
    ('irgsh_web.jobs.xmlrpc.assignment_fail', 'assignment_fail'),
    ('irgsh_web.jobs.xmlrpc.assignment_cancel', 'assignment_cancel'),
    ('irgsh_web.jobs.xmlrpc.assignment_wait_for_upload', 'assignment_wait_for_upload'),
    ('irgsh_web.jobs.xmlrpc.assignment_wait_for_installing', 'assignment_wait_for_installing'),
    ('irgsh_web.jobs.xmlrpc.assignment_upload_log', 'assignment_upload_log'),
    ('irgsh_web.jobs.xmlrpc.get_unassigned_task', 'get_unassigned_task'),
    ('irgsh_web.jobs.xmlrpc.get_assignment_for_builder', 'get_assignment_for_builder'),
    ('irgsh_web.jobs.xmlrpc.builder_ping', 'builder_ping'),
    ('irgsh_web.jobs.xmlrpc.get_assignment_info', 'get_assignment_info'),
    ('irgsh_web.jobs.xmlrpc.get_assignments_to_upload', 'get_assignments_to_upload'),
    ('irgsh_web.jobs.xmlrpc.get_assignments_to_install', 'get_assignments_to_install'),
)
