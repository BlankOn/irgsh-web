import uuid

def create_build_task_param(spec):
    from irgsh.specification.Specification as BuildSpecification
    from irgsh.distribution.distribution as BuildDistribution

    dist = spec.distribution

    build_spec = BuildSpecification(spec.source, spec.orig,
                                    spec.source_type, self.source_opts)

    build_dist = BuildDistribution(dist.name, dist.mirror, dist.dist,
                                   self.components, self.extra)

    return build_dist, build_spec

def build_task_id():
    return str(uuid.uuid4())

