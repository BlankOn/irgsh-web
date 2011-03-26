from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from irgsh_web.repo.models import Package, PackageDistribution
from irgsh_web.build.models import Specification
from irgsh_web.utils import paginate

def _package_required(func):
    def _func(request, package_name, *args, **kwargs):
        package = get_object_or_404(Package, name=package_name)
        return func(request, package, *args, **kwargs)
    return _func

@_package_required
def show(request, package):
    # Published packages
    dists = PackageDistribution.objects.filter(package=package) \
                                       .values_list('distribution', flat=True)

    published = []
    for dist in dists:
        try:
            spec = Specification.objects.filter(package=package,
                                                distribution__repo=dist,
                                                status=999) \
                                        .order_by('-finished') \
                                        .select_related()[0]
            published.append(spec)
        except IndexError:
            pass

    # Recent builds

    builds = Specification.objects.filter(package=package) \
                                  .order_by('-finished') \
                                  .select_related()[:15]

    context = {'package': package,
               'published': published,
               'builds': builds}
    return render_to_response('package/show.html', context,
                              context_instance=RequestContext(request))

def index(request):
    build_list = Specification.objects.filter(status=999) \
                                      .order_by('-finished') \
                                      .select_related()
    builds = paginate(build_list, 50, request.GET.get('page', 1))
    
    context = {'builds': builds}
    return render_to_response('package/index.html', context,
                              context_instance=RequestContext(request))

