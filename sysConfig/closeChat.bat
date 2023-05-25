
@echo off

REM Description: Closes the cmd window named Chat for the user
REM no report is generated

taskkill /F /FI "WINDOWTITLE eq Chat*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Chat*" >nul 2>&1
