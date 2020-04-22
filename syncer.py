import boto3, argparse,os,sys
import subprocess
import time

def parse_args():
    ''' Arg Parsing, invalid input handling, and setting global command'''
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--region",help='enter the aws region that you want to work in,\n Default us-east-1',default='us-east-1')
    parser.add_argument("upload_download",help='direction of sync, Enter upload or Download')
    parser.add_argument("--bucket",help='bucket, default is cloud-data',default='cloud-data')
    parser.add_argument("--path",help=' directory for sync',default='~/Documents/cloud-data/')
    parser.add_argument("env",help=' upload source, Valid Values are home, work')
    args=parser.parse_args()
    

    print ('\tregion ||||| is {}'.format(args.region).upper())
    print ('\tsync bucket is {}'.format(args.bucket).upper())
    print ('\tdefault path for sync is {}'.format(args.path))

    #User error for environment
    if (args.env != 'work' and args.env != 'home'):
        print ('arguments are not home or work')
        sys.exit()
    #User error for upload or download
    if (args.upload_download.lower()=='upload'):
        print ("\tlocal --> s3".upper())
        cmd="aws s3 sync {} s3://{}/  --profile priv-acc".format(args.path,args.bucket)
    elif (args.upload_download.lower()=='download'):
        print ("\ts3 --> local".upper())
        cmd = "aws s3 sync s3://{}/ {} --profile priv-acc".format(args.bucket,args.path)
    else:
        print('Enter only upload or download')
        sys.exit(0)

    #If upload, Check last uploader, and warn user to download files if they didn;t already do this.
    if (args.upload_download.lower()=='upload'):
        #Upload command called.
        if args.env == who_is_last_uploader():
            #We were the last uploader. Safe to upload/download:
            print("The last uploader was {}".format(args.env))
        else:
            #Warn user that they are not the previous uploader. Ideally, they should download first, and then upload
            print('WARNING: You are not the last uploader. Did you download the changes when you started? If not, an upload can cause conflicts')
            if (input('\tare you sure? y or n\n'.upper() ) != 'Y'):
                print ('cancelling')
                sys.exit()

    #Ask for final confirmation
    if (input('\tare you sure? y or n\n'.upper() ) != 'Y'):
        print ('cancelling')
        sys.exit()
    


    returned_args={}
    returned_args['cmd']=cmd
    returned_args['env']=args.env
    returned_args['path']=args.path
    returned_args['upload_download']=args.upload_download

    return returned_args


def run_command(cmd,debug=True):
    '''run the damm command using subprocess, prints stderr, stdout, process id'''
    p=subprocess.Popen(cmd,shell = True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding='utf-8')
    stdout,stderr=p.communicate(timeout=60)
    if (debug):
        print ('process id is {}'.format(p.pid))
        print (p.returncode)
        print('stderr is \n{}'.format(stderr))
        print('stdout is \n{}'.format(stdout))
    if stdout:
        return True
    else:
        return False

def create_file_marker_at_upload(bucket,envron):
    '''Create a log at s3bucket2 that identifies the environment
        input: s3bucket2
        output: True/False     
    '''
    bucket='s3://'+bucket+'/syncer/'
    log_time=str(time.time())
    if '.' in log_time:
        log_time=log_time.split('.')[0]
    log_string='{}|||{}'.format(log_time,envron)
    # print (log_string)
    with open('upload.txt','w') as f:
        f.write(log_string)
    #close file, and now upload to s3 bucket
    cmd='aws s3 cp upload.txt {} --profile priv-acc'.format(bucket)
    # print (cmd)
    return run_command(cmd,debug=False)

def who_is_last_uploader():
    '''
    Check s3 at s3://cloudlogd to see who is last uploader. Input -> none, Output -> Last Uploader at time.
    '''
    cmd='aws s3 cp s3://cloudlogd/syncer/upload.txt last_uploader.txt --profile priv-acc'
    if run_command(cmd,debug=False):
        with open('last_uploader.txt','r') as f:
            data=f.read()
            epoch_time,envron=data.split('|||')
            str_time=time.ctime(int(epoch_time))
            print ( 'Last uploader is {} at {}'.format(envron,str_time))
            return envron
            
    else:
        print('Failed to get last uploader status, Exit')
        sys.exit(0)


args=parse_args()

run_command(args['cmd'],debug=True)

if args['upload_download'] == 'upload':
    #if last uploader was same as work station, issue warning, ask user if they donwloaded first
    print ('Updated Upload Marker')
    create_file_marker_at_upload('cloudlogd',args['env'])
