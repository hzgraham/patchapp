import urllib.request, urllib.error, git, shutil, os, glob
from django.http import Http404
from .models import Server,Hosttotal

class ModMaint():
    def parseGit(self, manifests):
        git_path = 'autopatch/manifests'
        if not os.path.isdir(git_path):
            repo = git.Repo.clone_from(manifests,'autopatch/manifests')
            print("this is the repo: ",repo)
        else:
            shutil.rmtree(git_path)
            repo = git.Repo.clone_from(manifests,'autopatch/manifests')
            print("The path already exists",git_path)
        host_paths = []
        host_paths.extend(glob.glob(git_path+'/nodes/*'))
        print("Host Paths",host_paths)
        for each in host_paths:
            mgmt = ''
            hostgroup = ''
            exclude = ''
            skip = ''
            comments = ''
            pathname = each+'/maint.yaml'
            if os.path.exists(pathname):
                with open(pathname, 'rt') as myfile:
                    lines = myfile.readlines()
                    for i in lines:
                        if 'syspatch_mgmt: IT-Platops' == i.split("\n")[0]:
                            mgmt = i.split(":")[1].strip().split("\n")[0]
                        if 'syspatch_hostgroup' == i.split(":")[0]:
                            hostgroup = i.split(":")[1].strip().split("\n")[0]
                        if 'syspatch_yum_excludes' == i.split(":")[0]:
                            exclude = i.split(":")[1].strip().split("\n")[0]
                        if 'syspatch_skip' == i.split(":")[0]:
                            skip = i.split(":")[1].strip().split("\n")[0]
                            # if i.split(":")[1].strip().split("\n")[0] is '1':
                            #     skip = 'TRUE'
                            # elif i.split(":")[1].strip().split("\n")[0] is '0':
                            #     z = 'FALSE
                        if 'syspatch_comment' == i.split(":")[0]:
                            comments = i.split(":")[1].strip().split("\n")[0]
                    servername = each.split('/')[-1]
                    print("servername: ",servername)
                    s = Server(server=servername)
                    s.server = each.split('/')[-1]
                    s.mgmt = mgmt
                    s.exclude = exclude
                    s.skip = skip
                    s.hostgroup = hostgroup
                    s.comments = comments
                    print("server: ",s.server)
                    s.save()
                myfile.close()

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
        params = [['Hostname','Excluded packages','Skip','Hostgroup','Comments','Pastebin Link (If Errors Are Present)']]
        for host in Server.objects.all():
            hostname = host.server
            exclude = host.exclude
            skip = host.skip
            hostgroup = host.hostgroup
            comments = host.comments
            params.append([hostname, exclude, skip, hostgroup])
        return params

    def hostCount(self, env, field):
        Hosttotal.objects.all().filter(env=env).delete()
        total = 0
        for each in Server.objects.all().order_by("server"):
            s = each.server
            if env is "Prod":
                if ".prod." in s or ".util" in s:
                    total += 1
                    #print("1st check servername: ",s)
                elif ".dev" not in s and  ".stage." not in s and ".qa." not in s:
                    total += 1
                    #print("2nd check servername: ",s)
                else:
                    #print(s,"Not a server in: ",env)
                    pass
            else:
                if field in s:
                    total += 1
                    #print("servername: ",s)
                else:
                    #print("Not a server in: ",env)
                    pass
        t = Hosttotal(env=env)
        t.env = env
        t.total = total
        total = {'env': t.env, 'total': t.total}
        t.save()
        return total
