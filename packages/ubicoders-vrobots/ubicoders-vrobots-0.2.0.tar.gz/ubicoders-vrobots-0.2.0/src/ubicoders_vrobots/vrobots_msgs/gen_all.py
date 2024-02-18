import subprocess

def get_args_base():
    return [
        '--gen-onefile',
        '--gen-object-api',
        '--gen-all'
    ]

def get_args_dot_net(fname):
    args = get_args_base()
    args.extend([
        '-n',
        '-o', fr'.\dotnet',
        fr'.\definitions\{fname}.fbs'
    ])
    return args

def get_args_python(fname):
    args = get_args_base()
    args.extend([
        '--python',
        '-o', fr'.\python',
        fr'.\definitions\{fname}.fbs'
    ])
    return args

def get_args_typescript(fname):
    args = get_args_base()
    args.extend([
        '--ts',
        '-o', fr'.\ts\{fname}',
        fr'.\definitions\{fname}.fbs'
    ])
    return args


# assumes window.
def generate_msg(fname):
    command = r'.\flatc.exe'
    
    print(f"Generating {fname} dotnet")
    args = get_args_dot_net(fname)
    subprocess.run([command] + args)
    
    print(f"Generating {fname} python")
    args = get_args_python(fname)
    subprocess.run([command] + args)
    
    print(f"Generating {fname} typescript")
    args = get_args_typescript(fname)
    subprocess.run([command] + args)



# for *.fbs in definitions, generate message.
def generate_all():
    import os
    for file in os.listdir(r'./definitions'):
        if 'vectors' in file:
            continue
        
        if file.endswith('.fbs'):
            fname = file[:-4]
            generate_msg(fname)


if __name__ == "__main__":
    generate_all()