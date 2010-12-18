import uuid

def create_build_task_param(spec):
    from irgsh.specification import Specification as BuildSpecification
    from irgsh.distribution import distribution as BuildDistribution

    dist = spec.distribution

    build_spec = BuildSpecification(spec.source, spec.orig,
                                    spec.source_type, self.source_opts)

    build_dist = BuildDistribution(dist.name, dist.mirror, dist.dist,
                                   self.components, self.extra)

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

