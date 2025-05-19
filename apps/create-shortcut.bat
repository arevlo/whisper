@echo off
:: This batch file creates a shortcut to the dictation tool on your desktop
:: Run this once to set up the shortcut

echo Creating Whisper Dictation shortcut on desktop...

set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\Whisper Dictation.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0wdictate.bat" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "Whisper Dictation Tool" >> %SCRIPT%
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,138" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%

echo Shortcut created! You can now run the dictation tool by double-clicking "Whisper Dictation" on your Desktop.
pause
