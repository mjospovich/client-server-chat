
@echo off

REM Description: Closes the cmd window named Chat for the user
REM no report is generated

taskkill /f /fi "WINDOWTITLE eq Chat*"
taskkill /f /fi "WINDOWTITLE eq Chat*"