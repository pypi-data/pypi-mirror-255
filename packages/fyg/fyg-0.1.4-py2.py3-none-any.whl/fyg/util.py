import os, json, base64, pprint

def read(fname):
	if not os.path.exists(fname):
		return
	f = open(fname, 'r')
	data = f.read()
	f.close()
	return data and json.loads(base64.b64decode(data).decode())

def write(fname, data):
	f = open(fname, 'w')
	f.write(base64.b64encode(json.dumps(data).encode()).decode())
	f.close()

def selnum(data, rower=pprint.pformat):
    if not data:
        return print("nothing to select - you select nothing")
    ld = len(data)
    lines = ["#%s :: %s"%(i + 1, rower(data[i])) for i in range(ld)]
    print("you have %s options:\n"%(ld,), *lines, sep="\n")
    while True:
        whatdo = input("\nplease enter a number from 1 to %s: "%(ld,))
        try:
            whatdo = int(whatdo)
        except:
            print("'%s' is not a usable answer - try again!"%(whatdo,))
        else:
            if whatdo > 0 and whatdo <= ld:
                whatdo -= 1
                print("\n\nyou've selected: %s"%(lines[whatdo],))
                return data[whatdo]
            print("'%s' is out of range - try again!"%(whatdo,))

def confirm(condition, assumeYes=False):
    prompt = "%s? %s "%(condition, assumeYes and "[Y/n]" or "[N/y]")
    resp = input(prompt).lower()
    if assumeYes:
        return not resp.startswith("n")
    else:
        return resp.startswith("y")