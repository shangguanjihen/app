@echo off
for /f "delims=" %%a in ('dir /ad /s /b') do (
    copy concat.bat "%%~fa"
    start "" "%%~fa\concat.bat"
)