# Windows EXE

This folder contains the native Windows console build for the crystallic reorganizer.

Files:
- `CrystallicReorganizer.cs`: C# source for the executable
- `build_exe.ps1`: rebuild script that compiles the source with the local .NET Framework compiler
- `dist/CrystallicReorganizer.exe`: compiled executable output

Usage:
- `.\windows_exe\dist\CrystallicReorganizer.exe`
- `.\windows_exe\dist\CrystallicReorganizer.exe --apply`
- `.\windows_exe\dist\CrystallicReorganizer.exe --source-root C:\path\to\incoming --destination-root C:\path\to\crystallic_shape_shifting`
