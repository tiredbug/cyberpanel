import sys
import subprocess
import shutil
import installLog as logging
import argparse
import os
import shlex
from firewallUtilities import FirewallUtilities
import time
import platform



class preFlightsChecks:

    cyberPanelMirror = "mirror.cyberpanel.net"

    def __init__(self,rootPath,ip,path,cwd,cyberPanelPath):
        self.ipAddr = ip
        self.path = path
        self.cwd = cwd
        self.server_root_path = rootPath
        self.cyberPanelPath = cyberPanelPath

    @staticmethod
    def stdOut(message):
        print("\n\n")
        print ("[" + time.strftime(
            "%I-%M-%S-%a-%b-%Y") + "] #########################################################################\n")
        print("[" + time.strftime("%I-%M-%S-%a-%b-%Y") + "] " + message + "\n")
        print ("[" + time.strftime(
            "%I-%M-%S-%a-%b-%Y") + "] #########################################################################\n")

    def checkIfSeLinuxDisabled(self):
        try:
            command = "sestatus"
            output = subprocess.check_output(shlex.split(command))

            if output.find("disabled") > -1 or output.find("permissive") > -1:
                logging.InstallLog.writeToFile("SELinux Check OK. [checkIfSeLinuxDisabled]")
                preFlightsChecks.stdOut("SELinux Check OK.")
                return 1
            else:
                logging.InstallLog.writeToFile("SELinux is enabled, please disable SELinux and restart the installation!")
                preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                sys.exit()
                return 0

        except BaseException,msg:
            logging.InstallLog.writeToFile(str(msg) + "[checkIfSeLinuxDisabled]")
            logging.InstallLog.writeToFile("SELinux Check OK. [checkIfSeLinuxDisabled]")
            preFlightsChecks.stdOut("SELinux Check OK.")
            return 1

    def checkPythonVersion(self):
        if sys.version_info[0] == 2 and sys.version_info[1] == 7:
            return 1
        else:
            preFlightsChecks.stdOut("You are running Unsupported python version, please install python 2.7")
            sys.exit()

    def setup_account_cyberpanel(self):
        try:
            count = 0

            while (1):
                command = "yum install sudo -y"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("SUDO install failed, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("We are not able to install SUDO, exiting the installer. [setup_account_cyberpanel]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("SUDO successfully installed!")
                    preFlightsChecks.stdOut("SUDO successfully installed!")
                    break

            ##

            count = 0

            while (1):
                command = "adduser cyberpanel"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Not able to add user cyberpanel to system, trying again, try number: " + str(count) + "\n")
                    if count == 3:
                        logging.InstallLog.writeToFile("We are not able add user cyberpanel to system, exiting the installer. [setup_account_cyberpanel]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("CyberPanel user added!")
                    preFlightsChecks.stdOut("CyberPanel user added!")
                    break

            ##

            count = 0

            while (1):

                command = "usermod -aG wheel cyberpanel"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("We are trying to add CyberPanel user to SUDO group, trying again, try number: " + str(count) + "\n")
                    if count == 3:
                        logging.InstallLog.writeToFile("Not able to add user CyberPanel to SUDO group, exiting the installer. [setup_account_cyberpanel]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("CyberPanel user was successfully added to SUDO group!")
                    preFlightsChecks.stdOut("CyberPanel user was successfully added to SUDO group!")
                    break


            ###############################

            path = "/etc/sudoers"

            data = open(path, 'r').readlines()

            writeToFile = open(path, 'w')

            for items in data:
                if items.find("wheel    ALL=(ALL)   NOPASSWD: ALL") > -1:
                    writeToFile.writelines("%wheel  ALL=(ALL)   NOPASSWD: ALL")
                else:
                    writeToFile.writelines(items)

            writeToFile.close()

            ###############################

            count = 0

            while (1):

                pathLetsEncrypt = "/etc/letsencrypt"
                if os.path.exists(pathLetsEncrypt):
                    os.remove(pathLetsEncrypt)

                command = "mkdir /etc/letsencrypt"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("We are trying to create Let's Encrypt directory to store SSLs, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Failed to create Let's Encrypt directory to store SSLs. Installer can continue without this.. [setup_account_cyberpanel]")
                else:
                    logging.InstallLog.writeToFile("Successfully created Let's Encrypt directory!")
                    preFlightsChecks.stdOut("Successfully created Let's Encrypt directory!")
                    break

            ##

        except:
            logging.InstallLog.writeToFile("[116] setup_account_cyberpanel")

    def yum_update(self):
        try:
            count = 0
            while (1):

                command = 'yum update -y'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("YUM UPDATE FAILED, trying again, try number: " + str(count) + "\n")
                    if count == 3:
                        logging.InstallLog.writeToFile("YUM update failed to run, we are being optimistic that installer will still be able to complete installation. [yum_update]")
                        break
                else:
                    logging.InstallLog.writeToFile("YUM UPDATE ran successfully.")
                    preFlightsChecks.stdOut("YUM UPDATE ran successfully.")
                    break


        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [yum_update]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [yum_update]")
            return 0

        return 1

    def installCyberPanelRepo(self):

        cmd = []

        count = 0

        while(1):
            if version >= 7:
                command = 'curl -o /etc/yum.repos.d/litespeed.repo https://'+preFlightsChecks.cyberPanelMirror+'/litespeed/litespeed.repo'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)
            elif version >= 6:
                cmd.append("rpm")
                cmd.append("-ivh")
                cmd.append("https://rpms.litespeedtech.com/centos/litespeed-repo-1.1-1.el6.noarch.rpm")
                res = subprocess.call(cmd)

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to add CyberPanel official repository, trying again, try number: " + str(count) + "\n")
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to add CyberPanel official repository, exiting installer! [installCyberPanelRepo]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("CyberPanel Repo added!")
                preFlightsChecks.stdOut("CyberPanel Repo added!")
                break

    def enableEPELRepo(self):
        try:

            command = "yum list installed | grep epel-release"
            cmd = shlex.split(command)
            output = subprocess.check_output(cmd)

            cmd = []

            count = 0

            while (1):
                if output.find("epel") > -1:
                    res = 0
                elif version >= 7:
                    cmd.append("yum")
                    cmd.append("-y")
                    cmd.append("install")
                    cmd.append("epel-release")
                    res = subprocess.call(cmd)
                elif version >= 6:
                    cmd.append("rpm")
                    cmd.append("-ivh")
                    cmd.append("https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm")
                    res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to add EPEL repository, trying again, try number: " + str(count) + "\n")
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to add EPEL repository, exiting installer! [enableEPELRepo]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                else:
                    logging.InstallLog.writeToFile("EPEL Repo added!")
                    preFlightsChecks.stdOut("EPEL Repo added!")
                    break

        except OSError,msg:
            logging.InstallLog.writeToFile(str(msg) + " [enableEPELRepo]")
            return 0
        except ValueError,msg:
            logging.InstallLog.writeToFile(str(msg) + " [enableEPELRepo]")
            return 0

        return 1

    def install_pip(self):
        count = 0

        while (1):
            if os.path.exists("/usr/local/bin/pip") or os.path.exists("/usr/bin/pip"):
                break

            command = '''yum -y install python-pip || (yum install groupinstall "Development Tools" -y && yum install python-devel python-setuptools -y && easy_install pip)'''
            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to install PIP, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to install PIP, exiting installer! [install_pip]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("PIP successfully installed!")
                preFlightsChecks.stdOut("PIP successfully installed!")
                break

    def install_python_dev(self):
        count = 0
        while (1):
            command = "yum -y install python-devel"
            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("We are trying to install python development tools, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to install python development tools, exiting installer! [install_python_dev]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("Python development tools successfully installed!")
                preFlightsChecks.stdOut("Python development tools successfully installed!")
                break

    def install_gcc(self):
        count = 0

        while (1):
            command = "yum -y install gcc"
            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to install GCC, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to install GCC, exiting installer! [install_gcc]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("GCC Successfully installed!")
                preFlightsChecks.stdOut("GCC Successfully installed!")
                break

    def install_python_setup_tools(self):
        count = 0
        while (1):
            command = "yum -y install python-setuptools"
            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                print("[" + time.strftime(
                    "%I-%M-%S-%a-%b-%Y") + "] " + "Unable to install Python setup tools, trying again, try number: " + str(
                    count) + "\n")
                if count == 3:
                    logging.InstallLog.writeToFile(
                        "Unable to install Python setup tools, exiting installer! [install_python_setup_tools]")
                    print("[" + time.strftime(
                        "%I-%M-%S-%a-%b-%Y") + "] " + "Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("Python setup tools Successfully installed!")
                print("[" + time.strftime("%I-%M-%S-%a-%b-%Y") + "] " + "Python setup tools Successfully installed!")
                break

    def install_python_requests(self):
        try:
            import requests

            ## Un-install ULRLIB3 and requests

            command = "pip uninstall --yes urllib3"
            res = subprocess.call(shlex.split(command))

            command = "pip uninstall --yes requests"
            res = subprocess.call(shlex.split(command))


            ## Install specific versions

            count = 0
            while (1):

                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/urllib3-1.22.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut(
                        "Unable to install urllib3 module, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Unable to install urllib3 module, exiting installer! [install_python_requests]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("urllib3 module Successfully installed!")
                    preFlightsChecks.stdOut("urllib3 module Successfully installed!")
                    break

            count = 0
            while (1):

                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/requests-2.18.4.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut(
                        "Unable to install requests module, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Unable to install requests module, exiting installer! [install_python_requests]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("Requests module Successfully installed!")
                    preFlightsChecks.stdOut("Requests module Successfully installed!")
                    break

        except:

            count = 0
            while (1):

                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/urllib3-1.22.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut(
                        "Unable to install urllib3 module, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Unable to install urllib3 module, exiting installer! [install_python_requests]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("urllib3 module Successfully installed!")
                    preFlightsChecks.stdOut("urllib3 module Successfully installed!")
                    break

            count = 0
            while (1):

                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/requests-2.18.4.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut(
                        "Unable to install requests module, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Unable to install requests module, exiting installer! [install_python_requests]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("Requests module Successfully installed!")
                    preFlightsChecks.stdOut("Requests module Successfully installed!")
                    break

    def install_pexpect(self):
        try:
            import pexpect

            command = "pip uninstall --yes pexpect"
            res = subprocess.call(shlex.split(command))

            count = 0

            while (1):
                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/pexpect-4.4.0.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install pexpect, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install pexpect, exiting installer! [install_pexpect]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("pexpect successfully installed!")
                    preFlightsChecks.stdOut("pexpect successfully installed!")
                    break

        except:
            count = 0
            while (1):
                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/pexpect-4.4.0.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install pexpect, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install pexpect, exiting installer! [install_pexpect]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("pexpect successfully installed!")
                    preFlightsChecks.stdOut("pexpect successfully installed!")
                    break

    def install_django(self):
        count = 0
        while (1):
            command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/Django-1.11.10.tar.gz"

            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to install DJANGO, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to install DJANGO, exiting installer! [install_django]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("DJANGO successfully installed!")
                preFlightsChecks.stdOut("DJANGO successfully installed!")
                break

    def install_python_mysql_library(self):
        count = 0
        while (1):
            command = "yum -y install MySQL-python mysql-devel"
            res = subprocess.call(shlex.split(command))
            if res != 1:
                command = "pip install mysql-python"
                res = subprocess.call(shlex.split(command))
            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to install MySQL-python, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to install MySQL-python, exiting installer! [install_python_mysql_library]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("MySQL-python successfully installed!")
                preFlightsChecks.stdOut("MySQL-python successfully installed!")
                break

    def install_gunicorn(self):
        count = 0
        while (1):
            command = "easy_install gunicorn"
            res = subprocess.call(shlex.split(command))
            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to install GUNICORN, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to install GUNICORN, exiting installer! [install_gunicorn]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("GUNICORN successfully installed!")
                preFlightsChecks.stdOut("GUNICORN successfully installed!")
                break

    def setup_gunicorn(self):
        try:

            os.chdir(self.cwd)

            ##

            logging.InstallLog.writeToFile("Configuring Gunicorn..")

            if version >= 7:
                service = "/etc/systemd/system/gunicorn.service"
                socket = "/etc/systemd/system/gunicorn.socket"
                conf = "/etc/tmpfiles.d/gunicorn.conf"
                shutil.copy("gun-configs/gunicorn.service",service)
                shutil.copy("gun-configs/gunicorn.socket",socket)
                shutil.copy("gun-configs/gunicorn.conf", conf)
            elif version >= 6:
                service = "/etc/init.d/gunicorn"
                shutil.copy("gun-configs/gunicorn",service)
                command = "chmod +x /etc/init.d/gunicorn"
                res = subprocess.call(shlex.split(command))

            logging.InstallLog.writeToFile("Gunicorn Configured!")

            ### Enable at system startup

            count = 0

            while(1):
            
                if version >= 7:
                    command = "systemctl enable gunicorn.socket"
                elif version >= 6:
                    command = "chkconfig --add gunicorn"
                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to enable Gunicorn at system startup, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Gunicorn will not start after system restart, you can manually enable using systemctl enable gunicorn.socket! [setup_gunicorn]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        break
                else:
                    logging.InstallLog.writeToFile("Gunicorn can now start after system restart!")
                    preFlightsChecks.stdOut("Gunicorn can now start after system restart!")
                    break

            ##

            count = 0

            while(1):
                if version >= 7:
                    command = "systemctl start gunicorn.socket"
                elif version >= 6:
                    command = "service gunicorn start"
                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Starting Gunicorn now, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to start Gunicorn, exiting installer! [setup_gunicorn]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("Gunicorn successfully started!")
                    preFlightsChecks.stdOut("Gunicorn successfully started!")
                    break

        except BaseException, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setup_gunicorn]")
            preFlightsChecks.stdOut("Not able to setup gunicorn, see install log.")

    def install_psutil(self):

        try:
            import psutil

            ##

            command = "pip uninstall --yes psutil"
            res = subprocess.call(shlex.split(command))

            count = 0
            while (1):
                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/psutil-5.4.3.tar.gz"
                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install psutil, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install psutil, exiting installer! [install_psutil]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("psutil successfully installed!")
                    preFlightsChecks.stdOut("psutil successfully installed!")
                    break

        except:
            count = 0
            while (1):
                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/psutil-5.4.3.tar.gz"
                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install psutil, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install psutil, exiting installer! [install_psutil]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("psutil successfully installed!")
                    preFlightsChecks.stdOut("psutil successfully installed!")
                    break

    def fix_selinux_issue(self):
        try:
            cmd = []

            cmd.append("setsebool")
            cmd.append("-P")
            cmd.append("httpd_can_network_connect")
            cmd.append("1")

            res = subprocess.call(cmd)

            if res == 1:
                logging.InstallLog.writeToFile("fix_selinux_issue problem")
            else:
                pass
        except:
            logging.InstallLog.writeToFile("fix_selinux_issue problem")

    def install_psmisc(self):
        count = 0
        while (1):
            command = "yum -y install psmisc"
            res = subprocess.call(shlex.split(command))
            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to install psmisc, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to install psmisc, exiting installer! [install_psmisc]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("psmisc successfully installed!")
                preFlightsChecks.stdOut("psmisc successfully installed!")
                break

    def download_install_CyberPanel(self,mysqlPassword):
        try:
            ## On OpenVZ there is an issue with requests module, which needs to upgrade requests module

            if subprocess.check_output('virt-what').find("openvz")>-1:
                count = 0
                while(1):
                    command = "pip install --upgrade https://"+preFlightsChecks.cyberPanelMirror+"/pip/requests-2.18.4.tar.gz"
                    res = subprocess.call(shlex.split(command))

                    if res == 1:
                        count = count + 1
                        preFlightsChecks.stdOut("Unable to upgrade requests, trying again, try number: " + str(count))
                        if count == 3:
                            logging.InstallLog.writeToFile("Unable to install upgrade requests, exiting installer! [download_install_CyberPanel]")
                            preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                            sys.exit()
                    else:
                        logging.InstallLog.writeToFile("requests module successfully upgraded!")
                        preFlightsChecks.stdOut("requests module successfully upgraded!")
                        break
        except:
            pass

        ##

        os.chdir(self.path)

        count = 0
        while (1):
            command = "git clone https://github.com/jimorsm/cyberpanel.git"
            #command = "wget http://cyberpanel.net/CyberPanelTemp.tar.gz"
            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to download CyberPanel, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to download CyberPanel, exiting installer! [download_install_CyberPanel]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("CyberPanel successfully downloaded!")
                preFlightsChecks.stdOut("CyberPanel successfully downloaded!")
                break

        ##

        count = 0
        while(1):
            command = "mv cyberpanel CyberCP"
            #command = "tar zxf CyberPanelTemp.tar.gz"

            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to extract CyberPanel, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to extract CyberPanel. You can try to install on fresh OS again, exiting installer! [download_install_CyberPanel]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("Successfully extracted CyberPanel!")
                preFlightsChecks.stdOut("Successfully extracted CyberPanel!")
                break



        ### update password:

        passFile = "/etc/cyberpanel/mysqlPassword"

        f = open(passFile)
        data = f.read()
        password = data.split('\n', 1)[0]

        ### Put correct mysql passwords in settings file!

        logging.InstallLog.writeToFile("Updating settings.py!")

        path = self.cyberPanelPath+"/CyberCP/settings.py"

        data = open(path, "r").readlines()

        writeDataToFile = open(path, "w")

        counter = 0

        for items in data:
            if items.find("'PASSWORD':") > -1:
                if counter == 0:
                    writeDataToFile.writelines("        'PASSWORD': '" + mysqlPassword + "'," + "\n")
                    counter = counter + 1
                else:
                    writeDataToFile.writelines("        'PASSWORD': '" + password + "'," + "\n")

            else:
                writeDataToFile.writelines(items)

        writeDataToFile.close()

        logging.InstallLog.writeToFile("settings.py updated!")

        ### Applying migrations


        os.chdir("CyberCP")

        count = 0

        while(1):
            command = "python manage.py makemigrations"
            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to prepare migrations file, trying again, try number: " + str(count) + "\n")
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to prepare migrations file. You can try to install on fresh OS again, exiting installer! [download_install_CyberPanel]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("Successfully prepared migrations file!")
                preFlightsChecks.stdOut("Successfully prepared migrations file!")
                break

        ##

        count = 0

        while(1):
            command = "python manage.py migrate"

            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to execute the migrations file, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to execute the migrations file, exiting installer! [download_install_CyberPanel]")
                    preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                    sys.exit()
            else:
                logging.InstallLog.writeToFile("Migrations file successfully executed!")
                preFlightsChecks.stdOut("Migrations file successfully executed!")
                break

        ## Moving static content to lscpd location
        command = 'mv static /usr/local/lscp/cyberpanel'
        cmd = shlex.split(command)
        res = subprocess.call(cmd)

        if res == 1:
            logging.InstallLog.writeToFile("Could not move static content!")
            preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
            sys.exit()
        else:
            logging.InstallLog.writeToFile("Static content moved!")
            preFlightsChecks.stdOut("Static content moved!")


        ## fix permissions

        count = 0

        while(1):
            command = "chmod -R 744 /usr/local/CyberCP"
            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Changing permissions for '/usr/local/CyberCP' failed, trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to change permissions for '/usr/local/CyberCP', we are being optimistic that it is still going to work :) [download_install_CyberPanel]")
                    break
            else:
                logging.InstallLog.writeToFile("Permissions successfully changed for '/usr/local/CyberCP'")
                preFlightsChecks.stdOut("Permissions successfully changed for '/usr/local/CyberCP'")
                break

        ## change owner

        count = 0
        while(1):
            command = "chown -R cyberpanel:cyberpanel /usr/local/CyberCP"
            res = subprocess.call(shlex.split(command))

            if res == 1:
                count = count + 1
                preFlightsChecks.stdOut("Unable to change owner for '/usr/local/CyberCP', trying again, try number: " + str(count))
                if count == 3:
                    logging.InstallLog.writeToFile("Unable to change owner for '/usr/local/CyberCP', we are being optimistic that it is still going to work :) [download_install_CyberPanel]")
                    break
            else:
                logging.InstallLog.writeToFile("Owner for '/usr/local/CyberCP' successfully changed!")
                preFlightsChecks.stdOut("Owner for '/usr/local/CyberCP' successfully changed!")
                break


    def install_unzip(self):
        try:

            count = 0

            while (1):
                command = 'yum -y install unzip'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install unzip, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install unzip, exiting installer! [install_unzip]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("unzip successfully installed!")
                    preFlightsChecks.stdOut("unzip Successfully installed!")
                    break


        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_unzip]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_unzip]")
            return 0

        return 1

    def install_zip(self):
        try:

            count = 0

            while (1):

                command = 'yum -y install zip'

                cmd = shlex.split(command)

                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install zip, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install zip, exiting installer! [install_zip]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("zip successfully installed!")
                    preFlightsChecks.stdOut("zip successfully installed!")
                    break


        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_zip]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_zip]")
            return 0

        return 1

    def download_install_phpmyadmin(self):
        try:
            os.chdir("/usr/local/lscp/cyberpanel/")
            count = 0

            while(1):
                command = 'wget https://'+preFlightsChecks.cyberPanelMirror+'/misc/phpMyAdmin-4.7.7-all-languages.zip'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to download PYPMYAdmin, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to download PYPMYAdmin, exiting installer! [download_install_phpmyadmin]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("PHPMYAdmin successfully downloaded!")
                    preFlightsChecks.stdOut("PHPMYAdmin successfully downloaded!")
                    break

            #####

            count = 0

            while(1):
                command = 'unzip phpMyAdmin-4.7.7-all-languages.zip'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    print("[" + time.strftime(
                        "%I-%M-%S-%a-%b-%Y") + "] " + "Unable to unzip PHPMYAdmin, trying again, try number: " + str(
                        count) + "\n")
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Unable to unzip PHPMYAdmin, exiting installer! [download_install_phpmyadmin]")
                        print("[" + time.strftime(
                            "%I-%M-%S-%a-%b-%Y") + "] " + "Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("PHPMYAdmin unzipped!")
                    print(
                        "[" + time.strftime("%I-%M-%S-%a-%b-%Y") + "] " + "PHPMYAdmin unzipped!")
                    break

            ###

            os.remove("phpMyAdmin-4.7.7-all-languages.zip")

            count = 0

            while(1):
                command = 'mv phpMyAdmin-4.7.7-all-languages phpmyadmin'

                cmd = shlex.split(command)

                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    print("[" + time.strftime(
                        "%I-%M-%S-%a-%b-%Y") + "] " + "Unable to install PHPMYAdmin, trying again, try number: " + str(
                        count) + "\n")
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Unable to install PHPMYAdmin, exiting installer! [download_install_phpmyadmin]")
                        print("[" + time.strftime(
                            "%I-%M-%S-%a-%b-%Y") + "] " + "Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("PHPMYAdmin Successfully installed!")
                    print(
                        "[" + time.strftime("%I-%M-%S-%a-%b-%Y") + "] " + "PHPMYAdmin Successfully installed!")
                    break

        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [download_install_phpmyadmin]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [download_install_phpmyadmin]")
            return 0

        return 1


    ###################################################### Email setup


    def install_postfix_davecot(self):
        try:

            count = 0

            while(1):
                command = 'yum -y --enablerepo=centosplus install postfix'

                cmd = shlex.split(command)

                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install Postfix, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install Postfix, you will not be able to send mails and rest should work fine! [install_postfix_davecot]")
                        break
                else:
                    logging.InstallLog.writeToFile("Postfix successfully installed!")
                    preFlightsChecks.stdOut("Postfix successfully installed!")
                    break

            count = 0

            while(1):

                command = 'yum -y install dovecot dovecot-mysql'

                cmd = shlex.split(command)

                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install Dovecot and Dovecot-MySQL, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install install Dovecot and Dovecot-MySQL, you will not be able to send mails and rest should work fine! [install_postfix_davecot]")
                        break
                else:
                    logging.InstallLog.writeToFile("Dovecot and Dovecot-MySQL successfully installed!")
                    preFlightsChecks.stdOut("Dovecot and Dovecot-MySQL successfully installed!")
                    break



        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_postfix_davecot]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_postfix_davecot]")
            return 0

        return 1


    def setup_email_Passwords(self,mysqlPassword):
        try:

           logging.InstallLog.writeToFile("Setting up authentication for Postfix and Dovecot...")

           os.chdir(self.cwd)

           mysql_virtual_domains = "email-configs/mysql-virtual_domains.cf"
           mysql_virtual_forwardings = "email-configs/mysql-virtual_forwardings.cf"
           mysql_virtual_mailboxes = "email-configs/mysql-virtual_mailboxes.cf"
           mysql_virtual_email2email = "email-configs/mysql-virtual_email2email.cf"
           davecotmysql = "email-configs/dovecot-sql.conf.ext"

           ### update password:

           data = open(davecotmysql, "r").readlines()

           writeDataToFile = open(davecotmysql, "w")

           dataWritten = "connect = host=127.0.0.1 dbname=cyberpanel user=cyberpanel password="+mysqlPassword+" port=3307\n"

           for items in data:
               if items.find("connect") > -1:
                   writeDataToFile.writelines(dataWritten)
               else:
                   writeDataToFile.writelines(items)

           writeDataToFile.close()

           ### update password:

           data = open(mysql_virtual_domains, "r").readlines()

           writeDataToFile = open(mysql_virtual_domains, "w")

           dataWritten = "password = " + mysqlPassword + "\n"

           for items in data:
               if items.find("password") > -1:
                   writeDataToFile.writelines(dataWritten)
               else:
                   writeDataToFile.writelines(items)

           writeDataToFile.close()

           ### update password:

           data = open(mysql_virtual_forwardings, "r").readlines()

           writeDataToFile = open(mysql_virtual_forwardings, "w")

           dataWritten = "password = " + mysqlPassword + "\n"

           for items in data:
               if items.find("password") > -1:
                   writeDataToFile.writelines(dataWritten)
               else:
                   writeDataToFile.writelines(items)

           writeDataToFile.close()

           ### update password:

           data = open(mysql_virtual_mailboxes, "r").readlines()

           writeDataToFile = open(mysql_virtual_mailboxes, "w")

           dataWritten = "password = " + mysqlPassword + "\n"

           for items in data:
               if items.find("password") > -1:
                   writeDataToFile.writelines(dataWritten)
               else:
                   writeDataToFile.writelines(items)

           writeDataToFile.close()

           ### update password:

           data = open(mysql_virtual_email2email, "r").readlines()

           writeDataToFile = open(mysql_virtual_email2email, "w")

           dataWritten = "password = " + mysqlPassword + "\n"

           for items in data:
               if items.find("password") > -1:
                   writeDataToFile.writelines(dataWritten)
               else:
                   writeDataToFile.writelines(items)

           writeDataToFile.close()

           logging.InstallLog.writeToFile("Authentication for Postfix and Dovecot set.")

        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setup_email_Passwords]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setup_email_Passwords]")
            return 0

        return 1


    def setup_postfix_davecot_config(self):
        try:
           logging.InstallLog.writeToFile("Configuring postfix and dovecot...")

           os.chdir(self.cwd)

           mysql_virtual_domains = "/etc/postfix/mysql-virtual_domains.cf"
           mysql_virtual_forwardings = "/etc/postfix/mysql-virtual_forwardings.cf"
           mysql_virtual_mailboxes = "/etc/postfix/mysql-virtual_mailboxes.cf"
           mysql_virtual_email2email = "/etc/postfix/mysql-virtual_email2email.cf"
           main = "/etc/postfix/main.cf"
           master = "/etc/postfix/master.cf"
           davecot = "/etc/dovecot/dovecot.conf"
           davecotmysql = "/etc/dovecot/dovecot-sql.conf.ext"



           if os.path.exists(mysql_virtual_domains):
               os.remove(mysql_virtual_domains)

           if os.path.exists(mysql_virtual_forwardings):
               os.remove(mysql_virtual_forwardings)

           if os.path.exists(mysql_virtual_mailboxes):
               os.remove(mysql_virtual_mailboxes)

           if os.path.exists(mysql_virtual_email2email):
               os.remove(mysql_virtual_email2email)

           if os.path.exists(main):
               os.remove(main)

           if os.path.exists(master):
               os.remove(master)

           if os.path.exists(davecot):
               os.remove(davecot)

           if os.path.exists(davecotmysql):
               os.remove(davecotmysql)



           ###############Getting SSL

           count = 0

           while(1):
               command = 'openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com" -keyout /etc/postfix/key.pem -out /etc/postfix/cert.pem'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to generate SSL for Postfix, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to generate SSL for Postfix, you will not be able to send emails and rest should work fine!! [setup_postfix_davecot_config]")
                       return
               else:
                   logging.InstallLog.writeToFile("SSL for Postfix generated!")
                   preFlightsChecks.stdOut("SSL for Postfix generated!")
                   break
           ##

           count = 0

           while(1):

               command = 'openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com" -keyout /etc/dovecot/key.pem -out /etc/dovecot/cert.pem'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to generate ssl for Dovecot, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to generate SSL for Dovecot, you will not be able to send emails and rest should work fine! [setup_postfix_davecot_config]")
                       return
               else:
                   logging.InstallLog.writeToFile("SSL generated for Dovecot!")
                   preFlightsChecks.stdOut("SSL generated for Dovecot!")
                   break



           ########### Copy config files

           shutil.copy("email-configs/mysql-virtual_domains.cf","/etc/postfix/mysql-virtual_domains.cf")
           shutil.copy("email-configs/mysql-virtual_forwardings.cf", "/etc/postfix/mysql-virtual_forwardings.cf")
           shutil.copy("email-configs/mysql-virtual_mailboxes.cf", "/etc/postfix/mysql-virtual_mailboxes.cf")
           shutil.copy("email-configs/mysql-virtual_email2email.cf", "/etc/postfix/mysql-virtual_email2email.cf")
           shutil.copy("email-configs/main.cf", main)
           shutil.copy("email-configs/master.cf",master)
           shutil.copy("email-configs/dovecot.conf",davecot)
           shutil.copy("email-configs/dovecot-sql.conf.ext",davecotmysql)


           ######################################## Permissions

           count = 0

           while(1):

               command = 'chmod o= /etc/postfix/mysql-virtual_domains.cf'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change permissions for mysql-virtual_domains.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable change permissions for mysql-virtual_domains.cf. [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Permissions changed for mysql-virtual_domains.cf!")
                   preFlightsChecks.stdOut("Permissions changed for mysql-virtual_domains.cf!")
                   break

           ##

           count = 0

           while(1):

               command = 'chmod o= /etc/postfix/mysql-virtual_forwardings.cf'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change permissions for mysql-virtual_forwardings.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change permissions for mysql-virtual_forwardings.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Permissions changed for mysql-virtual_forwardings.cf!")
                   preFlightsChecks.stdOut("Permissions changed for mysql-virtual_forwardings.cf!")
                   break


           ##

           count = 0

           while(1):

               command = 'chmod o= /etc/postfix/mysql-virtual_mailboxes.cf'
               cmd = shlex.split(command)
               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change permissions for mysql-virtual_mailboxes.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change permissions for mysql-virtual_mailboxes.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Permissions changed for mysql-virtual_mailboxes.cf!")
                   preFlightsChecks.stdOut("Permissions changed for mysql-virtual_mailboxes.cf!")
                   break

           ##

           count = 0

           while(1):

               command = 'chmod o= /etc/postfix/mysql-virtual_email2email.cf'
               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change permissions for mysql-virtual_email2email.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change permissions for mysql-virtual_email2email.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Permissions changed for mysql-virtual_email2email.cf!")
                   preFlightsChecks.stdOut("Permissions changed for mysql-virtual_email2email.cf!")
                   break

           ##

           count = 0

           while(1):

               command = 'chmod o= '+main
               cmd = shlex.split(command)
               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change permissions for /etc/postfix/main.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change permissions for /etc/postfix/main.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Permissions changed for /etc/postfix/main.cf!")
                   preFlightsChecks.stdOut("Permissions changed for /etc/postfix/main.cf!")
                   break

           ##

           count = 0

           while(1):

               command = 'chmod o= '+master

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change permissions for /etc/postfix/master.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change permissions for /etc/postfix/master.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Permissions changed for /etc/postfix/master.cf!")
                   preFlightsChecks.stdOut("Permissions changed for /etc/postfix/master.cf!")
                   break


           #######################################

           count = 0

           while(1):
               command = 'chgrp postfix /etc/postfix/mysql-virtual_domains.cf'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change group for mysql-virtual_domains.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change group for mysql-virtual_domains.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Group changed for mysql-virtual_domains.cf!")
                   preFlightsChecks.stdOut("Group changed for mysql-virtual_domains.cf!")
                   break

           ##

           count = 0

           while(1):
               command = 'chgrp postfix /etc/postfix/mysql-virtual_forwardings.cf'
               cmd = shlex.split(command)
               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change group for mysql-virtual_forwardings.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change group for mysql-virtual_forwardings.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Group changed for mysql-virtual_forwardings.cf!")
                   preFlightsChecks.stdOut("Group changed for mysql-virtual_forwardings.cf!")
                   break

           ##

           count = 0

           while(1):
               command = 'chgrp postfix /etc/postfix/mysql-virtual_mailboxes.cf'
               cmd = shlex.split(command)
               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change group for mysql-virtual_mailboxes.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change group for mysql-virtual_mailboxes.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Group changed for mysql-virtual_mailboxes.cf!")
                   preFlightsChecks.stdOut("Group changed for mysql-virtual_mailboxes.cf!")
                   break

           ##

           count = 0

           while(1):

               command = 'chgrp postfix /etc/postfix/mysql-virtual_email2email.cf'
               cmd = shlex.split(command)
               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change group for mysql-virtual_email2email.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change group for mysql-virtual_email2email.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Group changed for mysql-virtual_email2email.cf!")
                   preFlightsChecks.stdOut("Group changed for mysql-virtual_email2email.cf!")
                   break

           ##

           count = 0
           while(1):
               command = 'chgrp postfix '+main
               cmd = shlex.split(command)
               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change group for /etc/postfix/main.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change group for /etc/postfix/main.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Group changed for /etc/postfix/main.cf!")
                   preFlightsChecks.stdOut("Group changed for /etc/postfix/main.cf!")
                   break

           ##

           count = 0

           while(1):

               command = 'chgrp postfix ' + master

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change group for /etc/postfix/master.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change group for /etc/postfix/master.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Group changed for /etc/postfix/master.cf!")
                   preFlightsChecks.stdOut("Group changed for /etc/postfix/master.cf!")
                   break


           ######################################## users and groups

           count = 0

           while(1):

               command = 'groupadd -g 5000 vmail'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to add system group vmail, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to add system group vmail! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("System group vmail created successfully!")
                   preFlightsChecks.stdOut("System group vmail created successfully!")
                   break

           ##

           count = 0

           while(1):

               command = 'useradd -g vmail -u 5000 vmail -d /home/vmail -m'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to add system user vmail, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to add system user vmail! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("System user vmail created successfully!")
                   preFlightsChecks.stdOut("System user vmail created successfully!")
                   break


           ######################################## Further configurations

           #hostname = socket.gethostname()

           ################################### Restart postix

           count = 0

           while(1):

               if version >= 7:
                    command = "systemctl enable postfix.service"
               elif version >= 6:
                    command = "chkconfig --add postfix"

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Trying to add Postfix to system startup, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Failed to enable Postfix to run at system restart you can manually do this using systemctl enable postfix.service! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("postfix.service successfully enabled!")
                   preFlightsChecks.stdOut("postfix.service successfully enabled!")
                   break

            ##

           count = 0

           while(1):

               if version >= 7:
                    command = "systemctl start postfix.service"
               elif version >= 6:
                    command = "service postfix start"

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Trying to start Postfix, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to start Postfix, you can not send email until you manually start Postfix using systemctl start postfix.service! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("postfix.service started successfully!")
                   preFlightsChecks.stdOut("postfix.service started successfully!")
                   break

           ######################################## Permissions

           count = 0

           while(1):

               command = 'chgrp dovecot /etc/dovecot/dovecot-sql.conf.ext'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change group for /etc/dovecot/dovecot-sql.conf.ext, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change group for /etc/dovecot/dovecot-sql.conf.ext! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Group changed for /etc/dovecot/dovecot-sql.conf.ext!")
                   preFlightsChecks.stdOut("Group changed for /etc/dovecot/dovecot-sql.conf.ext!")
                   break
           ##


           count = 0

           while(1):

               command = 'chmod o= /etc/dovecot/dovecot-sql.conf.ext'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change permissions for /etc/dovecot/dovecot-sql.conf.ext, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change permissions for /etc/dovecot/dovecot-sql.conf.ext! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Permissions changed for /etc/dovecot/dovecot-sql.conf.ext!")
                   preFlightsChecks.stdOut("Permissions changed for /etc/dovecot/dovecot-sql.conf.ext!")
                   break

           ################################### Restart davecot

           count = 0


           while(1):

               if version >= 7:
                    command = "systemctl enable dovecot.service"
               elif version >= 6:
                    command = "chkconfig --add dovecot"
               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to enable dovecot.service, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to enable dovecot.service! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("dovecot.service successfully enabled!")
                   preFlightsChecks.stdOut("dovecot.service successfully enabled!")
                   break


           ##


           count = 0


           while(1):
               if version >= 7:
                    command = "systemctl start dovecot.service"
               elif version >= 6:
                    command = "service dovecot start"
               cmd = shlex.split(command)
               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to start dovecot.service, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to start dovecot.service! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("dovecot.service successfully started!")
                   preFlightsChecks.stdOut("dovecot.service successfully started!")
                   break

           ##

           count = 0

           while(1):

               command = 'systemctl restart  postfix.service'

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to restart postfix.service, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to restart postfix.service! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("dovecot.service successfully restarted!")
                   preFlightsChecks.stdOut("postfix.service successfully restarted!")
                   break


           ## chaging permissions for main.cf

           count = 0

           while(1):

               command = "chmod 755 "+main

               cmd = shlex.split(command)

               res = subprocess.call(cmd)

               if res == 1:
                   count = count + 1
                   preFlightsChecks.stdOut("Unable to change permissions for /etc/postfix/main.cf, trying again, try number: " + str(count))
                   if count == 3:
                       logging.InstallLog.writeToFile("Unable to change permissions for /etc/postfix/main.cf! [setup_postfix_davecot_config]")
                       break
               else:
                   logging.InstallLog.writeToFile("Permissions changed for /etc/postfix/main.cf!")
                   preFlightsChecks.stdOut("Permissions changed for /etc/postfix/main.cf!")
                   break

           logging.InstallLog.writeToFile("Postfix and Dovecot configured")

        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setup_postfix_davecot_config]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setup_postfix_davecot_config]")
            return 0

        return 1


    def downoad_and_install_raindloop(self):
        try:
            ###########
            count = 0

            while(1):
                command = 'chown -R nobody:nobody /usr/local/lscp/cyberpanel/'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to change owner for /usr/local/lscp/cyberpanel/, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Failed to change owner for /usr/local/lscp/cyberpanel/, but installer can continue! [downoad_and_install_raindloop]")
                        break
                else:
                    logging.InstallLog.writeToFile("Owner changed for /usr/local/lscp/cyberpanel/!")
                    preFlightsChecks.stdOut("Owner changed for /usr/local/lscp/cyberpanel/!")
                    break
            #######


            os.chdir("/usr/local/lscp/cyberpanel")

            count = 1

            while(1):
                command = 'wget https://'+preFlightsChecks.cyberPanelMirror+'/misc/rainloop-community-latest.zip'

                cmd = shlex.split(command)

                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to download Rainloop, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to download Rainloop, installation can continue but you will not be able to send emails! [downoad_and_install_raindloop]")
                        return
                else:
                    logging.InstallLog.writeToFile("Rainloop Downloaded!")
                    preFlightsChecks.stdOut("Rainloop Downloaded!")
                    break

            #############

            count = 0

            while(1):
                command = 'unzip rainloop-community-latest.zip -d /usr/local/lscp/cyberpanel/rainloop'

                cmd = shlex.split(command)

                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to unzip rainloop, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("We could not unzip Rainloop, so you will not be able to send emails! [downoad_and_install_raindloop]")
                        return
                else:
                    logging.InstallLog.writeToFile("Rainloop successfully unzipped!")
                    preFlightsChecks.stdOut("Rainloop successfully unzipped!")
                    break

            os.remove("rainloop-community-latest.zip")

            #######

            os.chdir("/usr/local/lscp/cyberpanel/rainloop")

            count = 0

            while(1):
                command = 'find . -type d -exec chmod 755 {} \;'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to change permissions for Rainloop, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Failed to change permissions for Rainloop, so you will not be able to send emails!! [downoad_and_install_raindloop]")
                        break
                else:
                    logging.InstallLog.writeToFile("Rainloop permissions changed!")
                    print(
                        "[" + time.strftime("%I-%M-%S-%a-%b-%Y") + "] " + "Rainloop permissions changed!")
                    break

            #############

            count = 0

            while(1):

                command = 'find . -type f -exec chmod 644 {} \;'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to change permissions for Rainloop, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Failed to change permissions for Rainloop, so you will not be able to send emails!! [downoad_and_install_raindloop]")
                        break
                else:
                    logging.InstallLog.writeToFile("Rainloop permissions changed!")
                    preFlightsChecks.stdOut("Rainloop permissions changed!")
                    break
            ######

            count = 0

            while(1):

                command = 'chown -R nobody:nobody .'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to change owner for Rainloop, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Failed to change owner for Rainloop, so you will not be able to send emails!! [downoad_and_install_raindloop]")
                        break
                else:
                    logging.InstallLog.writeToFile("Rainloop owner changed!")
                    preFlightsChecks.stdOut("Rainloop owner changed!")
                    break




        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [downoad_and_install_rainloop]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [downoad_and_install_rainloop]")
            return 0

        return 1

    ###################################################### Email setup ends!


    def reStartLiteSpeed(self):
        try:
            count = 0
            while(1):
                cmd = []

                cmd.append(self.server_root_path+"bin/lswsctrl")
                cmd.append("restart")

                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to restart OpenLiteSpeed, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to restart OpenLiteSpeed! [reStartLiteSpeed]")
                        break
                else:
                    logging.InstallLog.writeToFile("OpenLiteSpeed restarted Successfully!")
                    preFlightsChecks.stdOut("OpenLiteSpeed restarted Successfully!")
                    break

        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [reStartLiteSpeed]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [reStartLiteSpeed]")
            return 0
        return 1


    def installFirewalld(self):
        try:

            preFlightsChecks.stdOut("Enabling Firewall!")

            count = 0

            while(1):
                if version >= 7:
                    command = "yum -y install firewalld"
                elif version >= 6:
                    command = "yum -y install iptables"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to install FirewallD, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install FirewallD, funtions related to Firewall will not work! [installFirewalld]")
                        break
                else:
                    logging.InstallLog.writeToFile("FirewallD successfully installed!")
                    preFlightsChecks.stdOut("FirewallD successfully installed!")
                    break

            ######

            count = 0

            while(1):
                if version >= 7:
                    command = "systemctl start firewalld"
                elif version >= 6:
                    command = "service iptables start"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to start Firewall, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to start Firewall, you can manually start it later using systemctl start firewalld! [installFirewalld]")
                        break
                else:
                    logging.InstallLog.writeToFile("FirewallD successfully started!")
                    preFlightsChecks.stdOut("FirewallD successfully started!")
                    break


            ##########

            count = 0

            while(1):

                if version >= 7:
                    command = "systemctl enable firewalld"
                elif version >= 6:
                    command = "chkconfig --add iptables"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to enable FirewallD at system startup, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("FirewallD may not start after restart, you need to manually run systemctl enable firewalld ! [installFirewalld]")
                        break
                else:
                    logging.InstallLog.writeToFile("FirewallD successfully enabled on system startup!")
                    preFlightsChecks.stdOut("FirewallD successfully enabled on system startup!")
                    break


            if version >= 7:
                FirewallUtilities.addRule("tcp","8090")
                FirewallUtilities.addRule("tcp", "80")
                FirewallUtilities.addRule("tcp", "443")
                FirewallUtilities.addRule("tcp", "21")
                FirewallUtilities.addRule("tcp", "25")
                FirewallUtilities.addRule("tcp", "587")
                FirewallUtilities.addRule("tcp", "465")
                FirewallUtilities.addRule("tcp", "110")
                FirewallUtilities.addRule("tcp", "143")
                FirewallUtilities.addRule("tcp", "993")
                FirewallUtilities.addRule("udp", "53")
                FirewallUtilities.addRule("tcp", "53")
                FirewallUtilities.addRule("tcp", "40110-40210")
            elif version >= 6:
                command = "iptables -I INPUT -p tcp --dport 8090,80,443,21,25,587,465,110,143,993,53 -j ACCEPT"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)
                command = "iptables -I INPUT -p udp --dport 53 -j ACCEPT"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)
                command = "iptables -I INPUT -p udp --dport 40110:40210 -j ACCEPT"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)


            logging.InstallLog.writeToFile("FirewallD installed and configured!")
            preFlightsChecks.stdOut("FirewallD installed and configured!")


        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [installFirewalld]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [installFirewalld]")
            return 0

        return 1

    ## from here

    def setupLSCPDDaemon(self):
        try:

            preFlightsChecks.stdOut("Trying to setup LSCPD Daemon!")
            logging.InstallLog.writeToFile("Trying to setup LSCPD Daemon!")

            os.chdir(self.cwd)

            if version >= 7:
                shutil.copy("lscpd/lscpd.service","/etc/systemd/system/lscpd.service")
            elif version >= 6:
                shutil.copy("lscpd/lscpd6.service","/etc/init.d/lscpd")
                command = "chmod +x /etc/init.d/lscpd"
                res = subprocess.call(shlex.split(command))
            shutil.copy("lscpd/lscpdctrl","/usr/local/lscp/bin/lscpdctrl")

            ##

            count = 0

            while(1):

                command = 'chmod +x /usr/local/lscp/bin/lscpdctrl'

                cmd = shlex.split(command)

                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to change permissions for /usr/local/lscp/bin/lscpdctrl, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to change permissions for /usr/local/lscp/bin/lscpdctrl [setupLSCPDDaemon]")
                        break
                else:
                    logging.InstallLog.writeToFile("Successfully changed permissions for /usr/local/lscp/bin/lscpdctrl!")
                    preFlightsChecks.stdOut("Successfully changed permissions for /usr/local/lscp/bin/lscpdctrl!")
                    break

            ##

            count = 1

            while(1):

                if version >= 7:
                    command = 'systemctl enable lscpd.service'
                elif version >= 6:
                    command = 'chkconfig --add lscpd && chmod +x /etc/init.d/lscpd'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to enable LSCPD on system startup, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to change permissions for /usr/local/lscp/bin/lscpdctrl, you can do it manually using  systemctl enable lscpd.service [setupLSCPDDaemon]")
                        break
                else:
                    logging.InstallLog.writeToFile("LSCPD Successfully enabled at system startup!")
                    preFlightsChecks.stdOut("LSCPD Successfully enabled at system startup!")
                    break

            ##

            count = 0

            while(1):

                if version >= 7:
                    command = 'systemctl start lscpd'
                elif version >= 6:
                    command = 'service lscpd start'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Unable to start LSCPD, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to start LSCPD! [setupLSCPDDaemon]")
                        break
                else:
                    logging.InstallLog.writeToFile("LSCPD successfully started!")
                    preFlightsChecks.stdOut("LSCPD successfully started!")
                    break

            preFlightsChecks.stdOut("LSCPD Daemon Set!")

            logging.InstallLog.writeToFile("LSCPD Daemon Set!")


        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setupLSCPDDaemon]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setupLSCPDDaemon]")
            return 0

        return 1

    def setup_cron(self):

        try:
            ## first install crontab

            file = open("installLogs.txt", 'a')

            count = 0

            while(1):

                command = 'yum install cronie -y'

                cmd = shlex.split(command)

                res = subprocess.call(cmd, stdout=file)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to install cronie, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install cronie, cron jobs will not work. [setup_cron]")
                        break
                else:
                    logging.InstallLog.writeToFile("Cronie successfully installed!")
                    preFlightsChecks.stdOut("Cronie successfully installed!")
                    break


            count = 0

            while(1):

                if version >= 7:
                    command = 'systemctl enable crond'
                elif version >= 6:
                    command = 'chkconfig --add crond'

                cmd = shlex.split(command)

                res = subprocess.call(cmd, stdout=file)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to enable cronie on system startup, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("We are not able to enable cron jobs at system startup, you can manually run systemctl enable crond. [setup_cron]")
                        break
                else:
                    logging.InstallLog.writeToFile("Cronie successfully enabled at system startup!")
                    preFlightsChecks.stdOut("Cronie successfully enabled at system startup!")
                    break

            count = 0

            while(1):

                if version >= 7:
                    command = 'systemctl start crond'
                elif version >= 6:
                    command = 'service crond start'

                cmd = shlex.split(command)

                res = subprocess.call(cmd, stdout=file)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to start crond, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("We are not able to start crond, you can manually run systemctl start crond. [setup_cron]")
                        break
                else:
                    logging.InstallLog.writeToFile("Crond successfully started!")
                    preFlightsChecks.stdOut("Crond successfully started!")
                    break

            ##

            cronFile = open("/etc/crontab", "a")
            cronFile.writelines("0 * * * * root python /usr/local/CyberCP/plogical/findBWUsage.py" + "\n")
            cronFile.close()

            command = 'chmod +x /usr/local/CyberCP/plogical/findBWUsage.py'

            cmd = shlex.split(command)

            res = subprocess.call(cmd, stdout=file)

            if res == 1:
                logging.InstallLog.writeToFile("1428 [setup_cron]")
            else:
                pass

            count = 0

            while(1):

                if version >= 7:
                    command = 'systemctl restart crond'
                elif version >= 6:
                    command = 'service crond restart'

                cmd = shlex.split(command)

                res = subprocess.call(cmd, stdout=file)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to restart crond, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("We are not able to restart crond, you can manually run systemctl restart crond. [setup_cron]")
                        break
                else:
                    logging.InstallLog.writeToFile("Crond successfully restarted!")
                    preFlightsChecks.stdOut("Crond successfully restarted!")
                    break

            file.close()


        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setup_cron]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [setup_cron]")
            return 0

        return 1

    def install_default_keys(self):
        try:
            count = 0

            path = "/root/.ssh"

            if not os.path.exists(path):
                os.mkdir(path)

            while (1):

                command = "ssh-keygen -f /root/.ssh/cyberpanel -t rsa -N ''"
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to setup default SSH keys, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to setup default SSH keys. [install_default_keys]")
                        break
                else:
                    logging.InstallLog.writeToFile("Succcessfully created default SSH keys!")
                    preFlightsChecks.stdOut("Succcessfully created default SSH keys!")
                    break

        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_default_keys]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_default_keys]")
            return 0

        return 1

    def install_rsync(self):
        try:
            count = 0
            while (1):

                command = 'yum -y install rsync'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut("Trying to install rsync, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile("Unable to install rsync, some of backup functions will not work. [install_rsync]")
                        break
                else:
                    logging.InstallLog.writeToFile("Succcessfully installed rsync!")
                    preFlightsChecks.stdOut("Succcessfully installed rsync!")
                    break


        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_rsync]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [install_rsync]")
            return 0

        return 1

    def test_Requests(self):
        try:
            import requests
            getVersion = requests.get('https://cyberpanel.net/version.txt')
            latest = getVersion.json()
        except BaseException,msg:

            command = "pip uninstall --yes urllib3"
            subprocess.call(shlex.split(command))

            command = "pip uninstall --yes requests"
            subprocess.call(shlex.split(command))

            count = 0
            while (1):

                command = "pip install http://"+preFlightsChecks.cyberPanelMirror+"/pip/urllib3-1.22.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut(
                        "Unable to install urllib3 module, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Unable to install urllib3 module, exiting installer! [install_python_requests]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("urllib3 module Successfully installed!")
                    preFlightsChecks.stdOut("urllib3 module Successfully installed!")
                    break

            count = 0
            while (1):

                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/requests-2.18.4.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut(
                        "Unable to install requests module, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Unable to install requests module, exiting installer! [install_python_requests]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("Requests module Successfully installed!")
                    preFlightsChecks.stdOut("Requests module Successfully installed!")
                    break

    def installation_successfull(self):
        print("###################################################################")
        print("                CyberPanel Successfully Installed                  ")
        print("                                                                   ")

        print("                                                                   ")
        print("                                                                   ")

        print("                Visit: https://" + self.ipAddr + ":8090                ")
        print("                Username: admin                                    ")
        print("                Password: 1234567                                  ")

        print("###################################################################")

    def installCertBot(self):
        try:

            command = "pip uninstall --yes pyOpenSSL"
            res = subprocess.call(shlex.split(command))

            command = "pip uninstall --yes certbot"
            res = subprocess.call(shlex.split(command))

            count = 0
            while (1):
                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/pyOpenSSL-17.5.0.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut(
                        "Trying to install pyOpenSSL, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Failed to install pyOpenSSL, exiting installer! [installCertBot]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("pyOpenSSL successfully installed!  [pip]")
                    preFlightsChecks.stdOut("pyOpenSSL successfully installed!  [pip]")
                    break

            count = 0
            while (1):
                command = "pip install https://"+preFlightsChecks.cyberPanelMirror+"/pip/certbot-0.21.1.tar.gz"

                res = subprocess.call(shlex.split(command))

                if res == 1:
                    count = count + 1
                    preFlightsChecks.stdOut(
                        "Trying to install CertBot, trying again, try number: " + str(count))
                    if count == 3:
                        logging.InstallLog.writeToFile(
                            "Failed to install CertBot, exiting installer! [installCertBot]")
                        preFlightsChecks.stdOut("Installation failed, consult: /var/log/installLogs.txt")
                        sys.exit()
                else:
                    logging.InstallLog.writeToFile("CertBot successfully installed!  [pip]")
                    preFlightsChecks.stdOut("CertBot successfully installed!  [pip]")
                    break

        except OSError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [installCertBot]")
            return 0
        except ValueError, msg:
            logging.InstallLog.writeToFile(str(msg) + " [installCertBot]")
            return 0

        return 1


def main():

    parser = argparse.ArgumentParser(description='CyberPanel Installer')
    parser.add_argument('publicip', help='Please enter public IP for your VPS or dedicated server.')
    args = parser.parse_args()

    logging.InstallLog.writeToFile("Starting CyberPanel installation..")
    preFlightsChecks.stdOut("Starting CyberPanel installation..")

    ## Writing public IP

    pathCyberPanel = "/etc/cyberpanel"
    if os.path.exists(pathCyberPanel):
        os.remove(pathCyberPanel)
    os.mkdir("/etc/cyberpanel")

    machineIP = open("/etc/cyberpanel/machineIP", "w")
    machineIP.writelines(args.publicip)
    machineIP.close()

    cwd = os.getcwd()

    checks = preFlightsChecks("/usr/local/lsws/",args.publicip,"/usr/local",cwd,"/usr/local/CyberCP")

    if checks.checkIfSeLinuxDisabled() == 1:
        pass
    else:
        return

    checks.checkPythonVersion()
    checks.setup_account_cyberpanel()
    checks.yum_update()
    checks.enableEPELRepo()
    checks.installCyberPanelRepo()
    checks.install_pip()
    checks.install_python_dev()
    checks.install_gcc()
    checks.install_python_setup_tools()
    checks.install_django()
    checks.install_pexpect()
    checks.install_python_mysql_library()
    checks.install_gunicorn()
    checks.install_psutil()
    checks.setup_gunicorn()

    import installCyberPanel

    installCyberPanel.Main(cwd)
    checks.fix_selinux_issue()
    checks.install_psmisc()
    checks.install_postfix_davecot()
    checks.setup_email_Passwords(installCyberPanel.InstallCyberPanel.mysqlPassword)
    checks.setup_postfix_davecot_config()


    checks.install_unzip()
    checks.install_zip()
    checks.install_rsync()

    checks.downoad_and_install_raindloop()


    checks.download_install_phpmyadmin()

    checks.installFirewalld()

    checks.setupLSCPDDaemon()
    checks.install_python_requests()
    checks.install_default_keys()

    checks.installCertBot()
    checks.test_Requests()
    checks.download_install_CyberPanel(installCyberPanel.InstallCyberPanel.mysqlPassword)
    checks.setup_cron()
    checks.installation_successfull()

    logging.InstallLog.writeToFile("CyberPanel installation successfully completed!")


if __name__ == "__main__":
    system=platform.dist()[0]
    version=float(platform.dist()[1])
    main()
