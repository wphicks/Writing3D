@echo off
setlocal EnableDelayedExpansion
cd /d %~dp0
for /f %%i in ('findblender.bat') do set blenderexec=%%i
if "%blenderexec%" == "" set blenderexec=..\..\..\blender\blender.exe
echo "INVOCATION >> %blenderexec% --background --python ..\..\samples\cwapp.py -- %1 %2"
%blenderexec%  --background --python ..\..\samples\cwapp.py -- %1 %2
