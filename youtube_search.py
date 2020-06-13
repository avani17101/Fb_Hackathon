#!/usr/bin/env python
# coding: utf-8

# In[6]:



def find_related_urls(title):
    """
    biggest innovation!
    args: title of article
    returns: links of  most related articles from trusted sources
    """
    try: 
        from googlesearch import search 
    except ImportError:  
        print("No module named 'google' found") 
    
    print(title)
    related_urls = []
    # to search 
    query1 = "youtube: "+ title
    print("Sugesstion")
    for q in search(query1, tld="com", num=10, stop=1, pause=2): 
        print(q)
        related_urls.append(q)
    return related_urls
        


# In[7]:


# file = open("user_query.txt") #file containes the topic user wants to read
query = "Soothing music for depression"
find_related_urls(query)

