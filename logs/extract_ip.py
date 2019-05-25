import re
f = open("copy.txt", "r")
f_cont = f.readlines()
f.close()
f = open("all_ip.txt", "w")
res = []
for line in f_cont:
	tmp = re.findall(r'user ip:.*',line)
	if tmp!=[]:
		tmp = tmp[0]
		f.write(".".join(re.findall(r'[0-9]+',tmp))+'\n')

f.close()
