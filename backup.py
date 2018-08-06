import datetime
import smtplib
import subprocess as sp
from datetime import datetime
from shutil import move


def send_mail():
    log_file = open('/var/log/website_backup.log', 'r')
    log_msg = log_file.read()
    mail_srv = 'mail.novusgroup.co.za'
    mail_port = '25'
    mail_name = 'website_backup@novusgroup.co.za'
    mail_recip = ['itmonitor@novusgroup.co.za']
    smtpServ = smtplib.SMTP(mail_srv, mail_port)
    smtpServ.sendmail(mail_name, mail_recip, log_msg)
    log_file.close()
    smtpServ.quit()
    print('Sending email notification to: %s' % mail_recip)


def log(data, timestamp):
    with open('/var/log/website_backup.log', 'a') as log_file:
        log_file.write(timestamp)
        log_file.write(str(data))
        log_file.write('\n')


def sync():
    timestamp = str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    datestamp = str(datetime.now().strftime('%d-%m-%Y'))
    ftp_server = 'ip_address_goes_here'
    ftp_user = 'username_goes_here'
    ftp_pass = 'supersecret_pass_goes_here'
    source_dir = 'public_html'
    target_dir = '/tmp/website/'
    tar_dir = target_dir + source_dir
    backup_dir = '/mnt/website/'

    print()
    print('%s  starting ftp sync' % timestamp)

    connect = 'lftp -u {},{} -e "mirror -v {} {}" -p 21 {}  <<-EOF'.format(ftp_user, ftp_pass, source_dir, target_dir, ftp_server)
    res = sp.Popen(connect,shell=True,stdout=sp.PIPE,stderr=sp.PIPE)
    output, error = res.communicate()
    output = output.decode('ascii')
    error = error.decode('ascii')
    if output:
        print('{}  Backing up the website'.format(timestamp))
        print(str(output))
        log(output, timestamp)

    if error:
        print('{} Error message'.format(timestamp))
        print(str(error))
        log(error, timestamp)
        send_mail()
        with open('/var/log/website_backup_notification.log', 'w') as file:
            file.write('failed')

    else:
        archive = 'tar -cjf /tmp/website/{}_website.tar.bz2 {}'.format(datestamp, tar_dir)
        res = sp.Popen(archive,shell=True,stdout=sp.PIPE,stderr=sp.PIPE)
        output, error = res.communicate()
        output = output.decode('ascii')
        error = error.decode('ascii')
        if output:
            print(str(output))

        if error:
            print(str(error))

        move('/tmp/website/' + datestamp + '_website.tar.bz2', backup_dir)

        print('%s backup process complete!' % timestamp)
        with open('/var/log/website_backup_notification.log', 'w') as file:
            file.write('success')


if __name__ == '__main__':
   sync()
