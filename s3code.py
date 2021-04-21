import boto3, os
import datetime
from pathlib import Path



class AwsS3(object):
    """docstring for AwsS3"""
    def __init__(self,bucket):
        super(AwsS3, self).__init__()
        self.bucket = bucket
        #print('bucket_name: ',self.bucket)
        
    def __enter__(self,*_):
        return self

    def __exit__(self,*_):
        pass

    def upload_file(self,local_path,s3_path):
        '''
        '''
        try:
            s3 = boto3.resource('s3')
            s3.meta.client.upload_file(local_path, self.bucket, s3_path)
            return True
        except Exception as e:
            raise Exception("error inside bucket code:  "+str(e))
    
    def download_file(self,id):
        try:
            s3 = boto3.resource('s3')
            serverpath=str(id)+'/ProfileHtml/ProfileDetails.html'
            localpath=str(Path().absolute())+'/htmls/'+str(id)+'profile.html'
            #print(serverpath+' '+localpath)
            s3.meta.client.download_file(self.bucket, serverpath , localpath)
        except Exception as e:
            print(e)   


#server=AwsS3('linkedin-info')
#server.download_file(14)


    # def uploadFile(self,upload_file,firm_name,court_id):
    # 	""" """
    # 	# SUCCESS = False
    # 	try:
    # 		date = datetime.datetime.strftime(datetime.datetime.now(),'%d-%m-%Y-%H-%M-%s')
    # 		# date = str(date)
    # 		print(upload_file,firm_name,court_id)
    # 		file_name = "_".join([court_id,firm_name,date+'.html'])
    # 		print('file_name:::',file_name)
    # 		s3 = boto3.resource('s3')
    # 		s3.meta.client.upload_file(upload_file, self.bucket, file_name)
    # 	except Exception as e:
    # 		print("Document Not Downloaded",e)
    # 		# raise


    # def upload_linkedin_image(self,upload_file,firm_name,court_id):
    # 	try:
    # 		print("upload_linkedin_image---->>>>")
    # 		date = datetime.datetime.strftime(datetime.datetime.now(),'%d-%m-%Y-%H-%M-%s')
    # 		file_name = "_".join([court_id,firm_name,date+'.jpg'])
    # 		print("FILE NAME------>>>>>>",file_name)
    # 		s3 = boto3.resource('s3')
    # 		s3.meta.client.upload_file(upload_file, self.bucket, file_name)
    # 		print("SUCCESSFULLY upload_file")
    # 		return file_name
    # 	except Exception as e:
    # 		print("Document Not Downloaded for upload_linkedin_image",e)
    # 		raise

def test():
    pass


if __name__ == '__main__':
    test()
