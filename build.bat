:: Set up the attentive support project with all dependencies
@ECHO OFF
ECHO "Loading Visual Studio Settings"
call "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" x64
ECHO "Running cmake"
if not exist "build" mkdir build
cd build
cmake.exe -G "Visual Studio 17 2022" -DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE -DBUILD_SHARED_LIBS=TRUE -DCMAKE_BUILD_TYPE=Release -DVCPKG_TARGET_TRIPLET=x64-windows -DCMAKE_TOOLCHAIN_FILE=C:\dev\vcpkg\scripts\buildsystems\vcpkg.cmake ../src/Smile -Wno-dev -DCMAKE_INSTALL_PREFIX=../install
ECHO "Building project"
msbuild -maxCpuCount:8 -verbosity:minimal -p:Configuration=Release INSTALL.vcxproj 
cd ..
ECHO "Creating python virtual environment"
python.exe -m venv .venv 
ECHO "Activating virtual environment"
call ".venv\Scripts\activate"
ECHO "Installing requirements"
pip install -r requirements.txt
ECHO "All set."
set /p=Hit ENTER to continue...
