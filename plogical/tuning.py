import CyberCPLogFileWriter as logging
from installUtilities import installUtilities
import argparse
import subprocess
import shlex

class tuning:


    @staticmethod
    def fetchTuningDetails():

        try:
            dataToReturn = {}

            command = "sudo cat /usr/local/lsws/conf/httpd_config.conf"
            datas = subprocess.check_output(shlex.split(command)).split("\n")

            for items in datas:
                if items.find("maxConnections")>-1:
                    data = items.split()
                    dataToReturn['maxConnections'] = data[1]

                if items.find("maxSSLConnections") > -1:
                    data = items.split()
                    dataToReturn['maxSSLConnections'] = data[1]

                if items.find("connTimeout") > -1:
                    data = items.split()
                    dataToReturn['connTimeout'] = data[1]


                if items.find("maxConnections")>-1:
                    data = items.split()
                    dataToReturn['maxConnections'] = data[1]

                if items.find("keepAliveTimeout") > -1:
                    data = items.split()
                    dataToReturn['keepAliveTimeout'] = data[1]


                if items.find("totalInMemCacheSize") > -1:
                    data = items.split()
                    dataToReturn['totalInMemCacheSize'] = data[1]

                if items.find("enableGzipCompress") > -1:
                    data = items.split()
                    dataToReturn['enableGzipCompress'] = data[1]

            return dataToReturn

        except BaseException, msg:
            logging.CyberCPLogFileWriter.writeToFile(
                str(msg) + " [fetchTuningDetails]")
            return 0


    @staticmethod
    def saveTuningDetails(maxConnections,maxSSLConnections,connectionTimeOut,keepAliveTimeOut,cacheSizeInMemory,gzipCompression):

        try:
            datas = open("/usr/local/lsws/conf/httpd_config.conf").readlines()
            writeDataToFile = open("/usr/local/lsws/conf/httpd_config.conf","w")

            if gzipCompression == "Enable":
                gzip = 1
            else:
                gzip = 0


            for items in datas:
                if items.find("maxConnections") > -1:
                    data = "  maxConnections          "+str(maxConnections)+"\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("maxSSLConnections") > -1:
                    data = "  maxSSLConnections       "+str(maxSSLConnections) + "\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("connTimeout") > -1:
                    data ="  connTimeout             "+str(connectionTimeOut)+"\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("keepAliveTimeout") > -1:
                    data = "  keepAliveTimeout        " + str(keepAliveTimeOut) + "\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("totalInMemCacheSize") > -1:
                    data = "  totalInMemCacheSize     " + str(cacheSizeInMemory) + "\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("enableGzipCompress") > -1:
                    data = "  enableGzipCompress      " + str(gzip) + "\n"
                    writeDataToFile.writelines(data)
                    continue
                else:
                    writeDataToFile.writelines(items)

            writeDataToFile.close()

            print "1,None"

        except BaseException, msg:
            logging.CyberCPLogFileWriter.writeToFile(
                str(msg) + " [saveTuningDetails]")
            print "0," + str(msg)


    @staticmethod
    def fetchPHPDetails(virtualHost):
        try:
            path = installUtilities.Server_root_path + "/conf/vhosts/"+virtualHost+"/vhost.conf"

            command = "sudo cat "+path
            datas = subprocess.check_output(shlex.split(command)).split("\n")

            dataToReturn = {}

            for items in datas:
                if items.find("maxConns")>-1:
                    data = items.split()
                    dataToReturn['maxConns'] = data[1]

                if items.find("initTimeout") > -1:
                    data = items.split()
                    dataToReturn['initTimeout'] = data[1]

                if items.find("persistConn") > -1:
                    data = items.split()
                    dataToReturn['persistConn'] = data[1]


                if items.find("memSoftLimit")>-1:
                    data = items.split()
                    dataToReturn['memSoftLimit'] = data[1]

                if items.find("memHardLimit") > -1:
                    data = items.split()
                    dataToReturn['memHardLimit'] = data[1]


                if items.find("procSoftLimit") > -1:
                    data = items.split()
                    dataToReturn['procSoftLimit'] = data[1]

                if items.find("procHardLimit") > -1:
                    data = items.split()
                    dataToReturn['procHardLimit'] = data[1]

            return dataToReturn

        except BaseException, msg:
            logging.CyberCPLogFileWriter.writeToFile(
                str(msg) + " [fetchPHPDetails]")
            return 0

    @staticmethod
    def tunePHP(virtualHost,maxConns,initTimeout,persistConn,memSoftLimit,memHardLimit,procSoftLimit,procHardLimit):


        try:
            path = installUtilities.Server_root_path + "/conf/vhosts/" + virtualHost + "/vhost.conf"
            datas = open(path).readlines()

            writeDataToFile = open(path,"w")


            for items in datas:
                if items.find("maxConns") > -1:
                    data = "  maxConns                "+str(maxConns)+"\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("initTimeout") > -1:
                    data = "  initTimeout             "+str(initTimeout) + "\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("memSoftLimit") > -1:
                    data ="  memSoftLimit            "+str(memSoftLimit)+"\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("memHardLimit") > -1:
                    data = "  memHardLimit            " + str(memHardLimit) + "\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("procSoftLimit") > -1:
                    data = "  procSoftLimit           " + str(procSoftLimit) + "\n"
                    writeDataToFile.writelines(data)
                    continue

                elif items.find("procHardLimit") > -1:
                    data = "  procHardLimit           " + str(procHardLimit) + "\n"
                    writeDataToFile.writelines(data)
                    continue
                elif items.find("persistConn") > -1:
                    if persistConn == "Enable":
                        persist = 1
                    else:
                        persist = 0


                    data = "  persistConn             " + str(persist) + "\n"
                    writeDataToFile.writelines(data)
                    continue
                else:
                    writeDataToFile.writelines(items)

            writeDataToFile.close()

            print "1,None"

        except BaseException, msg:
            logging.CyberCPLogFileWriter.writeToFile(
                str(msg) + " [saveTuningDetails]")
            print "0,"+str(msg)

def main():

    parser = argparse.ArgumentParser(description='CyberPanel Installer')
    parser.add_argument('function', help='Specific a function to call!')
    parser.add_argument('--virtualHost', help='Domain name!')
    parser.add_argument('--maxConns', help='Max Connections for PHP!')
    parser.add_argument('--initTimeout', help='Initial Request Timeout (secs) for PHP!')
    parser.add_argument("--persistConn", help="Persistent Connection for PHP!")
    parser.add_argument("--memSoftLimit", help="Memory Soft Limit (bytes) for PHP!")
    parser.add_argument("--memHardLimit", help="Memory Hard Limit (bytes) for PHP!")
    parser.add_argument("--procSoftLimit", help="Process Soft Limit for PHP!")
    parser.add_argument("--procHardLimit", help="Process Hard Limit for PHP!")

    ## Litespeed Tuning Arguments

    parser.add_argument("--maxConn", help="Max Connections for LiteSpeed!")
    parser.add_argument("--maxSSLConn", help="Max SSL Connections for LiteSpeed!")
    parser.add_argument("--connTime", help="Connection Timeout (secs) for LiteSpeed!")
    parser.add_argument("--keepAlive", help="Keep-Alive Timeout (secs) for LiteSpeed!")
    parser.add_argument("--inMemCache", help="Total Small File Cache Size (bytes) for LiteSpeed!")
    parser.add_argument("--gzipCompression", help="Enable disable GZIP Compression for LiteSpeed!")


    args = parser.parse_args()

    if args.function == "tunePHP":
        tuning.tunePHP(args.virtualHost, args.maxConns, args.initTimeout, args.persistConn, args.memSoftLimit, args.memHardLimit, args.procSoftLimit,
                       args.procHardLimit)
    elif args.function == "saveTuningDetails":
        tuning.saveTuningDetails(args.maxConn, args.maxSSLConn, args.connTime, args.keepAlive, args.inMemCache, args.gzipCompression)




if __name__ == "__main__":
    main()

