REM start "" /w "C:\Program Files (x86)\DHI\2014\bin\x64\MzLaunch.exe" sim11files\Scenario_002.sim11 -e "C:\Program Files (x86)\DHI\2014\bin\x64\mike11.exe" -y 3
REM "C:\Program Files (x86)\DHI\2014\bin\x64\MzLaunch.exe" sim11files\Scenario_002.sim11 -x
set path=%path%;C:\Program Files (x86)\DHI\2014\bin\x64
set dsn=C:\Users\julierozenberg\Documents\GitHub\create_files_for_mike11\sim11files\Scenario_002.sim11
start /w MzLaunch.exe %dsn% -x