@echo off
setlocal EnableDelayedExpansion
cd /d %~dp0
for /f %%i in ('findblender.bat') do set blenderexec=%%i
if "%blenderexec%" == "Not found" set blenderexec="%cd%..\..\..\blender\blender.exe"
echo "INVOCATION >> %blenderexec% --background --python Writing3D\samples\cwapp.py -- %*"
%blenderexec%  --background --python %*
