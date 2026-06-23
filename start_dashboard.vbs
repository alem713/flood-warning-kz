Option Explicit

Dim shell, fileSystem, scriptFolder, launcherPath, pythonPath, command, exitCode

Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")

scriptFolder = fileSystem.GetParentFolderName(WScript.ScriptFullName)
launcherPath = shell.ExpandEnvironmentStrings("%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe")

Do
    command = """" & launcherPath & """ -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & scriptFolder & "\run_dashboard.ps1"""
    exitCode = shell.Run(command, 0, True)
    WScript.Sleep 3000
Loop
