@echo off
echo Arcee - Riot Crew Profiling System
echo 2011 Competition -- LOGO MOTION
echo.
echo Pit Crew sync script
echo.
echo Connect to Scouting1 and press [ENTER] to continue
pause > NUL

:: stop service
echo Halting Apache...
net stop djangoStackApache >NUL 2>&1

:: Copy DB
echo.
echo Copying Database...
xcopy "\\192.168.100.1\RiotCrew\database.db" "C:\Documents and Settings\r\BitNami DjangoStack projects\RiotCrew" /Y >NUL 2>&1

:: Copy images
echo.
echo Copying Robot Pictures...
xcopy "\\192.168.100.1\RiotCrew\media\Images\Robots\*.gif" "C:\Documents and Settings\r\BitNami DjangoStack projects\RiotCrew\media\Images\Robots" /Y >NUL 2>&1

:: stop service
echo.
echo Revivifying Apache...
net start djangoStackApache >NUL 2>&1

echo Complete. Press [ENTER] to exit.
pause > NUL
