from s3code import AwsS3
from pathlib import Path
from lxml import html
import requests
import re
from db import Dbconnect
import os
import json
from time import sleep
import datetime
import logging

#create and configure log
LOG_FORMAT="%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(
    filename="awsS3DEBUG.log",
    level = logging.ERROR,
    format = LOG_FORMAT,
)
logger=logging.getLogger()

class Maincrawler:
    
    def __init__(self):
        
        #self.query='select distinct lc.id,profile_url from linkedin_contacts lc, linkedin_contact_relationship lcr where lc.id=lcr.contact_id and lcr.contact_type=7'
        #self.result=Dbconnect().query(self.query)
        self.ids=[]
        self.profile_data=[]
        self.linkedin_id=0
        self.active,self.status,self.priority=0,0,0

    def __enter__(self,*g):
        return self
    
    def cleanText(self,bodytext):
        unformatted_text=''.join(bodytext).strip('\n')
        final_text=re.sub('\s\s+', ' ',unformatted_text)
        return final_text

    def get_text(self,tree,xpath):
        textdata=''
        textdata_text=tree.xpath(xpath)
        if textdata_text:
            #print (textdata_text[0].text)
            textdata=self.cleanText(textdata_text[0].text)
        return textdata

    def get_list(self,tree,xpath):
        bodytext= [data.text for data in tree.xpath(xpath)]
        final_text=self.cleanText(bodytext)
        return final_text
    
    def get_profile_spl(self,tree,xpath):
        try:
            #contents=filey.read()
            #tree=html.fromstring(contents)
            sumry=''
            stored_data=tree.xpath(xpath)[0].text
            stored_data=json.loads(stored_data)
            for dic in stored_data['included']:
                if 'summary' in dic:
                    sumry=self.cleanText(dic.get('summary'))
                    return sumry
            return sumry
        except Exception as e:
            logger.error('Get profile special function : '+str(e))
            print (e)

    def fetch_which_to_crawl(self):
        try:
            where_condition=''
            q='select id,where_condition,config,priority from awsS3Status where active=1 and status=1 order by priority desc limit 1'
            res=Dbconnect().query(q)
            if res:
                try:
                    self.linkedin_id,where_condition,config,self.priority=res[0]
                except:
                    self.linkedin_id,config=res[0]
            else:
                print('result list is none')
        except Exception as e:
            logger.error('Error in which to crawl function : '+str(e))
            u_qry='update awsS3Status set active={},status={},end_date="{}",exceptions="{}" where id={}'.format(0,4,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(e),self.linkedin_id)
            Dbconnect().update_query(u_qry)
            print(e)
        #self.query='select distinct lc.id,profile_url from linkedin_contacts lc, linkedin_contact_relationship lcr '
        self.query='select distinct lc.id,profile_url from linkedin_contacts lc, linkedin_contact_relationship lcr where lcr.contact_id=lc.id and '+where_condition
        try:
            self.result=Dbconnect().query(self.query)
            self.ids=[ tup for tup in self.result ]
            config=json.loads(config)
            self.startCrawl(config)
        except Exception as e:
            u_qry='update awsS3Status set priority={},active={},status={},start_date="{}",end_date="{}",exceptions="{}" where id={}'.format(0,0,4,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(e),self.linkedin_id)
            Dbconnect().update_query(u_qry)
            print(e)
        

    def startCrawl(self,config):
        try:
            #local_priority=self.priority
            u_qry='update awsS3Status set priority={},status={},start_date="{}" where id={}'.format(0,2,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.linkedin_id)
            Dbconnect().update_query(u_qry)
            for id,url in self.ids:
                try:
                    tree=None
                    print('id={}  url={}'.format(id,url))
                    id=str(id)
                    path_to_html_file=str(Path().absolute())+'/htmls/'+id+'profile.html'
                    try:
                        with AwsS3('linkedin-info') as server:
                            server.download_file(id)
                    except Exception as e:
                        print("Error in downloading..",e)
                        logger.error('Error in downloading files: '+str(e))
                        continue
                    try:
                        f=open(path_to_html_file,'r')
                        contents=f.read()
                        tree=html.fromstring(contents)
                    except Exception as e:
                        logger.error('Error in For reading html file: '+str(e))
                        print(e)
                        continue
                    print(config)
                    print(type(config))
                    final_text=''
                    if config['fieldname']=='profile_summary':
                        final_text=self.get_profile_spl(tree,config['xpath'])
                    else:
                        final_text=self.get_text(tree,config['xpath'])
                    print("final text: ",final_text)
                    query='update linkedin_contacts set {} = "{}" where id={}'.format(config['fieldname'],final_text,id)
                    print(query)
                    Dbconnect().update_query(query)
                    u_qry='update awsS3Status set active={},status={},end_date="{}" where id={}'.format(0,3,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.linkedin_id)
                    Dbconnect().update_query(u_qry)
                    f.close()
                except Exception as e:
                    print("exception in for loop---------->",e)
                    u_qry='update awsS3Status set active={},status={},end_date="{}",exceptions="{}" where id={}'.format(0,4,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(e),self.linkedin_id)
                    Dbconnect().update_query(u_qry)
                    logger.error('Error in For loop: '+str(e))
                finally:
                    if os.path.exists(path_to_html_file):
                        os.remove(path_to_html_file)
        except Exception as e:
            u_qry='update awsS3Status set active={},status={},end_date="{}",exceptions="{}" where id={}'.format(0,4,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(e),self.linkedin_id)
            Dbconnect().update_query(u_qry)
            print(e)
            logger.error('Error in whole program: '+str(e))


    def __exit__(self, exception_type, exception_value, traceback):
        print("exception_type: ", exception_type)
        print("exception_value: ", exception_value)
           


#idee=input("Enter ID to crawl: ")
while True:
    try:
        with Maincrawler() as crawler:
            crawler.fetch_which_to_crawl()
    except Exception as e:
        print(e)
        logger.info(str(e))
    sleep(60)