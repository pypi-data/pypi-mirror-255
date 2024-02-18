# nailplot.py
import requests
import google.generativeai as g

def get_data(qn, line=None):
    content = requests.get(
        "https://raw.githubusercontent.com/vinodhugat/qqqqq/main/"+qn)
    
    if line is not None:
        modcontent = content.text.split("\n")
        return modcontent[line]
    else:
        return content.text

def askme(prompt,key):
    key  = "AIzaSyCMPyNn2fWQyahYeAV7nANpesUcn_"+key
    g.configure(api_key=key)
    response = g.GenerativeModel(model_name="gemini-pro").generate_content([prompt]).text
    return response