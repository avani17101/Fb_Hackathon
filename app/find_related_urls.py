def find_related_urls(title,website):
    """
    args: title of article
    returns: links of  most related articles
    """
    try: 
        from googlesearch import search 
    except ImportError:  
        print("No module named 'google' found") 
    
    print(title)
    related_urls = []
    # to search 
    query1 = website + title
    print("Sugesstion")
    for q in search(query1, tld="com", num=10, stop=1, pause=2): 
        print(q)
        related_urls.append(q)
    return related_urls