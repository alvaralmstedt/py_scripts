#!/usr/bin/python

import subprocess
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-e', '--emails', nargs='+', help='Email list', required=True)
#parser.add_argument('-j', '--job_name', nargs='?', type=str, help="Job name")
parser.add_argument('-u', '--users', nargs='+', help="User list")
parser.add_argument('-i', '--input_thingie', nargs='+', help="Useless argument needed for clc")
parser.add_argument('-s', '--subject', nargs='?', type=str, help="Subject of the email")
parser.add_argument('-b', '--body', nargs='?', type=str, help="Body of the email")

args = parser.parse_args()
emails_input = args.emails
users_input = args.users
#job_name_input = args.job_name
useless_input = args.input_thingie
email_body = args.body
email_subject = args.subject

def email_list_creator(emails, users, body, subject):
    email_list = []
    if len(emails) == len(users):
        for email, user in zip(emails, users):
            email_list.append('From: \"CLC_Workbench_at_medair\" <CLC.Workbench.noreply@medair.sahlgrenska.gu.se>' + '\n' +
                              'To: \"%s\" <%s>' % (user, email) + '\n' +
                              'Subject: %s' % str(subject) + '\n' +
                              'MIME-Version: 1.0' + '\n' +
                              'Content-Type: text/plain' + '\n' +
                              str(body))
    else:
        for email in emails:
            email_list.append('From: \"CLC_Workbench_at_medair\" <CLC.Workbench.noreply@medair.sahlgrenska.gu.se>' + '\n' +
                              'To: \"%s\" <%s>' % (email, email) + '\n' +
                              'Subject: %s' % str(subject) + '\n' +
                              'MIME-Version: 1.0' + '\n' +
                              'Content-Type: text/plain' + '\n' +
                              str(body))
    return email_list


def email_sender(emails):
    for i in emails:
        subprocess.call('echo "%s" | /usr/sbin/sendmail -i -t' % i, shell=True)

email_sender(email_list_creator(emails_input, users_input, email_body, email_subject))
