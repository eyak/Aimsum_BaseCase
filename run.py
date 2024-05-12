import subprocess
import os

AIMSUM_FN = 'c:\Program Files\Aimsun\Aimsun Next 23\Aimsun Next.exe'
PROJECT_FN = os.path.join(os.getcwd(), 'Base_Case_November.ang').replace('\\', '/')

print(PROJECT_FN)

# execute aimsum
subprocess.Popen([AIMSUM_FN, '--project', PROJECT_FN, '--script', 'test.py'])