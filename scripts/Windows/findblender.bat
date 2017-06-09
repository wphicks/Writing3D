@echo off
setlocal EnableDelayedExpansion
cd /d %~dp0
if not exist "%HOMEPATH%\.w3d.json" (
    if not exist "..\..\..\blender\blender.exe"(
        call :finish "%cd%\..\..\..\blender\blender.exe"
    ) else (
        call :finish "Not found"
    )
)
for /f "Tokens=* Delims=" %%x in (%HOMEPATH%\.w3d.json) do set "string=!string!%%x"

rem Remove quotes
set string=%string:"=%
rem Remove braces
set "string=%string:~1,-1%"
rem Replace colon+space with equal-sign
set "string=%string:: ==%"

call :parse "%string%"
goto :eos

:parse
set list=%1
set list=%list:"=%

for /f "tokens=1* delims=," %%a in ("%list%") do (
  if not "%%a" == "" call :sub "%%a"
  if not "%%b" == "" call :parse "%%b"
)
goto :eos

:sub
set pair=%1
for /f "tokens=1,2 delims==" %%a in (%pair%) do (
    set key=%%a
    set value=%%b
)
for /f "tokens=* delims= " %%a in ("%key%") do set key=%%a

if "%key%" == "Blender executable" call :finish %value%
goto :eos

:finish
echo %1
goto :eos

:eos
endlocal
