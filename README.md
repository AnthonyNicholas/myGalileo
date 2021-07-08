# innerGalileo
[![Build Status](https://travis-ci.org/fun-zoological-computing/innerGalileo.svg?branch=master)](https://travis-ci.org/fun-zoological-computing/innerGalileo)

![for_git_hub.png](https://github.com/fun-zoological-computing/innerGalileo/blob/master/for_git_hub.png)
The goal of the inner Galileo project is to quantify & visualize metrics related to personal health - sleep, fitness etc. 

Galileo was a pioneer in empericism via quantification. In this quantified self project we want to get insights into our individual and personal functioning.
This approach is distinct from standard medical science, as we make predictions about health by comparing current state to our own past, rather than comparing our state to the mean of population 
[A similar project](https://pdfs.semanticscholar.org/8e32/64552e108d96e9b9fb95b9795bac989f5052.pdf).

# setup:
```
  pip install -r requirements.txt
```
# How to run: 
```
  python3 process-sleep-data.py; 
```  
  or
```
  streamlit run app.py 
```
  or
```  
  ipython notebook IGalileo.ipynb
```


To get more data linux:
``` 
  wget https://www.dropbox.com/sh/0nz5l0zwcuu7ojf/AADvG7nkUBmT93vrOVnQfj9Ua?dl=0
```
To get more data on OSX:
```
  curl -s -L https://www.dropbox.com/sh/0nz5l0zwcuu7ojf/AADvG7nkUBmT93vrOVnQfj9Ua?dl=0
```

