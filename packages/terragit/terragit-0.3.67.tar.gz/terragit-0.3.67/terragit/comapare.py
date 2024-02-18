import json
import pandas as pd
import os
import subprocess
import csv
import terragit.terraConf as terraconf



class Compare:
    def __init__(self, gitlab_token, git_url):
        self.gitlab_token = gitlab_token
        self.git_url = git_url

    def list_state(self, infra, file1):

        cmd = "cd " + infra + " && terragrunt state list > ~/" + file1
        popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                 encoding='utf8')
        lines = popen.communicate(input='\n')[0].split("\n")

    def compare_state(self, infra1, infra2, file1, file2):
        self.list_state(infra1, file1)
        self.list_state(infra2, file2)
        fichier1 = open(os.path.expanduser(os.path.join("~/" + file1)), 'r')

        fichier1.close()

    def compare_tf_states(self, state1, state2):
        pwd =terraconf.TerraConf.current_path(self)
        pwd_f= pwd+"terragit-compare"

        folder_path=terraconf.TerraConf.goTo_or_create_folder(self,pwd_f)

        f = open(state1)

        data = f.read().rstrip()
        x = json.loads(data)

        df = pd.json_normalize(x, record_path=['resources'],
                               errors='ignore')

        f.close()
        f2 = open(state2)
        data2 = f2.read().rstrip()
        x = json.loads(data2)

        df2 = pd.json_normalize(x, record_path=['resources'],
                                errors='ignore')

        f2.close()

        l1 = []
        l23 = []
        State_list1 = ["source"]
        State_list = ["destination"]
        State_list3 = []
        new_list1 = []
        new_list = []
        for i in df.columns:
            l1.append([i, df[i].values])
        l2 = []
        for i in df2.columns:
            l2.append([i, df[i].values])

        l = [["object", "source", "destination"]]
        for i in l1:

            for j in l2:

                if (i[0] == j[0]):

                    l.append([i[0], i[1], j[1]])


        j=0
        while j<len(l[1][1]):
            cc=l[1][1][j]+"."+l[2][1][j]+"."+l[3][1][j]+"."+l[4][1][j]


            State_list.append(cc)

            j=j+1

        jr=0
        while jr<len(l[2][1]):

            cr=l[1][2][jr]+"."+l[2][2][jr]+"."+l[3][2][jr]+"."+l[4][2][jr]


            State_list1.append(cr)

            jr=jr+1



        for j in range(len(l[6][1])):

            l24=[["Property", "destination", "Source"]]
            jp=l[1][1][j]+"."+l[2][1][j]+"."+l[3][1][j]+"."+l[4][1][j]
            df22 = pd.json_normalize(l[6][1][j][0],
                                errors='ignore')

            df220 = pd.json_normalize(l[6][2][j][0],
                                     errors='ignore')


            for i in df22.columns:
                l24.append([i, df22[i].values, df220[i].values])
            self.write_tuple_liste_in_csv( l24, folder_path+'/S_list'+jp+'.csv')
        jj = 0
        new_list.append(State_list[0])
        for i in range(1, len(State_list)):

            l = State_list[0:jj]

            if State_list[i] not in l:

                new_list.append(State_list[i])
            else:

                continue
            jj += 1
        jk = 0
        new_list1.append(State_list1[0])
        for i in range(1, len(State_list1)):

            l = State_list1[0:jk]
            if i not in l:
                new_list1.append(State_list1[i])
            else:
                continue
            jk += 1

        for i in range(len(new_list)):
            State_list3.append([new_list[i], new_list1[i]])
        self.write_tuple_liste_in_csv( State_list3, folder_path+'/State_list.csv')


    def write_tuple_liste_in_csv(self, list, file):

        f_State_list = open(file, 'w')

        writer = csv.writer(f_State_list)

        writer.writerows(list)

        f_State_list.close()


