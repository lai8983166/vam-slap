"""Compile-check against the installed VaM API; DLL is for checking only."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).parent
managed = Path('F:/Virt A Mate/Virt A Mate/VaM_Data/Managed')
csc = sorted(Path('C:/Program Files/dotnet/sdk').glob('*/Roslyn/bincore/csc.dll'))[-1]
build = root/'build'
build.mkdir(exist_ok=True)
refs = ['mscorlib.dll','System.dll','System.Core.dll','Assembly-CSharp.dll',
        'UnityEngine.dll','UnityEngine.CoreModule.dll','UnityEngine.UI.dll',
        'UnityEngine.PhysicsModule.dll','UnityEngine.UIModule.dll']
source = sys.argv[1] if len(sys.argv) > 1 else 'SlapReferenceSetup'
args = ['dotnet', str(csc), '/nologo', '/noconfig', '/nostdlib+', '/target:library',
        '/langversion:6', '/out:'+str(build/(source+'.dll'))]
args += ['/reference:'+str(managed/name) for name in refs]
args += [str(root/(source+'.cs'))]
subprocess.run(args, check=True)
print('Compiled against installed VaM assemblies (C# 6).')
