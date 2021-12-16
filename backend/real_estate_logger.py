#!/usr/bin/env python
# coding: utf-8

# In[2]:


import logging
import logging.config

logging.config.fileConfig(fname='logger_config.conf', disable_existing_loggers=False)
# Get the logger specified in the file
logger = logging.getLogger(__name__)

def getLogger():
    return logger


# In[ ]:




