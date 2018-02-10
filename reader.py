from __future__ import print_function
import yaml
import random
import os
import fileinput
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import platform

ips = []
global jmeterPath
chrome_script_path = '/Scripts/Chrome'
chrome_fullpath = os.path.dirname(os.path.realpath(__file__))+chrome_script_path
firefox_script_path = '/Scripts/Firefox'
firefox_fullpath = os.path.dirname(os.path.realpath(__file__))+firefox_script_path
global reportPath

def replaceAll(file_path, pattern, subst):
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    remove(file_path)
    move(abs_path, file_path)




with open("Input/config.yaml", 'r') as stream:
    try:

        content = yaml.load(stream)
        print(content)
        urlList = content['gitUrl']
        url = urlList[0]
        print(url)
        osname = platform.system()
        print(osname)
        if osname == "Windows":
            jmeterVar = content['windows-jmeterPath']
            print(jmeterVar)

        else:
            jmeterVar = content['ubuntu-jmeterPath']
            print(jmeterVar)
        jmeterPath = jmeterVar[0]
        print(jmeterPath)




    except yaml.YAMLError as exc:
        print(exc)


def jmeter_exection(iteration, rampup, concurrency, filepath):
    os.chdir(jmeterPath)
    os.system("./jmeter.sh -n -t"+ filepath+" -r -Gusers="+str(concurrency)+" -GrampUp="+str(rampup)+" -Gcount="+str(iteration)+" -Gduration="+str(timeout)+" -Gurl="+str(url))
    print("executed")




def read_n_write_ip():
    with open(jmeterPath+"/ipconfig.txt", 'r') as stream:
        try:
            content = yaml.load(stream)
            print(content)

        except yaml.YAMLError as exc:
            print(exc)

    text = "remote_hosts="
    x = fileinput.input(files=jmeterPath+"/jmeter.properties",inplace=1)
    for line in x:
        if text in line:
            line = "remote_hosts="+content+"\n"
        print (line)
    x.close()



with open("Input/Input.yaml", 'r') as stream:
    global concurrency
    concurrency = 1
    iteration = 1
    rampup = 0
    try:
        content = yaml.load(stream)
        #print(content)

        if 'instance' in content:
            instancevar = content['instance']
            instanceNo = instancevar[0]
            read_n_write_ip()


        if 'execution' in content:
            exection = content['execution']
            for var in exection:
                if "iteration" in var:
                    iteration = var['iteration']
                elif  "concurrency" in var:
                    concurrency = var["concurrency"]
                elif "ramp-up" in var:
                    rampup = var['ramp-up']

                    if(isinstance(rampup,int)):
                        rampup =int(rampup)*60

                    elif "m" in rampup:
                        rampup = rampup.replace("m","")
                        rampup=int(rampup)*60

                    elif "s" in rampup:
                        rampup = rampup.replace("s","")
                        rampup = int(rampup)

            print(concurrency,iteration,rampup)


        if "time-out" in content:
            timeout = content['time-out'][0]

            if (isinstance(timeout, int)):
                timeout = int(timeout)* 60

            elif "m" in timeout:
                timeout = timeout.replace("m", "")
                timeout = int(timeout) * 60

            elif "s" in rampup:
                timeout = timeout.replace("s", "")
                timeout = int(timeout)

        if "random" in content:
            path = content['random'][0]
            lst = os.listdir(path)
            randomArray = random.sample(range(0, len(lst) - 1), len(lst) - 1)
            for no in randomArray:
                filepath = path + "/" + lst[no]
                print(filepath,iteration,rampup,concurrency,iteration,rampup,concurrency)
                jmeter_exection(iteration,rampup,concurrency,filepath)

        else:
            browsers = content['browsers']
            for browser in browsers:
                if "chrome" in browser:
                    path = chrome_fullpath

                elif "firefox" in browser:
                    path = ''
                    path = firefox_fullpath

                scripts = content['scripts']
                for script in scripts:
                    filedir = path
                    print(filedir)
                    lst = os.listdir(filedir)
                    if script in lst:
                        filepath = filedir+"/"+script
                        print(filepath)
                        cache=content['cache'][0]
                        if not cache:
                            print(cache)
                            replaceAll(filepath, '<boolProp name="WebDriverConfig.reset_per_iteration">false</boolProp>', '<boolProp name="WebDriverConfig.reset_per_iteration">true</boolProp>')

                        else:
                            print(cache)
                            replaceAll(filepath,'<boolProp name="WebDriverConfig.reset_per_iteration">true</boolProp>', '<boolProp name="WebDriverConfig.reset_per_iteration">false</boolProp>')

                        print(script,browser,iteration,rampup,concurrency,iteration,rampup,concurrency)
                        jmeter_exection(iteration, rampup, concurrency, filepath)

                    elif os.path.isfile(script):
                        filepath = script
                        jmeter_exection(iteration, rampup, concurrency, filepath)

                    else:
                        print(script+" script is not present for "+browser)


    except yaml.YAMLError as exc:
        print(exc)
