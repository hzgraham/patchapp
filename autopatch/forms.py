from django import forms
from autopatch.models import Server, Errata

class PostForm(forms.Form):
    content = forms.CharField(max_length=256)
    created_at = forms.DateTimeField()

# class NameForm(form.Form):
#     your_name = forms.CharField(label='Your name', max_length=100)

class EmailForm(forms.Form):
    email = forms.EmailField(max_length=256)

class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    loginname = forms.CharField(max_length=256)
    satellite = forms.CharField(max_length=256)
    #hostname = forms.CharField(max_length=256)
    ENV = [
        ('dev'), ('qa'), ('stage'), ('prod'),
    ]
    environment = forms.ChoiceField(choices=ENV, required=True, label='Environment')

class ErrataForm(forms.ModelForm):

    class Meta:
        model = Errata
        fields = "__all__"

class ServerForm(forms.Form):
    server = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'server01.example.com'}))
    exclude = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'jbossas*, openjdk*'}))
    skip = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'False'}))
    hostgroup = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'JBoss Servers'}))
    comments = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'Jmainguy provisioned this server'}))
    satid = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': '0123456'}))
    env = forms.CharField(widget=forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'Prod'}))
    #updates = forms.TextInput(attrs={'size': 25, 'class': 'form-control', 'placeholder': 'Updates'})

class HostListForm(forms.Form):
    manifests = forms.CharField(max_length=256)
