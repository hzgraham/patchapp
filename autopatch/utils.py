import urllib.request, urllib.error, git
from django.http import Http404
from .models import Server,Hosttotal

class ModMaint():
    def parseGit(self, manifests):
        repo = git.Repo.clone_from(manifests,'autopatch/manifests')
        print("this is the repo: ",repo)

    def getMaint(self, url):
        syspatch = {}
        lines = []
        try:
            myurl = urllib.request.urlopen(url)
            lines = myurl.readlines()
        except urllib.error.HTTPError as e:
            #raise Http404("Poll does not exist")
            pass
        mgmt = ""
        hostgroup = ""
        exclude = ""
        skip = ""
        for i in lines:
            if b'syspatch_mgmt: IT-Platops' == i.split(b"\n")[0]:
                mgmt = i.split(b":")[1].strip().split(b"\n")[0]
            if b'syspatch_hostgroup' == i.split(b":")[0]:
                hostgroup = i.split(b":")[1].strip().split(b"\n")[0]
            if b'syspatch_yum_excludes' == i.split(b":")[0]:
                exclude = i.split(b":")[1].strip().split(b"\n")[0]
            if b'syspatch_skip' == i.split(b":")[0]:
                skip = i.split(b":")[1].strip().split(b"\n")[0]
            syspatch = {'mgmt': mgmt, 'hostgroup': hostgroup, 'exclude': exclude, 'skip': skip}
        #print(syspatch)
            #if syspatch is not dict:
            #syspatch = {}
        return syspatch

    def genCSV(self):
        s = []
        params = []
        for host in Server.objects.all():
            hostname = host.server
            exclude = host.exclude
            skip = host.skip
            hostgroup = host.hostgroup
            params.append([hostname, exclude, skip, hostgroup])
        return params

    def hostCount(self, env):
        Hosttotal.objects.all().filter(env=env).delete()
        total = {}
        t = Hosttotal(env=env)
        t.env = "Dev"
        t.total = 10
        total = {'env': t.env, 'total': t.total}
        t.save()
        return total
        #if not Hostcount.objects.filter(env="Dev").exists():
        #    print("no hosts in dev")
        #else:
        #    print("hosts in dev")
