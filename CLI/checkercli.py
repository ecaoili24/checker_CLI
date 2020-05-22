#!/usr/bin/python3
import sys
import os
import requests
import time

def getToken(refresh=False):
    tfile = os.path.expanduser("~/.ccli/token")
    tok = ""
    try:
        f = open(tfile, "r")
        tok = f.read()
        if tok == "" or refresh:
            raise FileNotFoundError
        return (tok)
    except FileNotFoundError:
        if not os.path.exists(os.path.expanduser("~/.ccli/")):
            os.mkdir(os.path.expanduser("~/.ccli/"))
        api_key = input("Please enter API key: ")
        email = input("Please enter your Email: ")
        password = input("Please enter your password: ")
        res = requests.post("https://intranet.hbtn.io/users/auth_token.json",
                              json={
                                "api_key": api_key,
                                "email": email,
                                "password": password,
                                "scope": "checker"
                              });
        if not res or res.status_code != 200:
            print("Error authenticating. Please make sure your information is correct.")
            sys.exit(1)
        f = open(tfile, "w")
        tok = res.json()["auth_token"]
        f.write(tok)
        f.close()
        print (tok)
        return tok

def help():
    print("Help for Checker CLI:")
    print("")
    print("\033[1mCommands:\033[0m")
    print("\tstatus <project_id> [task_num]\t: Gets the status of a "+
          "certain project or task")
    print("\t\tproject_id\t: The ID of the project to get the " +
          "status of, or contains the task to get the status of")
    print("\t\ttask_num\t: (Optional) The number of the task to " +
          "get the status of")
    print("")
    print("\tcheck <project_id> <task_num>\t: Checks a certain task")
    print("\t\tproject_id\t: The ID of the project that has the task to check")
    print("\t\ttask_num\t: The number of the task to check")
    print("")
    print("\trefresh\t: Prompts credential refresh")
    print("")
    print("\trun\t: Pushes code and runs checker")
    print("\t\t-d{n}\t: Dry mode. Runs checker for task `n` without " +
          "pushing new code. Note: `n` should be the number next " +
          "to the task, not the file prefix.")
    print("")

if __name__ == "__main__":
    token = getToken()
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if (command in set(["-h", "--help"])):
            help()
        elif (command == "run"):
            dry = -1
            if len(sys.argv) > 2:
                flag = sys.argv[2]
                if len(flag) > 2 and flag[:2] == "-d":
                    try:
                        dry = int(flag[2:])
                    except:
                        print("Not a valid value for `n`!")

            if dry == -1:
                os.system("echo 'Replace this with git push code'")
            os.system("echo 'Replace this with checker API code'")
        elif (command == "status"):
            if len(sys.argv) > 2:
                if len(sys.argv) == 3:
                    projnum = sys.argv[2]
                    res = requests.get("https://intranet.hbtn.io/projects/{}.json"\
                                       .format(projnum),
                                       params={"auth_token" : token})
                    if (not res or res.status_code != 200):
                        print("Error with the request. Try refreshing credentials.")
                        print(res)
                        print(res.json())
                        sys.exit(1)

                    dat = res.json()
                    print("\033[1m{}\033[0m".format(dat["name"]))
                    for i in range(len(dat["tasks"])):
                        print("{}: {}".format(i, dat["tasks"][i]["title"]))
                else:
                    projnum = sys.argv[2]
                    tasknum = sys.argv[3]
                    res = requests.get("https://intranet.hbtn.io/projects/{}.json"\
                                       .format(projnum),
                                       params={"auth_token" : token})
                    if (not res or res.status_code != 200):
                        print("Error with the request. Try refreshing credentials.")
                        print(res)
                        print(res.json())
                        sys.exit(1)

                    dat = res.json()
                    task = dat["tasks"][int(tasknum)]
                    print("Task {}: \033[1m{}\033[0m".format(int(tasknum), task["title"]))
                    if task["checker_available"]:
                        print("Checker is available for this task")
                    else:
                        print("Checker is not available for this task")
            else:
                print("Not enough arguments. Run `checkercli --help`")
        elif (command == "check"):
            if len(sys.argv) >= 4:
                projnum = sys.argv[2]
                tasknum = sys.argv[3]
                res = requests.get("https://intranet.hbtn.io/projects/{}.json"\
                                   .format(projnum),
                                   params={"auth_token" : token})
                if (not res or res.status_code != 200):
                    print("Error with the request. Try refreshing credentials.")
                    print(res)
                    print(res.json())
                    sys.exit(1)

                dat = res.json()
                task_id = dat["tasks"][int(tasknum)]["id"]
                print("Checking task {} of project {}".format(tasknum,
                                                              dat["name"]))
                res = requests.post("https://intranet.hbtn.io/tasks/{}/start_correction.json"\
                                    .format(task_id),
                                    params={"auth_token" : token})
                dat = res.json()
                check_id = dat["id"]
                done = False
                while (not done):
                    time.sleep(1)
                    res = requests.get("https://intranet.hbtn.io/correction_requests/{}.json"\
                                       .format(check_id),
                                       params={"auth_token" : token})
                    dat = res.json()
                    if (dat["status"] == "Done"):
                        done = True
                        checks = dat["result_display"]["checks"]
                        for check in checks:
                            if (check["passed"]):
                                print("\033[32my\033[0m", end="")
                            else:
                                print("\033[31mn\033[0m", end="")
                        print("")
            else:
                print("Not enough arguments. Run `checkercli --help`")
        elif (command == "refresh"):
            getToken(refresh=True)
        else:
            print("Run `checkercli --help` for help")
    else:
        help()