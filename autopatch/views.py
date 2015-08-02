from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.core.urlresolvers import reverse
from .models import Server,Hosttotal
from django.utils import timezone
from .forms import PostForm, EmailForm, ServerForm, HostListForm, LoginForm
from django.core.context_processors import csrf
from autopatch.utils import ModMaint
from time import sleep
from django.contrib.auth.backends import RemoteUserBackend
import urllib, bs4, urllib.request, csv

def CreateCSV(request):
    s = []
    q = []
    if(request.GET.get('mybtn')):
        servers = Server.objects.all().order_by("server")
        for host in Server.objects.all():
            s.append(host.server)
        #for host in servers:
    params = ModMaint().genCSV()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patching.csv"'
    writer = csv.writer(response)
    for each in params:
        writer.writerow(each)
    #context = {'params': params}
    #return render(request, 'autopatch/create_csv.html', context)
    return response

def devTotal(request):
    if(request.GET.get('mybtn')):
        ModMaint().hostCount("Dev")
    template_name = 'autopatch/dev-servers.html'

def GetList(request):
    if(request.GET.get('mybtn')):
        #mypythoncode.mypythonfunction( int(request.GET.get('mytextbox')) )
        manifests = str(request.GET.get('mytextbox'))
    else:
        manifests = None
    if manifests:
        Server.objects.all().delete()
        url_list = []
        paths = []
        mgmt = []
        host_list = HostList()
        myurl = urllib.request.urlopen(manifests)
        html = myurl.read()
        soup = bs4.BeautifulSoup(html, "html.parser")
        for link in soup.findAll("a"):
            if ".com" in link.string:
                path = link.get("href")
                maint_path = manifests+"/"+link.string+'/maint.yaml'
                syspatch_data = ModMaint().getMaint(maint_path)
                mgmt1 = syspatch_data.get('mgmt')
                exclude1 = syspatch_data.get('exclude')
                skip1 = syspatch_data.get('skip')
                hostgroup1 = syspatch_data.get('hostgroup')
                if not Server.objects.filter(server=link.string).exists():
                    s = Server(server=link.string)
                    s.server = link.string
                    s.mgmt = mgmt1
                    s.exclude = exclude1
                    s.skip = skip1
                    s.hostgroup = hostgroup1
                else:
                    s = Server(server=link.string)
                    s.server = link.string
                    s.mgmt = mgmt1
                    s.exclude = exclude1
                    s.skip = skip1
                    s.hostgroup = hostgroup1
                s.save()
                #mgmt.append(syspatch)
                #mgmt.append(syspatch.get('mgmt'))
                #if not Server.objects.filter(server=link.string).exists():
                    #s = Server(server=link.string)
                    #s.save()
                #url_list.append(link.get("href"))
                url_list.append(link.string)
                #paths.append(maint_path)
            else:
                pass
        context = {'manifests': manifests, 'url_list': url_list, 'check': "worked", 'paths': paths, 'mgmt1': mgmt1, 'skip1': skip1}
    else:
        context = {'manifests': manifests}
    return render(request, 'autopatch/get_list.html', context)

class AllHosts(generic.ListView):
    template_name = 'autopatch/serverlist.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")

def create(request):
    if request.POST:
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/autopatch/')
    else:
        form = ServerForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('autopatch/create_server.html', args)

def login(request):
    if request.Post:
        form = LoginForm(request.Post)
        if form.is_valid():
            pass

def Home(request):
    template = 'autopatch/base.html'
    return render(request, template)

class IndexView(generic.ListView):
    template_name = 'autopatch/index.html'
    context_object_name = 'latest_question_list'
    #queryset=Post.objects.all().order_by("-date")[:10]
    def get_queryset(self):
        """Return the last five published questions."""
        # return Question.objects.order_by('-pub_date')[:5]
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Server
    template_name = 'autopatch/results.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")

class TasksView(generic.ListView):
    template_name = 'autopatch/patching-tasks.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")

class ProdView(generic.ListView):
    template_name = 'autopatch/prod-servers.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")

class StageView(generic.ListView):
    template_name = 'autopatch/stage-servers.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")

class QAView(generic.ListView):
    template_name = 'autopatch/qa-servers.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")

def DevView(request):
    dev_list = Server.objects.all().order_by('server')
    env = "Dev"
    total = ModMaint().hostCount(env)
    devtotal = total.get("total")
    # if Hosttotal.objects.filter(env="Dev"):
    #     host = Hosttotal(env="Dev")
    #     total = host.total
    #     env = host.env
    # else:
    #     total = 0
    context = {'dev_list': dev_list, 'total': devtotal, 'env': env}
    return render(request, 'autopatch/dev-servers.html', context)

# class DevView(generic.ListView):
#     context = []
#     template_name = 'autopatch/dev-servers.html'
#     if Hosttotal.objects.filter(env="Dev"):
#         host = Hosttotal(env="Dev")
#         total = host.total
#     else:
#         total = 0
#     context = {'total': total}
#     def get_queryset(self):
#         #return Server.objects.all().order_by('server'),total
#         return Server.objects.all().order_by('server'),context

# Create your views here.
def index(request):
    # return HttpResponse("Hello, world. You're at the auto-patching index.")
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # output = ', '.join([p.question_text for p in latest_question_list])
    # return HttpResponse(output)
    # template = loader.get_template('polls/index.html')
    # context = RequestContext(request, {
    #     'latest_question_list': latest_question_list,
    # })
    context = {'latest_question_list': latest_question_list}
    # return HttpResponse(template.render(context))
    return render(request, 'autopatch/index.html', context)

def detail(request, question_id):
    # return HttpResponse("You're looking at question %s." % question_id)
    # try:
    #     question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #     raise Http404("Question does not exist")
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'autopatch/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # response = "You're looking at the results of question %s."
    # return HttpResponse(response % question_id)
    return render(request, 'autopatch/results.html', {'question': question})

def vote(request, question_id):
    #return HttpResponse("You're voting on question %s." % question_id)
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'autopatch/detail.html', {
            'question': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('autopatch:results', args=(p.id,)))
