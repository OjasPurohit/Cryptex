; Script generated for Cryptex - Secure File Encryption
; Compatible with Inno Setup 6+

#define MyAppName "Cryptex - Secure File Encryption"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Ojas Purohit"
#define MyAppExeName "Cryptex.exe"

[Setup]
; App Identity
AppId={{8B49B7DF-1F5B-4C9D-A3D2-E40409A6D29E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Icon and Assets
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=dist
OutputBaseFilename=Cryptex_Setup_Inno
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Cryptex.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  UserHome: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Initialize %USERPROFILE%\Cryptex directories
    UserHome := ExpandConstant('{userdocs}\..\Cryptex');
    ForceDirectories(UserHome + '\Encrypted');
    ForceDirectories(UserHome + '\Decrypted');
    ForceDirectories(UserHome + '\Vault');
  end;
end;

