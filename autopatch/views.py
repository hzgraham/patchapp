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
import urllib, bs4, urllib.request, csv, os
from xmlrpc import client, server
import xmlrpc.client, xmlrpc.server

from .forms import PostForm, EmailForm, ServerForm, HostListForm, LoginForm, ErrataForm, ErratumForm
from .models import Server, Hosttotal, Errata, Owner, Audit
from autopatch.utils import ModMaint, TaskScripts, encouragement, Satellite

from django.views.decorators.debug import sensitive_variables
from django.views.decorators.debug import sensitive_post_parameters

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

# if not request.user.is_authenticated():
#             return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
# to get the uid of a user
# uid = request.user.username

def userLogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=request.REQUEST.get('uid'), password=request.REQUEST.get('password'))
    if user is not None:
        # the password verified for the user
        if user.is_active:
            print("User is valid, active and authenticated")
        else:
            print("The password is valid, but the account has been disabled!")
    else:
        # the authentication system was unable to verify the username and password
        print("The username and password were incorrect.")
    login(request, user)

@login_required
def profile(request):
    context = {}
    # groups = ldap_user.group_names
    # context['groups'] = groups
    uid = request.user.username
    # TaskScripts().parseServerForm(request.user, request.user.ldap_user.attrs)
    all_groups = request.user.ldap_user.group_names
    context['name'] = ''.join(request.user.ldap_user.attrs['displayname']+request.user.ldap_user.attrs['sn'])
    context['uid'] = uid
    context['all_groups'] = all_groups
    return render_to_response('autopatch/profile.html', context, context_instance=RequestContext(request))

# The group that can perform admin tasks is a build time env variable
def is_member(request):
    # uid = request.user.username
    groups = request.ldap_user.group_names
    admin_group = os.getenv('LDAP_ADMIN_GROUP')
    # user = request.ldap_user.User
    # TaskScripts().parseServerForm(admin_group, groups)
    group = False
    for each in groups:
        if each == admin_group:
            group = True
    return group

@login_required
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
    return response

# Funtion used to import hosts from git by cloning the repo
@login_required
def Git(request):
    unlist = []
    #Checks if a path was give to the git repo
    if(request.GET.get('mybtn')):
        manifests = str(request.GET.get('gitpath'))
    elif(request.GET.get('clear')):
        Server.objects.all().delete()
        envs = (('Prod',".prod."), ("Stage",".stage."), ("QA",".qa."), ("Dev",".dev"))
        for env,field in envs:
            total = ModMaint().hostCount(env, field)
        manifests = None
    else:
        manifests = None
    # if a path was give this call parseGit which does the
    # importing of FQDNs and syspatch_* parameters to the Server model
    if manifests:
        # Server.objects.all().delete()
        hosts = ModMaint().parseGit(manifests)
        Audit.objects.all().delete()
    else:
        pass
    # unsassignlist (not in an env) hosts are displayed on the patching-tasks.html template
    unassignlist = Server.objects.all().filter(env="unassigned").order_by('server')
    for each in unassignlist:
        unhost = each.server
        unlist.append(unhost)
    context = {'unlist': unlist, 'encouragement': encouragement()}
    return HttpResponseRedirect(reverse('autopatch:tasks'), context)

# hosts of owners set here will be excluded from patching
@login_required
#@user_passes_test(is_member)
@user_passes_test(is_member,login_url='autopatch:denied', redirect_field_name=None)
def SetOwners(request):
    # owners is a test variable
    owners_list = []
    context = {'encouragement': encouragement()}
    owner_list = Owner.objects.all().order_by('owner')
    # If the "Set Owners" button is pressed
    if request.method == 'GET':
        if request.GET.get('addowners'):
            owners = str(request.GET.get('owners'))
            owners_list = owners.split(",")
            for each in owners_list:
                cl_owner = each.strip()
                if not Owner.objects.filter(owner=cl_owner).exists():
                    owner = Owner(owner=cl_owner)
                    owner.owner = cl_owner
                    owner.save()
                else:
                    pass
            context['owners_list'] = ModMaint().excludedOwners()
            ModMaint().allHostTotals()
            return HttpResponseRedirect(reverse('autopatch:owners'), context)
        # If the "Remove Owners" button is pressed
        elif request.GET.get('delowners'):
            Owner.objects.all().delete()
            context['owners_list'] = ModMaint().excludedOwners()
            ModMaint().allHostTotals()
            return HttpResponseRedirect(reverse('autopatch:owners'), context)
        else:
            pass
    context['owners_list'] = ModMaint().excludedOwners()
    return render(request, 'autopatch/owners.html', context)

@login_required
@user_passes_test(is_member,login_url='autopatch:denied', redirect_field_name=None)
def UpdateErrata(request):
    # This view used to update the top level errata
    args = {}
    args['encouragement'] = encouragement()
    if request.POST:
        # errata = Errata.objects.filter(pk=1)
        form = ErrataForm(request.POST)
        # form = ErrataForm(pk=1)
        if form.is_valid():
            new_erratas = {}
            # TaskScripts().parseForm(form)
            # saving the errata levels entered in the form
            RHEA = form.data['RHEA']
            RHSA = form.data['RHSA']
            RHBA = form.data['RHBA']
            oldrhea = ''
            oldrhsa = ''
            oldrhba = ''
            # errata = Errata.objects.get(pk=1)
            # TaskScripts().parseServerForm(RHEA, RHBA)
            # This keeps the exists errata levels set if none are entered in the form
            if not Errata.objects.exists():
                errata = Errata(pk=1)
            else:
                errata = Errata.objects.get(pk=1)
                oldrhea = errata.RHEA
                oldrhsa = errata.RHSA
                oldrhba = errata.RHBA
            errata_list = {'RHEA': RHEA, 'RHSA': RHSA, 'RHBA': RHBA}
            # checkErrata is a check for any clear returns to remove errata levels
            new_erratas = ModMaint().checkErrata(errata_list)
            # TaskScripts().parseServerForm('new errata', new_erratas)
            if new_erratas['RHEA'] == 'clear':
                errata.RHEA = ''
            elif new_erratas['RHEA']:
                errata.RHEA = RHEA
            elif oldrhea:
                errata.RHEA = oldrhea
            else:
                pass
            if new_erratas['RHSA'] == 'clear':
                errata.RHSA = ''
            elif new_erratas['RHSA']:
                errata.RHSA = RHSA
            elif oldrhsa:
                errata.RHSA = oldrhsa
            else:
                pass
            if new_erratas['RHBA'] == 'clear':
                errata.RHBA = ''
            elif new_erratas['RHBA']:
                errata.RHBA = RHBA
            elif oldrhba:
                errata.RHBA = oldrhba
            else:
                pass
            errata.save()
            # recalculates the desired errata for each host
            Satellite().recalcPlerrata()
            # if they exist then they are returned to the template
            if Errata.objects.exists():
                # errata = Errata.objects.first()
                errata = Errata.objects.first()
                args['RHEA'] = errata.RHEA
                args['RHSA'] = errata.RHSA
                args['RHBA'] = errata.RHBA
                # TaskScripts().parseServerForm('Errata does exist',errata)
            else:
                args['RHEA'] = ''
                args['RHSA'] = ''
                args['RHBA'] = ''
            args.update(csrf(request))
            return render(request, 'autopatch/update_errata.html', args)
    else:
        form = ErrataForm()
    args.update(csrf(request))
    # Checking if errata levels exist
    # if they exist then they are returned to the template
    if Errata.objects.exists():
        # errata = Errata.objects.first()
        errata = Errata.objects.first()
        args['RHEA'] = errata.RHEA
        args['RHSA'] = errata.RHSA
        args['RHBA'] = errata.RHBA
        # TaskScripts().parseServerForm('Errata does exist',errata)
    else:
        args['RHEA'] = ''
        args['RHSA'] = ''
        args['RHBA'] = ''
        # TaskScripts().parseServerForm('Errata doesnt exist!','no errata')
    args['form'] = form
    return render_to_response('autopatch/update_errata.html', args)

def Home(request):
    template = 'autopatch/base.html'
    context = {'encouragement': encouragement()}
    return render(request, template, context)

def denied(request):
    template = 'autopatch/denied.html'
    context = {'encouragement': encouragement()}
    return render_to_response(template, context)

@login_required
@user_passes_test(is_member,login_url='autopatch:denied', redirect_field_name=None)
def ChangesView(request):
    changes_list = Audit.objects.all().order_by('mod_date')
    context = {'changes_list': changes_list, 'encouragement': encouragement()}
    return render(request, 'autopatch/changes_list.html', context)

def ProdView(request):
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
    prod_list = Server.objects.all().filter(env="prod").order_by('server')
    context = {'host_list': prod_list, 'total': prodtotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/host_list.html', context)

def StageView(request):
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
    stage_list = Server.objects.all().filter(env="stage").order_by('server')
    context = {'host_list': stage_list, 'total': stagetotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/host_list.html', context)

def QAView(request):
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
    qa_list = Server.objects.all().filter(env="qa").order_by('server')
    context = {'host_list': qa_list, 'total': qatotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/host_list.html', context)

def DevView(request):
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
    dev_list = Server.objects.all().filter(env="dev").order_by('server')
    context = {'host_list': dev_list, 'total': devtotal, 'env': env, 'encouragement': encouragement()}
    return render(request, 'autopatch/host_list.html', context)

@login_required
@user_passes_test(is_member,login_url='autopatch:denied', redirect_field_name=None)
def erratumView(request):
    context = {}
    if request.method == "GET":
        if(request.GET.get("erratum_hosts")):
            form = ErratumForm(request.GET)
            if form.is_valid():
                host_list = []
                env = form.data['environment']
                erratum = form.data['erratum']
                if env == 'all':
                    server_objs = Server.objects.all().order_by('server')
                    env = 'whole'
                else:
                    server_objs = Server.objects.filter(env=env).order_by('server')
                for host in server_objs:
                    if host.updates:
                        updates = eval(host.updates)
                        updates = list(updates)
                    else:
                        updates = []
                    #TaskScripts().parseServerForm(host.server, updates)
                    if any(x in erratum for x in updates):
                        host_list.append(host)
                    else:
                        pass
                total = len(host_list)
                #TaskScripts().parseServerForm(total, host_list)
                context = {'host_list': host_list, 'env': env, 'total': total}
                return render(request,'autopatch/erratum_hosts.html', context)
    context['encouragement'] = encouragement()
    return render(request, 'autopatch/erratum_hosts.html', context)

@sensitive_post_parameters()
@sensitive_variables()
@login_required
@user_passes_test(is_member,login_url='autopatch:denied', redirect_field_name=None)
def SatInfo(request):
    # SatId will get the ID of each server in Satellite
    # There are 4 buttons on the patching tasks page, one for each env
    context = {'encouragement': encouragement()}
    if request.POST:
        form = LoginForm(request.POST)
        # TaskScripts().parseSatForm(request, form)
        if form.is_valid():
            # Get variables from the form
            user = form.cleaned_data['loginname']
            pswd = form.cleaned_data['password']
            url = form.cleaned_data['satellite']
            URL = "https://"+url+"/rpc/api"
            env = form.cleaned_data['environment']
            # using xmlrpc to get a session key from the satellite server
            client = xmlrpc.client.Server(URL, verbose=0)
            session = client.auth.login(user, pswd)
            # Get list of hosts in an env
            host_list = Server.objects.all().filter(env=env).order_by('server')
            # Loop through each host and get satellite ID
            client = xmlrpc.client.Server(URL, verbose=0)
            for host in host_list:
                servername = host.server
                if not host.satid:
                    data = client.system.getId(session, servername)
                    # TaskScripts().parseSatForm(servername, data)
                    if data:
                        getid = data[0].get('id')
                        host.satid = getid
                        # TaskScripts().parseSatForm(servername, getid)
                    else:
                        pass
                else:
                    # TaskScripts().parseSatForm(servername, "already has a satid")
                    pass
                if host.satid:
                    updates = []
                    # TaskScripts().parseSatForm(servername, env)
                    errata_list = client.system.getRelevantErrata(session,host.satid)
                    # If a list of errata is returned from satellite
                    if errata_list:
                        # TaskScripts().parseSatForm(servername, errata_list)
                        for erratum in errata_list:
                            updates.append(erratum["advisory_name"])
                            all_updates = set(updates)
                            # TaskScripts().parseSatForm(host.server,all_updates)
                        needed_updates = Satellite().desiredErrata(all_updates)
                        # TaskScripts().parseSatForm(needed_updates, all_updates)
                        if needed_updates:
                            host.plerrata = str(needed_updates).replace("'",'"')
                            # TaskScripts().parseSatForm(servername, host.plerrata)
                            host.uptodate = 0
                        else:
                            host.plerrata = None
                            host.uptodate = 1
                        host.updates = str(all_updates).replace("'",'"')
                        host.save()
                    else:
                        pass
                else:
                    pass
            client.auth.logout(session)
    else:
        pass
    return HttpResponseRedirect(reverse('autopatch:tasks'), context)

@login_required
def resultView(request, pk):
    args = []
    server = get_object_or_404(Server, pk=pk)
    template_name = 'autopatch/results.html'
    hostgroup = "nothing"
    exclude = "nothing"
    skip = []
    if request.POST.get('set_param'):
        form = ServerForm(request.POST)
        # test1 = "Recognizes form"
        # test2 = pk
        # TaskScripts().parseServerForm(test1, test2)
        if form.is_valid():
            exclude = form.data['exclude']
            hostgroup = form.data['hostgroup']
            skip = form.cleaned_data['skip']
            comments = form.cleaned_data['comments']
            s = Server.objects.get(pk=pk)
            # Creating a new Audit entry for the changes_list.html
            cn = ''.join(request.user.ldap_user.attrs['cn'])
            Audit.objects.create(server=s.server, skip=s.skip, exclude=s.exclude, hostgroup=s.hostgroup, comments=s.comments, user=cn)
            # test1 = [exclude, hostgroup, skip, comments]
            # test2 = pk
            # TaskScripts().parseServerForm(test1, test2)
            s.exclude = exclude
            s.hostgroup = hostgroup
            s.skip = skip
            s.comments = comments
            s.save()
        else:
            # test1 = "Form not valid"
            # test2 = ""
            # TaskScripts().parseServerForm(test1, test2)
            pass
    else:
        # test1 = "Doesn't recognize form"
        # test2 = ""
        # TaskScripts().parseServerForm(test1, test2)
        pass
    id_number = pk
    context = {'exclude': exclude, 'encouragement': encouragement(), 'hostgroup': hostgroup, 'skip': skip}
    return HttpResponseRedirect(reverse('autopatch:detail', kwargs={'pk':id_number}), context)

def DetailView(request, pk):
    server = get_object_or_404(Server, pk=pk)
    if server.updates != None:
        server.updates = server.updates.strip('{}').replace('"','').replace(' ', '').split(',')
    if server.plerrata != None:
        server.plerrata = server.plerrata.strip('{}').replace('"','').replace(' ', '').split(',')
    template_name = 'autopatch/results.html'
    context = {'encouragement': encouragement(), 'server': server}
    return render_to_response('autopatch/results.html', context,
                              context_instance=RequestContext(request))

# Patching Task Related Views
# ##########################################
# @login_required(login_url='autopatch/login/')
class TasksView(generic.ListView):
    template_name = 'autopatch/patching-tasks.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")
    def get_context_data(self):
        return {'encouragement': encouragement()}

class Unicorns(generic.ListView):
    template_name = 'autopatch/unicorns.html'
    def get_queryset(self):
        return Server.objects.all().order_by("server")
    def get_context_data(self):
        return {'encouragement': encouragement()}

@login_required
def security(request):
    return render(request, 'autopatch/security.html')

# Views not currently being used
# ##########################################
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
