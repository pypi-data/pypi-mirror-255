set NGSCXX_DIR=%~dp0
call "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Auxiliary/Build/vcvarsall.bat" amd64

 cl /c /MD /O2 /Ob2 /DNDEBUG /DWIN32 /D_WINDOWS /W3 /GR /EHsc  /DHAVE_NETGEN_SOURCES /DUSE_TIMEOFDAY /DTCL /DLAPACK /DUSE_PARDISO /DNGS_PYTHON /DNETGEN_PYTHON /DNG_PYTHON /DPYBIND11_SIMPLE_GIL_MANAGEMENT /D_WIN32_WINNT=0x1000 /DWNT /DWNT_WINDOW /DNOMINMAX /DMSVC_EXPRESS /D_CRT_SECURE_NO_WARNINGS /DHAVE_STRUCT_TIMESPEC /DWIN32 /std:c++17 -DMAX_SYS_DIM=3 /AVX2 /bigobj /MP /W1 /wd4068  /I"C:/gitlabci/tools/builds/3zsqG5ns/0/ngsolve/venv_ngs/Library/include" /I"C:/Python39/include" /I"%NGSCXX_DIR%/include" /I"%NGSCXX_DIR%/include/include" %*
