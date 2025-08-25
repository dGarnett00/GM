@echo off
REM Build Qt resource modules for development. Requires pyrcc5 in PATH.
SET PYRCC=pyrcc5
IF NOT EXIST "%PYRCC%" (
  REM try from Python Scripts directory
  FOR %%P IN ("%LOCALAPPDATA%\Programs\Python\*\Scripts\pyrcc5.exe" "%USERPROFILE%\AppData\Local\Programs\Python\*\Scripts\pyrcc5.exe") DO (
    IF EXIST %%~P SET PYRCC=%%~P & GOTO :FOUND
  )
)
:FOUND
echo Using %PYRCC%
REM Optional: run QSS preprocessor to generate processed QSS under build/styles
IF "%1"=="--preprocess" (
  echo Running QSS preprocessor (apply mode)...
  python tools\qss_preprocess.py --apply --outdir build\styles
)
%PYRCC% -o gui\resources\rc_icons.py gui\resources\icons.qrc
%PYRCC% -o gui\resources\rc_skill_icons.py gui\resources\skill_icons.qrc
echo Done.
PAUSE
