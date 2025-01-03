import subprocess
from datetime import datetime
import os

def backup_postgresql_database(username, database_name, password, backup_file_path):
    try:
        # Construct the pg_dump command
       
        env = os.environ.copy()
        env["PGPASSWORD"] = password

        command = [
            'pg_dump',
            '-U', username,
            '-d', database_name,
            '--no-owner',
            '--no-acl'
            '-f', backup_file_path,
        ]

        # Execute the command
        subprocess.run(command, check=True, env=env)
        print("Backup created successfully!")
        return {"status": "okay", "message": "Backup Created"}

    except subprocess.CalledProcessError as e:
        print("Error creating backup: " + e)
        return {"status": "error", "message": "Backup Failed"}

