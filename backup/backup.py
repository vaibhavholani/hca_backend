import subprocess
from datetime import datetime

def backup_postgresql_database(username, database_name, backup_file_path):
    try:
        # Construct the pg_dump command
        command = [
            'pg_dump',
            '-U', username,
            '-d', database_name,
            '-f', backup_file_path
        ]

        # Execute the command
        subprocess.run(command, check=True)
        print("Backup created successfully!")
        return {"status": "okay", "message": "Backup Created"}

    except subprocess.CalledProcessError as e:
        print("Error creating backup:", "message": "Backup Failed")
        return {"status": "error"}

