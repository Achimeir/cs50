from django import forms
from django.http import HttpResponseRedirect, request
from django.shortcuts import render
from django.urls import reverse
from . import util
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from markdown2 import markdown


def validate_page_not_exist(title):
    if title.lower() in [entry.lower() for entry in util.list_entries()]:
        raise ValidationError(
            _('%(title)s is already exist'),
            params={'title': title},
        )


class NewPageForm(forms.Form):
    title = forms.CharField(label="Page Title", validators=[
                            validate_page_not_exist])
    entry_data = forms.CharField(
        widget=forms.Textarea(), label="")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry_data = util.get_entry(title)
    if entry_data:
        entry_data = markdown(entry_data)
    return render(request, "encyclopedia/entry.html", {
        "title": title if entry_data else "Error Page",
        "entry_name": title,
        "entry_data": entry_data
    })


def search(request):
    search_entry = request.GET.get("search_entry")
    if util.get_entry(search_entry):
        return HttpResponseRedirect(reverse('entry', args=[search_entry]))
    entries = [entry for entry in util.list_entries(
    ) if search_entry.lower() in entry.lower()]
    return render(request, "encyclopedia/search.html", {
        "title": "Search Result",
        "entries_counter": len(entries),
        "entries": entries
    })


def new(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry_data = form.cleaned_data["entry_data"]
            if title.lower() not in [entry.lower() for entry in util.list_entries()]:
                util.save_entry(title, entry_data)
            return HttpResponseRedirect(reverse('entry', args=[title]))
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form.as_p()
            })
    else:
        return render(request, "encyclopedia/new.html", {
            "form": NewPageForm().as_p()
        })


def edit(request, title):
    if request.method == "POST":
        entry_data = request.POST.get("entry_data")
        util.save_entry(title, entry_data)
        return HttpResponseRedirect(reverse('entry', args=[title]))
    else:
        form = NewPageForm(
            initial={"title": title, "entry_data": util.get_entry(title)})
        return render(request, "encyclopedia/edit.html", {
            "form": form,
            "entry_name": title
        })


def rand(request):
    title = util.get_random_entry()
    if title:
        return HttpResponseRedirect(reverse('entry', args=[title]))
    else:
        return render(request, "encyclopedia/index.html")
