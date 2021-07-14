#!/usr/bin/env python
# coding: utf-8

# In[4]:


import re
from string import Template


# In[5]:


#template class
#extract the elements from all kinds of derivatives' tickers
class TemplateMatcher(object):
    numElements = 0 #number of elements can be extracted
    regEx = '' #reggular expression of the ticker

    #compile the regEx
    def pattern(cls):
        reg = re.compile(cls.regEx)
        return reg
    
    #match the ticker and extract elements if valid
    def matcher(cls, ticker):
        elements = []
        result = cls.pattern().match(ticker)
        if result:
            for i in range(cls.numElements):
                elements.append(result.group(i+1))
            return elements 
        return "Invalid ticker"
            
    def list_to_str(List):
        string = ''
        for char in List:
            string=string+char+'|'
        return string[:-1]


# In[6]:


#extract the elements from ir-swap ticker
class IRSwapMathcer(TemplateMatcher):
    ccy = ['us', 'bp']
    swap = ['ois', 'ff']
    ccy = TemplateMatcher.list_to_str(ccy)
    swap = TemplateMatcher.list_to_str(swap)
    forward = '\d+[ymwb]'
    maturity = '\d+[ymwb]'
    template = Template('($ccy)($swap)($forward)?($maturity)')
    dict = {'ccy':ccy, 'swap':swap, 'forward':forward, 'maturity':maturity}
    numElements = len(dict) 
    regEx = template.substitute(dict)


# In[7]:


if __name__ == '__main__':
    for ticker in ['usois10y', 'bpff5y10y', 'ussw10x']:
        IRS = IRSwapMathcer().matcher(ticker)
        print(IRS)


# In[ ]:




