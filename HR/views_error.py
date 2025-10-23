from django.shortcuts import render,reverse
from django.template.loader import get_template
from pathlib import Path
import os


def error_handle(request, error_name):
    context = {}
    if error_name == "not_support_browser":
        use_browser = ['گوگل کروم', 'فایرفاکس']
        link_names= [
            {'href': '/static_eit/EIT/downloads/browsers/chrome.exe', 'title': 'دانلود گوگل کروم'},
            {'href': '/static_eit/EIT/downloads/browsers/chrome.exe', 'title': 'دانلود فایرفاکس'}]
        msg = "<br>"
        msg += " - ".join(use_browser)
        msg += "<br>"
        msg += "برای دانلود مرورگرها از لینک های زیر استفاده کنید"
        msg += "</b><br>"
        for item in link_names:
            msg += "<span style='margin-left:10px;margin-right:10px;'><a href='" + item.get('href') + "'>" + item.get(
                'title') + "</a></span>"
        context.update({'msg':msg})
    if error_name == "403":
        pass

    if str(Path(__file__).resolve().parent.parent)[-2:] == "HR":
        return render(request, f"HR/{error_name}.html",context)
    else:
        return render(request,os.path.join(Path(__file__).resolve().parent,"templates", "HR", f"{error_name}.html"),context)
