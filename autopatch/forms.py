from django import forms
from models import Server

class PostForm(forms.Form):
    content = forms.CharField(max_length=256)
    created_at = forms.DateTimeField()

# class NameForm(form.Form):
#     your_name = forms.CharField(label='Your name', max_length=100)

class EmailForm(forms.Form):
    email = forms.EmailField(max_length=256)

class ServerForm(forms.ModelForm):

    class Meta:
        model = Server
        fields = "__all__"
        #can also specify only fields you want to appear
        #fields = ('server', 'hostgroup', 'skip')

class HostListForm(forms.Form):
    manifests = forms.CharField(max_length=256)
