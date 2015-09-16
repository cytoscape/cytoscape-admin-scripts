@echo off
REM Target Cytoscape version for this script
set CYTOSCAPE_VERSION=3.3.0
REM Cytoscpae App Store location
set APP_STORE_URL=apps.cytoscape.org
REM Minimal Java version
set MIN_JAVA_VERSION=18000
set MIN_JAVA_VERSION_STR=8.0
REM Error checking flags
set pass=true
set 64bit_pass=true
set java64bit_pass=true
set javahome_pass=true
set javaversion_pass=true
set appstore_pass=true
REM Timeout values
set TRACERT_TIMEOUT=30000
set PING_TIMEOUT=30000
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
where java >nul 2>&1
if errorlevel 1 (
    set pass=false
    echo Problem: Java not installed.
    echo Please install Java and re-run this script again.
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
if %PROCESSOR_ARCHITECTURE%==x86 (
    set pass=false
    set 64bit_pass=false
    echo Problem: Your system is 32 bit: %PROCESSOR_ARCHITECTURE%
    echo.
) else (
    echo Your system is 64 bit as required
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
REM Test for Java version
REM ---------------------
for /f tokens^=2-5^ delims^=.-_^" %%j in ('java -fullversion 2^>^&1') do set "jver=%%j%%k%%l%%m"
if %jver% LSS %MIN_JAVA_VERSION% (
    set pass=false
    set javaversion_pass=false
    echo Problem: Your Java version is less than 8.0
    echo.
) else (
    echo Your Java version is at least %MIN_JAVA_VERSION_STR% as required
    echo.
)
REM Test if Java 64 bit
REM -------------------
java -d64 -version >nul 2>&1
if errorlevel 1 (
    set java64bit_pass=false
    echo Java is 32 bit
    echo.
) else (
    echo Java is 64 bit
    echo.
)

:appcheck

REM Test for "app" store
REM --------------------
ping -n 1 -w %PING_TIMEOUT% %APP_STORE_URL% | find "TTL=" >nul
if errorlevel 1 (
    set pass=false
    set appstore_pass=false
    echo Problem: The "app" store at %APP_STORE_URL% is not reachable with a timeout of %PING_TIMEOUT%ms
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
    echo Your system still has some issues.
    echo Please fix those and re-run this script again:
    if %64bit_pass% == false (
        echo - Your system is not 64 bit
    )
    if %javaversion_pass% == false (
        echo - You need at least Java version %MIN_JAVA_VERSION_STR%
    )
    if %appstore_pass% == false (
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
REM Wait to close window
REM --------------------
pause
