import yaml

with open('./environment.yml', 'r') as e:
    y = yaml.safe_load(e)

    print(y['dependencies'])

    with open('./requirements.txt', 'w') as r:
        for d in y['dependencies']:
            if isinstance(d, dict):
                for p in d['pip']:
                    r.write(str(p) + '\n')
            else:
                if 'matplotlib' in d:
                    r.write('matplotlib\n')
                else:
                    r.write(str(d) + '\n')
        r.close()
    e.close()


