Option Explicit

Dim shell, fso, projectDir, userProfile, candidates, pythonw, candidate, command, finder, foundPaths
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

projectDir = fso.GetParentFolderName(WScript.ScriptFullName)
userProfile = shell.ExpandEnvironmentStrings("%USERPROFILE%")
candidates = Array( _
    projectDir & "\.venv\Scripts\pythonw.exe", _
    userProfile & "\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe" _
)

pythonw = ""
For Each candidate In candidates
    If fso.FileExists(candidate) Then
        pythonw = candidate
        Exit For
    End If
Next

If pythonw = "" Then
    On Error Resume Next
    Set finder = shell.Exec(shell.ExpandEnvironmentStrings("%ComSpec%") & " /c where pythonw.exe")
    foundPaths = Trim(finder.StdOut.ReadAll)
    If Err.Number = 0 And foundPaths <> "" Then
        pythonw = Split(foundPaths, vbCrLf)(0)
    End If
    Err.Clear
    On Error GoTo 0
End If

If pythonw = "" Then
    MsgBox "Python was not found. Create the project .venv and install requirements.txt first.", 16, "Mandros Blind"
    WScript.Quit 1
End If

command = Chr(34) & pythonw & Chr(34) & " " & Chr(34) & projectDir & "\run_gui.pyw" & Chr(34)
shell.Run command, 0, False
