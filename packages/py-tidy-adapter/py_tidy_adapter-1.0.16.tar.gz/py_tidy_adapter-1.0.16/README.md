### Python module to access tidy functionality


Distribuzione generata con comando:
  <br/>&emsp;`python setup.py sdist bdist_wheel`

Pubblicazione su Pypi
   <br/>&emsp;`twine upload dist/*`

Documentazione generata con comando:
  <br/>&emsp;`pdoc --html .\py_adapter`
  
 <br/>Installazione
  <br/>&emsp;`cd %HOME_TIDY%/basvi/pythonenv`
  <br/>&emsp;`source bin/activate`
  <br/>&emsp;`pip install py_adapter-<version>.tar.gz ` 


<br/>Moduli generati
<li/>adapter.py: funzioni per interfacciarsi al server tidy.
<li/>tidy.py: funzioni di utilità generale


<br/>Per utilizzare i moduli
   <li/>from py_tidy_adapter  import Adapter
   <li/>from py_tidy_adapter  import tidy
   
   
   
Puoi trovare ulteriore documentazione [qui](./html/py_adapter/index.html)
   