import uuid

from django.utils.translation import ugettext as _

def create_build_task_param(spec):
    from irgsh.specification import Specification as BuildSpecification
    from irgsh.distribution import Distribution as BuildDistribution

    dist = spec.distribution

    build_spec = BuildSpecification(spec.source, spec.orig,
                                    spec.source_type, spec.source_opts)

    build_dist = BuildDistribution(dist.name, dist.mirror, dist.dist,
                                   dist.components, dist.extra)

    return build_dist, build_spec

def build_task_id():
    return str(uuid.uuid4())

def get_package_info(packages):
    from .models import Package, SOURCE, BINARY

    result = []
    for info in packages:
        pkg = {}
        if info.has_key('Source'):
            pkg['name'] = info['Source']
            pkg['type'] = SOURCE
        else:
            pkg['name'] = info['Package']
            pkg['type'] = BINARY
            pkg['architecture'] = info['Architecture']

        pkg.save()

    return result

def store_package_info(spec, packages):
    from .models import Package, BINARY

    for info in packages:
        pkg = Package()
        pkg.specification = spec
        pkg.name = info['name']
        pkg.type = info['type']
        if pkg.type == BINARY:
            pkg.architecture = info['architecture']
        pkg.save()

def build_source_opts(source_type, source_opts):
    from .models import TARBALL, BZR

    if source_opts is None:
        source_opts = ''
    source_opts = source_opts.strip()

    if source_type == TARBALL:
        return None

    elif source_type == BZR:
        '''
        valid opts:
        - tag=a-tag
        - rev=a-rev
        '''
        if source_opts == '':
            return None

        try:
            key, value = source_opts.split('=', 1)
            key = key.strip()
            value = value.strip()
            if key in ['tag', 'rev']:
                return {key: value}

        except ValueError:
            pass

        raise ValueError(_('Invalid source options for Bazaar'))

