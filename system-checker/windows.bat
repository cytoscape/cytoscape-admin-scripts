@echo off

REM This is a handy reference for this scripting language: https://technet.microsoft.com/en-us/library/cc754335(v=ws.11).aspx

REM Target Cytoscape version for this script
set CYTOSCAPE_VERSION=3.9.0

REM Cytoscpae App Store location
set APP_STORE_URL=apps.cytoscape.org

REM Minimal Java version
set MIN_JAVA_VERSION=11
set MIN_JAVA_VERSION_STR=11
set MAX_JAVA_VERSION=11
set MAX_JAVA_VERSION_STR=11

REM Recommended link to download Java
set JAVA_DOWNLOAD=https://adoptopenjdk.net/?variant=openjdk11&jvmVariant=hotspot

REM Error checking flags
set pass=true
set sys64bit_pass=true
set java64bit_pass=true
set javahome_pass=true
set javaversion_pass=true
set appstore_pass=true

REM Timeout values
set TRACERT_TIMEOUT=30000

echo.
echo Cytoscape System Requirements Checker for Windows
echo -------------------------------------------------
echo.
echo Target Cytoscape version: %CYTOSCAPE_VERSION%
echo.
echo.

REM Windows version
REM ---------------
echo Your Windows version is:
ver
echo.

REM Test if Java installed
REM ----------------------
java -help >nul 2>&1
if %errorlevel% NEQ 0 (
    set pass=false
    echo Problem: Java not installed.
    echo.
    set javaversion_pass=false
    goto appcheck
    exit
) else (
    echo Java is installed
    echo.
)

REM Test for 64 bit
REM ---------------
if %PROCESSOR_ARCHITECTURE% == x86 (
    set sys64bit_pass=false
    echo Your system is 32 bit: %PROCESSOR_ARCHITECTURE%
    echo.
) else (
    echo Your system is 64 bit
    echo.
)

REM Test for JAVA_HOME environment variable
REM ---------------------------------------
if "%JAVA_HOME%" == "" (
    set javahome_pass=false
    echo JAVA_HOME is not set
    echo.
) else (
    echo Your JAVA_HOME is set to %JAVA_HOME%
    echo.
)

REM Test for Java version ... could look like 1.8.0_181 or 9+142
REM ------------------------------------------------------------
for /f tokens^=2-5^ delims^=.-_+^" %%j in ('java -fullversion 2^>^&1') do (
	set jver[0]=%%j
	set jver[1]=%%k
	set jver[2]=%%l
	set jver[3]=%%m
)
set jmajorver=%jver[0]%
if "%jmajorver%" EQU "1" (
	set jmajorver=%jver[1]%
)
echo Your Java Major version is %jmajorver%

if %jmajorver% LSS %MIN_JAVA_VERSION% (
    set pass=false
    set javaversion_pass=false
    echo Problem: Your Java version is less than version %MIN_JAVA_VERSION_STR%
    echo.
) else (
    echo Your Java version is at least version %MIN_JAVA_VERSION_STR% as required
    echo.
)
if %jmajorver% GTR %MAX_JAVA_VERSION% (
    set pass=false
    set javaversion_pass=false
    echo Problem: Your Java version is greater than version %MAX_JAVA_VERSION_STR%
    echo.
) else (
    echo Your Java version is no higher than version %MAX_JAVA_VERSION_STR% as required
    echo.
)

:appcheck

REM Test for "app" store
REM --------------------
curl -I https://%APP_STORE_URL% | find "200 OK" >nul
if %errorlevel% NEQ 0 (
    set pass=false
    set appstore_pass=false
    echo Problem: The "app" store at %APP_STORE_URL% is not reachable
    echo.
) else (
    echo The "app" store at %APP_STORE_URL% is reachable
    echo.
)
echo.

REM Summary
REM -------
echo.
echo Summary
echo -------
echo.
if %pass% == true (
    echo Success! You are ready to run Cytoscape %CYTOSCAPE_VERSION%
) else (
    echo Your system has some issues.
    echo Please fix those and re-run this script again:
    if %sys64bit_pass% == true (
        if %java64bit_pass% NEQ true (
            echo - Your system is 64 bit but your Java is only 32 bit
            echo - Link to download 64 bit Java: %JAVA_DOWNLOAD%
        )
    )
    if %javaversion_pass% NEQ true (
        echo - You need at least Java version %MIN_JAVA_VERSION_STR%, but not greater than Java version %MAX_JAVA_VERSION_STR%
        echo - Link to download Java: %JAVA_DOWNLOAD%
    )
    if %appstore_pass% NEQ true (
        echo - App store at %APP_STORE_URL% is not reachable
    )
)
echo.
echo.
echo.

REM Java -version
REM -------------
echo More details on Java
echo --------------------
echo.
java -version
echo.
echo.
echo.

if %appstore_pass% NEQ true (
    REM Trace route
    REM -----------
    echo More details on %APP_STORE_URL%
    echo ----------------------------------
    echo.
    echo Going to run trace route command for %APP_STORE_URL% with timeout of %TRACERT_TIMEOUT%ms now...
    tracert -w %TRACERT_TIMEOUT% %APP_STORE_URL%
    echo.
    echo.
    echo.
)
REM Wait to close window
REM --------------------
pause
