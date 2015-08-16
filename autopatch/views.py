from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
#Class Views
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils import timezone

from django.core.context_processors import csrf
from time import sleep
from django.contrib.auth.backends import RemoteUserBackend
import urllib, bs4, urllib.request, csv
from xmlrpc import client, server
import xmlrpc.client, xmlrpc.server

from .forms import PostForm, EmailForm, ServerForm, HostListForm, LoginForm, ErrataForm
from .models import Server, Hosttotal, Errata
from autopatch.utils import ModMaint, TaskScripts, encouragement, Satellite

from django.views.decorators.debug import sensitive_variables
from django.views.decorators.debug import sensitive_post_parameters

def CreateCSV(request):
    s = []
    q = []
    context = {}
    #if request.GET:
    if(request.GET.get('devbtn')):
        dev_list = Server.objects.all().filter(env="dev").order_by('server')
        for host in dev_list:
            s.append(host.server)
    elif(request.GET.get('qabtn')):
        qa_list = Server.objects.all().filter(env="qa").order_by('server')
        for host in qa_list:
            s.append(host.server)
    elif(request.GET.get('stagebtn')):
        stage_list = Server.objects.all().filter(env="stage").order_by('server')
        for host in stage_list:
            s.append(host.server)
    elif(request.GET.get('prodbtn')):
        prod_list = Server.objects.all().filter(env="prod").order_by('server')
        for host in prod_list:
            s.append(host.server)
    else:
        pass
    params = ModMaint().genCSV(s)
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

def Git(request):
    unlist = []
    if(request.GET.get('mybtn')):
        manifests = str(request.GET.get('gitpath'))
    else:
        manifests = None
    if manifests:
        Server.objects.all().delete()
        hosts = ModMaint().parseGit(manifests)
    else:
        pass
    unassignlist = Server.objects.all().filter(env="unassigned").order_by('server')
    for each in unassignlist:
        unhost = each.server
        unlist.append(unhost)
    context = {'unlist': unlist, 'encouragement': encouragement()}
    return render(request, 'autopatch/patching-tasks.html', context)

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
        #host_list = HostList()
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

def UpdateErrata(request):
    #This view used to update the top level errata
    if request.POST:
        #errata = Errata.objects.filter(pk=1)
        form = ErrataForm(request.POST)
        #form = ErrataForm(pk=1)
        if form.is_valid():
            #TaskScripts().parseForm(form)
            #saving the errata levels entered in the form
            RHEA = form.data['RHEA']
            RHSA = form.data['RHSA']
            RHBA = form.data['RHBA']
            errata = Errata.objects.first()
            #This keeps the exists errata levels set if none are entered in the form
            if not errata:
                errata = Errata(RHEA=form.data['RHEA'])
            else:
                oldrhea = errata.RHEA
                oldrhsa = errata.RHSA
                oldrhba = errata.RHBA
            if RHEA:
                errata.RHEA = RHEA
            elif oldrhea:
                errata.RHEA = oldrhea
            else:
                pass
            if RHSA:
                errata.RHSA = RHSA
            elif oldrhsa:
                errata.RHSA = oldrhsa
            else:
                pass
            if RHBA:
                errata.RHBA = RHBA
            elif oldrhba:
                errata.RHBA = oldrhba
            else:
                pass
            errata.save()
            return HttpResponseRedirect('/autopatch/errata/')
    else:
        form = ErrataForm()
    args = {}
    args.update(csrf(request))
    if Errata.objects.exists():
        errata = Errata.objects.first()
        args['RHEA'] = errata.RHEA
        args['RHSA'] = errata.RHSA
        args['RHBA'] = errata.RHBA
        #updates = {'RHEA': RHEA, 'RHSA': RHSA, 'RHBA': RHBA}
    else:
        #updates = {'RHEA': 0, 'RHSA': 0, 'RHBA': 0}
        args['RHEA'] = 0
        args['RHSA'] = 0
        args['RHBA'] = 0
    #args = {'form': form}
    #args.append(updates)
    args['form'] = form
    #args['RHEA'] = errata.RHEA
    return render_to_response('autopatch/update_errata.html', args)

def Home(request):
    template = 'autopatch/base.html'
    context = {'encouragement': encouragement()}
    return render(request, template, context)

class TasksView(generic.ListView):
    template_name = 'autopatch/patching-tasks.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")
    def get_context_data(self):
        return {'encouragement': encouragement()}
    
class DetailView(generic.DetailView):
   model = Server
   template_name = 'autopatch/results.html'
   def get_queryset(self):
       return Server.objects.all().order_by("server")

def ProdView(request):
    prod_list = Server.objects.all().order_by('server')
    env = "Prod"
    field = ".prod."
    if Hosttotal.objects.filter(env=env).exists():
        h = Hosttotal.objects.get(env=env)
        prodtotal = h.total
    else:
        prodtotal = None
    if(request.GET.get('mybtn')):
        total = ModMaint().hostCount(env, field)
        prodtotal = total.get("total")
    context = {'prod_list': prod_list, 'total': prodtotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/prod-servers.html', context)

def StageView(request):
    stage_list = Server.objects.all().order_by('server')
    env = "Stage"
    field = ".stage."
    if Hosttotal.objects.filter(env=env).exists():
        h = Hosttotal.objects.get(env=env)
        stagetotal = h.total
    else:
        stagetotal = None
    if(request.GET.get('mybtn')):
        total = ModMaint().hostCount(env, field)
        stagetotal = total.get("total")
    context = {'stage_list': stage_list, 'total': stagetotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/stage-servers.html', context)

def QAView(request):
    qa_list = Server.objects.all().order_by('server')
    env = "QA"
    field = ".qa."
    if Hosttotal.objects.filter(env=env).exists():
        h = Hosttotal.objects.get(env=env)
        qatotal = h.total
    else:
        qatotal = None
    if(request.GET.get('mybtn')):
        total = ModMaint().hostCount(env, field)
        qatotal = total.get("total")
    context = {'qa_list': qa_list, 'total': qatotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/qa-servers.html', context)

def DevView(request):
    dev_list = Server.objects.all().order_by('server')
    env = "Dev"
    field = ".dev"
    if Hosttotal.objects.filter(env=env).exists():
        h = Hosttotal.objects.get(env=env)
        devtotal = h.total
    else:
        devtotal = None
    if(request.GET.get('mybtn')):
        total = ModMaint().hostCount(env, field)
        devtotal = total.get("total")
    context = {'dev_list': dev_list, 'total': devtotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/dev-servers.html', context)

@sensitive_variables('pswd', 'password', 'form')
@sensitive_post_parameters('password')
def SatId(request):
    #SatId will get the ID of each server in Satellite
    #There are 4 buttons on the patching tasks page, one for each env
    context = {'encouragement': encouragement()}
    if request.POST:
        form = LoginForm(request.POST)
        #TaskScripts().parseSatForm(request, form)
        if form.is_valid():
            user = form.cleaned_data['loginname']
            pswd = form.cleaned_data['password']
            url = form.cleaned_data['satellite']
            URL = "https://"+url+"/rpc/api"
            env = form.cleaned_data['environment']
            #name = form.cleaned_data['hostname']
            client = xmlrpc.client.Server(URL, verbose=0)
            session = client.auth.login(user, pswd)
            #session = 'temp'
            #context = Satellite().getIds(request, client, session, env)
            if(env=="dev"):
                dev_list = Server.objects.all().filter(env="dev").order_by('server')[:25]
                for host in dev_list:
                    servername = host.server
                    #print("Servername: ",servername)
                    client = xmlrpc.client.Server(URL, verbose=0)
                    data = client.system.getId(session, servername)
                    #TaskScripts().parseSatForm(servername, data)
                    if data:
                        getid = data[0].get('id')
                        host.satid = getid
                    else:
                        pass
                    host.save()
                    #context = {'getid': getid}
                client.auth.logout(session)
            if(env=="qa"):
                qa_list = Server.objects.all().filter(env="qa").order_by('server')[:25]
                for host in qa_list:
                    servername = host.server
                    #print("Servername: ",servername)
                    client = xmlrpc.client.Server(URL, verbose=0)
                    data = client.system.getId(session, servername)
                    #TaskScripts().parseSatForm(servername, data)
                    if data:
                        getid = data[0].get('id')
                        host.satid = getid
                    else:
                        pass
                    host.save()
                    #context = {'getid': getid}
                client.auth.logout(session)
            if(env=="stage"):
                stage_list = Server.objects.all().filter(env="stage").order_by('server')[:25]
                for host in stage_list:
                    servername = host.server
                    #print("Servername: ",servername)
                    client = xmlrpc.client.Server(URL, verbose=0)
                    data = client.system.getId(session, servername)
                    #TaskScripts().parseSatForm(servername, data)
                    if data:
                        getid = data[0].get('id')
                        host.satid = getid
                    else:
                        pass
                    host.save()
                    #context = {'getid': getid}
                client.auth.logout(session)
            if(env=="prod"):
                prod_list = Server.objects.all().filter(env="prod").order_by('server')[:25]
                for host in prod_list:
                    servername = host.server
                    #print("Servername: ",servername)
                    client = xmlrpc.client.Server(URL, verbose=0)
                    data = client.system.getId(session, servername)
                    #TaskScripts().parseSatForm(servername, data)
                    if data:
                        getid = data[0].get('id')
                        host.satid = getid
                    else:
                        pass
                    host.save()
                    #context = {'getid': getid}
                client.auth.logout(session)
    else:
        pass
    return render_to_response('autopatch/patching-tasks.html', context,
                              context_instance=RequestContext(request))

@sensitive_variables('pswd', 'password', 'form')
@sensitive_post_parameters('password')
def SatUpdates(request):
    #SatId will get the ID of each server in Satellite
    #There are 4 buttons on the patching tasks page, one for each env
    context = {'encouragement': encouragement()}
    errata_levels = {}
    errata = Errata.objects.first()
    if errata:
        errata_levels['rhea'] = errata.RHEA
        errata_levels['rhsa'] = errata.RHSA
        errata_levels['rhba'] = errata.RHBA
    else:
        pass
    if request.POST:
        form = LoginForm(request.POST)
        #TaskScripts().parseSatForm(request, form)
        if form.is_valid():
            user = form.cleaned_data['loginname']
            pswd = form.cleaned_data['password']
            url = form.cleaned_data['satellite']
            URL = "https://"+url+"/rpc/api"
            env = form.cleaned_data['environment']
            #name = form.cleaned_data['hostname']
            client = xmlrpc.client.Server(URL, verbose=0)
            session = client.auth.login(user, pswd)
            #session = 'temp'
            #context = Satellite().getIds(request, client, session, env)
            host_list = Server.objects.all().filter(env=env).order_by('server')[:25]
            for host in host_list:
                servername = host.server
                if host.satid:
                    updates = []
                    satid = host.satid
                    #TaskScripts().parseSatForm(servername, env)
                    client = xmlrpc.client.Server(URL, verbose=0)
                    erratas = client.system.getRelevantErrata(session,satid)
                    if erratas:
                        #TaskScripts().parseSatForm(servername, erratas)
                        for errata in erratas:
                            updates.append(errata['advisory_name']+' ')
                            Updates = ''.join(updates).strip()
                        needed_updates = Satellite().desiredErrata(updates)
                        #TaskScripts().parseSatForm(servername, Updates)
                        if needed_updates:
                            host.plerrata = needed_updates
                            host.uptodate = 0
                        else:
                            host.uptodate = 1
                        host.updates = Updates
                    else:
                        pass
                    host.save()
                else:
                    pass
                #context = {'getid': getid}
            client.auth.logout(session)
    else:
        pass
    return render_to_response('autopatch/patching-tasks.html', context,
                              context_instance=RequestContext(request))

def index(request):
    return render(request, 'autopatch/index.html')

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
    
def detail(request, question_id):
    # return HttpResponse("You're looking at question %s." % question_id)
    # try:
    #     question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #     raise Http404("Question does not exist")
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'autopatch/detail.html', {'question': question})
