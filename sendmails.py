#!/usr/bin/python

import subprocess
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-e', '--emails', nargs='+', help='Email list', required=True)
parser.add_argument('-j', '--job_name', nargs='?', type=str, help="Job name")
parser.add_argument('-u', '--users', nargs='+', help="User list")

args = parser.parse_args()
emails_input = args.emails
users_input = args.users
job_name_input = args.job_name


def email_list_creator(emails, users, job):
    email_list = []
    if len(emails) == len(users):
        for email, user in zip(emails, users):
            email_list.append('From: \"CLC_Workbench_at_medair\" <CLC.Workbench.noreply@medair.sahlgrenska.gu.se>' + '\n' +
                              'To: \"%s\" <%s>' % (user, email) + '\n' +
                              'Subject: Your CLC job %s has finished!' % job + '\n' +
                              'MIME-Version: 1.0' + '\n' +
                              'Content-Type: text/plain' + '\n' +
                              'Work Complete!' + '\n' +
                              '%s finished at `date`' % job)
    else:
        for email in emails:
            email_list.append('From: \"CLC_Workbench_at_medair\" <CLC.Workbench.noreply@medair.sahlgrenska.gu.se>' + '\n' +
                              'To: \"%s\" <%s>' % (email, email) + '\n' +
                              'Subject: Your CLC job %s has finished!' % job + '\n' +
                              'MIME-Version: 1.0' + '\n' +
                              'Content-Type: text/plain' + '\n' +
                              'Work Complete!' + '\n' +
                              '%s finished at `date`' % job)
    return email_list


def email_sender(emails):
    for i in emails:
        subprocess.call('echo %s | sendmail -i -t' % i)

email_sender(email_list_creator(emails_input, users_input, job_name_input))