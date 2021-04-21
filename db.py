import mysql.connector
import logging

#create and configure log
LOG_FORMAT="%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(
    filename="awsS3DEBUG.log",
    level = logging.ERROR,
    format = LOG_FORMAT,
)
logger=logging.getLogger()

class Dbconnect:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                user='',
                password='',
                host='',
                database='')
            if self.connection.is_connected():
                self.db_Info = self.connection.get_server_info()
                print("Connected to MySQL database... MySQL Server version on ",self.db_Info)
                self.mycursor = self.connection.cursor()
                self.mycursor.execute("select database();")
                self.myrecord = self.mycursor.fetchone()
                print ("Your connected to - ", self.myrecord)
        except Exception as e:
            logger.critical('Error in connecting to mysql: '+str(e))
        
    def query(self,string,t=None):
        print("insie Dbconnect")
        try:
            print(string)
            if t is not None:
                self.mycursor.execute(string,t)
                self.mycursor.execute("commit")
                self.connection.commit
                self.connection.close()
            else:
                self.mycursor.execute(string)
                self.records=self.mycursor.fetchall()
                self.connection.close()
                return self.records
        except Exception as e :
            print ("Error while connecting to MySQL: ", e)
            logger.critical('Error in making query to mysql: '+str(e))

    def update_query(self,string):
        try:
            self.mycursor.execute(string)
            self.mycursor.execute("commit")
            self.connection.commit
            self.connection.close()
        except Exception as e :
            print ("Error while doing update query: ", e)
            logger.critical('Error while doing update query: '+str(e))
            
#string="CREATE TABLE court (ID int NOT NULL PRIMARY KEY,state VARCHAR(50),county_name VARCHAR(50),county_url VARCHAR(255))"
#string='insert into court (state,county_name,court_name,court_url) values ("Alabama","test","none","None")'
#Dbconnect.query(string)

#string=checkpoint='select j.judge_id,j.profile_url,j.location_id from judge j, profile p where p.profile_id>(select max(profile_id) from profile)'
#result=Dbconnect.query(string)
#for i in result:
#    print(i)
#print(result)
#if not result:
#    print("list is empty")
