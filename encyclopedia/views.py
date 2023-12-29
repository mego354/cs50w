from django.shortcuts import render, redirect
from .util import get_entry, save_entry, list_entries
from markdown2 import markdown
from django import forms
from django.http import HttpResponse
import secrets


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": list_entries()
    })

def entry_page(request, page_title):
    content = html_code(page_title)
    if content :
        return render(request, "encyclopedia/Entry_Page.html", {
            "title": page_title,
            "content": content,
        })
    else:
        return render(request, "encyclopedia/error.html", {
        "text": f"there is no page with the title - {page_title} -"
    })

              
def searching(request):
    if request.method == "POST":
        pages_list = list_entries()
        page_title = request.POST['q']
        content = html_code(page_title)

        if content :
            return render(request, "encyclopedia/Entry_Page.html", {
                "title": page_title,
                "content": content,
            })

        return find_page(pages_list, page_title, request)


              
def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new_Page.html", {
            "form": Newpage()
        })
    else:
        form = Newpage(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if get_entry(title):
                return render(request, "encyclopedia/error.html", {
                    "text": f" - {title} -  page already exist"
                })
            else:
                save_entry(title.capitalize(), content)
                return entry_page(request, title)
                
                  
              
def edit(request):
    if request.method == "POST":
        title = request.POST["title"]
        old_content = get_entry(title)
        form = form_edit(old_content)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": form,
        })



def save_changes(request):
    if request.method == "POST":
        title = request.POST["title"]
        form = NewpageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            save_entry(title, content)
            # Redirect the user to a specific page
            return entry_page(request, title)
    return HttpResponse("Invalid request")
            
def random_page(request):
    current_list = list_entries()
    title = secrets.choice(current_list)
    return entry_page(request, title)




##################################################################################################
def find_page(pages_list, page_title, request) :
    pages_in_suggestion = []
    for suspect in pages_list :
        if page_title.lower() in suspect.lower() or suspect.lower() in page_title.lower():
            pages_in_suggestion.append(suspect)
    if pages_in_suggestion:
        return render(request, "encyclopedia/suggestion.html", {
            "pages_in_suggestion": pages_in_suggestion,
        })
    else:       
        return render(request, "encyclopedia/error.html", {
            "text": f" - {page_title} -  page Doesn't exist"
        })
 
 
def html_code(title):
    content = get_entry(title)
    if content:
        return markdown(content)
    else:
        return None    


class Newpage(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': "Page's title"}))
    content = forms.CharField(label='', widget=forms.Textarea(attrs={"required": True, 'placeholder': "Page's content"}))


class NewpageForm(forms.Form):
    content = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={"required": True, 'placeholder': "Page's content"})
    )

def form_edit(old_content):
    initial_data = {'content': old_content}
    return NewpageForm(initial=initial_data)


