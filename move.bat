@Echo Off
For /f "tokens=*" %%i in ('dir /ad /b /s "%~dp0"') do (
For /f "tokens=*" %%j in ('dir /a-d /b /s "%%i\new.MP4"') do (
Ren "%%j" "%%~nxi%%~xj"
Move "%%i\%%~nxi%%~xj" "%~dp0"\dowlod\"
Rd /q "%%i"
))
Pause
