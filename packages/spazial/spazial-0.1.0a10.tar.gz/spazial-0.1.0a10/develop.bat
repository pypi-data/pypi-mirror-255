@echo off
call ../.venv/Scripts/activate.bat

maturin build --release

for %%F in (target\wheels\*.whl) do (
    set "WHEEL_PATH=%%~fF"
)

call "D:\Forschung\Glasbruch\Code\packages\fracsuite\.venv\scripts\pip.exe" install %WHEEL_PATH% --force-reinstall


cd ..
call .venv/Scripts/activate.bat