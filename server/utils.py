import os
import time

def format_file_stat(path, name):
    full_path = os.path.join(path, name)
    stats = os.stat(full_path)
    
    # File type
    file_type = '-' if os.path.isfile(full_path) else 'd'
    
    # Permissions
    permissions = {
        '7': 'rwx',
        '6': 'rw-',
        '5': 'r-x',
        '4': 'r--',
        '3': '-wx',
        '2': '-w-',
        '1': '--x',
        '0': '---'
    }
    mode = oct(stats.st_mode)[-3:]
    perm = ''.join([permissions[digit] for digit in mode])
    
    # Number of links
    nlink = stats.st_nlink

    # User and group name
    uid_name = os.getlogin()
    gid_name = os.getlogin()
    
    # File size
    size = stats.st_size
    
    # Date format: 'Month Day HH:MM'
    mtime = time.strftime('%b %d %H:%M', time.gmtime(stats.st_mtime))
    
    return f'{file_type}{perm} {nlink} {uid_name} {gid_name} {size} {mtime} {name}'