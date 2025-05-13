import pysftp
import argparse
from environment_variables import create_environment_variables
from date_funcs import *
from communication import *
from paramiko import *

# executes function to create local environment variables defined in environment_variables script.
create_environment_variables()

wife = os.environ['wife']
husband = os.environ['husband']
parser = argparse.ArgumentParser(description="script to call server and back up images from media")
parser.add_argument("-j", help="back up " + wife + "'s phone", action="store_true")
parser.add_argument("-c", help="back up " + husband + "'s phone", action="store_true")
parser.add_argument("-s", "--sort", help="sorts any images placed in C:/usr/red/tmp/{user}", action="store_true")

args = parser.parse_args()

if args.j:
    user = wife
elif args.c:
    user = husband
else:
    parser.print_help()
    exit(1)

host = os.environ['host']
username = os.environ['username']
sender = os.environ['sender']
to = os.environ['to']
private_key_path = os.environ['private_key_path']
media_remote_path = os.environ['media_remote_path'] + user
tmp_local_path = os.environ['tmp_local_path'] + user
media_local_path = os.environ['media_local_path'] + user + "_phone"

try:
    if not args.sort:
        with pysftp.Connection(host=host, username=username, private_key=private_key_path) as sftp:
            with sftp.cd(media_remote_path):
                # Checks to see if user has a tmp directory
                if not os.path.isdir(tmp_local_path):
                    os.mkdir(tmp_local_path)
                if len(sftp.listdir()):
                    for directory in sftp.listdir():
                        # get_d copies all files in directory
                        sftp.get_d(directory, tmp_local_path, preserve_mtime=True)

                        # cd into directory to remove files
                        sftp.chdir(directory)
                        for file in sftp.listdir():
                            if sftp.isdir(file):
                                sftp.rmdir(file)
                            elif sftp.isfile(file):
                                sftp.remove(file)

                        # cd back up .. to remove directory of media
                        sftp.chdir(media_remote_path)
                        sftp.rmdir(directory)
                else:
                    print("no media to back up remotely")
        # Checks to see if user passed has a directory, if not one is made
        if not os.path.isdir(media_local_path):
            os.mkdir(media_local_path)

        sftp.close()

    # cd to desired directory for os.listdir to work
    os.chdir(tmp_local_path)
    if len(os.listdir()):
        for filename in os.listdir(tmp_local_path):
            if not filename.startswith("."):
                year = filename[0:4]
                month = date_converter[filename[4:6]]
                media_local_path_year = media_local_path + "/" + year
                media_local_path_month = media_local_path_year + "/" + month

                if not os.path.isdir(media_local_path_year):
                    os.mkdir(media_local_path_year)

                if not os.path.isdir(media_local_path_month):
                    os.mkdir(media_local_path_month)

                if not os.path.isfile(media_local_path_month + "/" + filename):
                    os.rename(tmp_local_path + "/" + filename, media_local_path_month + "/" + filename)
                else:
                    # removes redundant media
                    os.chdir(tmp_local_path)
                    os.remove(filename)
    else:
        print("no media to sort")
    exit(0)
except (IOError, OSError, KeyError, SFTPError, pysftp.ConnectionException, pysftp.CredentialException,
        pysftp.SSHException, pysftp.AuthenticationException) as error:
    send_email(sender=sender, to=to,
               subject="[Urgent] Photo backup failed for " + user, message_text=str(error))
    print(str(error))
    sftp.close()
    exit(1)


