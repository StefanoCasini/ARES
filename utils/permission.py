import os
import shutil

def fix_ownership(path):
    """
    Changes ownership of a specific file or folder to the SUDO user.
    Safe to call even if the file doesn't exist yet.
    """
    sudo_uid = os.environ.get("SUDO_UID")
    sudo_gid = os.environ.get("SUDO_GID")

    if not sudo_uid or not sudo_gid:
        return  # Not running as sudo, nothing to do

    uid = int(sudo_uid)
    gid = int(sudo_gid)

    try:
        # If it's a file, simple chown
        if os.path.isfile(path):
            os.chown(path, uid, gid)
        
        # If it's a directory, chown the dir (and optionally recurse if needed)
        elif os.path.isdir(path):
            os.chown(path, uid, gid)
            
    except FileNotFoundError:
        pass # File wasn't created (e.g., scan failed), ignore
    except Exception as e:
        print(f"[!] Warn: Could not fix permissions for {path}: {e}")