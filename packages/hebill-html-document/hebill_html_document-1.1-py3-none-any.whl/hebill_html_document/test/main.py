from hebill_html_document import document
from hebill_html_document.nodes import comment


doc = document()
doc.titles.append("Hello World")
doc.html.body.create().tag().div("Hello World")
x = comment(doc.html.body.create().tag().div(), "Hello World2")
output = doc.output()
