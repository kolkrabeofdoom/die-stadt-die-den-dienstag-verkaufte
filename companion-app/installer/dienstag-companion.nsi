Unicode true
RequestExecutionLevel user
SetCompressor /SOLID lzma

!ifndef SOURCE_EXE
  !error "SOURCE_EXE muss auf die gebaute Companion-App zeigen."
!endif

!ifndef OUTPUT_EXE
  !define OUTPUT_EXE "Dienstag-Companion-Setup.exe"
!endif

Name "Dienstag-Companion"
OutFile "${OUTPUT_EXE}"
InstallDir "$LOCALAPPDATA\Programs\Dienstag-Companion"
InstallDirRegKey HKCU "Software\Dienstag-Companion" "InstallDir"

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Dienstag-Companion" SEC_MAIN
  SetOutPath "$INSTDIR"
  File /oname=Dienstag-Companion.exe "${SOURCE_EXE}"
  WriteUninstaller "$INSTDIR\Deinstallieren.exe"

  CreateDirectory "$SMPROGRAMS\Dienstag-Companion"
  CreateShortcut "$SMPROGRAMS\Dienstag-Companion\Dienstag-Companion.lnk" "$INSTDIR\Dienstag-Companion.exe"
  CreateShortcut "$SMPROGRAMS\Dienstag-Companion\Deinstallieren.lnk" "$INSTDIR\Deinstallieren.exe"

  WriteRegStr HKCU "Software\Dienstag-Companion" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Dienstag-Companion" "DisplayName" "Dienstag-Companion"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Dienstag-Companion" "DisplayVersion" "0.1.0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Dienstag-Companion" "Publisher" "Die Stadt, die den Dienstag verkaufte"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Dienstag-Companion" "DisplayIcon" "$INSTDIR\Dienstag-Companion.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Dienstag-Companion" "UninstallString" '"$INSTDIR\Deinstallieren.exe"'
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Dienstag-Companion" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Dienstag-Companion" "NoRepair" 1
SectionEnd

Section "Uninstall"
  Delete "$SMPROGRAMS\Dienstag-Companion\Dienstag-Companion.lnk"
  Delete "$SMPROGRAMS\Dienstag-Companion\Deinstallieren.lnk"
  RMDir "$SMPROGRAMS\Dienstag-Companion"

  Delete "$INSTDIR\Dienstag-Companion.exe"
  Delete "$INSTDIR\Deinstallieren.exe"
  RMDir "$INSTDIR"

  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Dienstag-Companion"
  DeleteRegKey HKCU "Software\Dienstag-Companion"
SectionEnd
