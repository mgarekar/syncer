import boto3, argparse,os,sys
import subprocess

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
    if (args.upload_download.lower()=='upload'):
        print ("\tlocal --> s3".upper())
        cmd="aws s3 sync {} s3://{}/  --profile priv-acc".format(args.path,args.bucket)
    elif (args.upload_download.lower()=='download'):
        print ("\ts3 --> local".upper())
        cmd = "aws s3 sync s3://{}/ {} --profile priv-acc".format(args.bucket,args.path)
    else:
        print('Enter only upload or download')
        sys.exit(0)

    if (input('\tare you sure? y or n\n'.upper() ) != 'Y'):
        print ('cancelling')
        sys.exit()
    if (args.env != 'work' and args.env != 'home'):
        print ('arguments are not home or work')
        sys.exit()
    returned_args={}
    returned_args['cmd']=cmd
    returned_args['env']=args.env
    returned_args['path']=args.path

    return returned_args

def sync(cmd):
    ''' actual code to push/pull data, ask for confirmation visually'''
    run_command(cmd,debug=True)
    print ('done the sync')

def run_command(cmd,debug=True):
    '''run the damm command using subprocess, prints stderr, stdout, process id'''
    p=subprocess.Popen(cmd,shell = True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding='utf-8')
    stdout,stderr=p.communicate(timeout=60)
    if (debug):
        print ('process id is {}'.format(p.pid))
        print (p.returncode)
        print('stderr is \n{}'.format(stderr))
        print('stdout is \n{}'.format(stdout))

def create_file_marker(path,envron):
    '''Create/re-writes a file at path that identifies the environment. Does not return anuthing, but the contents of the file after creation '''
    print (path)
    print (envron)
    pass
args=parse_args()
# print (args)
create_file_marker(args['path'],args['env'])
sync(args['cmd'])

