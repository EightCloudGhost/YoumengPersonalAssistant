; 幽梦个人助手 - Inno Setup 安装脚本
; 版本: 1.0.0

#define MyAppName "幽梦个人助手"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "幽梦工作室"
#define MyAppURL "https://github.com/youmeng"
#define MyAppExeName "幽梦个人助手.exe"

[Setup]
; 应用程序基本信息
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 安装目录设置
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; 输出设置
OutputDir=installer_output
OutputBaseFilename=幽梦个人助手_安装程序_v{#MyAppVersion}
SetupIconFile=resources\icons\app.ico

; 压缩设置
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; 权限设置
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; 界面设置
WizardStyle=modern
DisableProgramGroupPage=yes
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no

; 语言设置
ShowLanguageDialog=auto

; 卸载设置
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"
Name: "quicklaunchicon"; Description: "创建快速启动栏图标"; GroupDescription: "附加任务:"; Flags: unchecked

[Files]
; 主程序
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 资源文件（如果需要外部资源）
; Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"

; 桌面快捷方式
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; 快速启动栏
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 安装完成后运行程序（可选）
Filename: "{app}\{#MyAppExeName}"; Description: "立即运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除用户数据（可选，默认不删除）
; Type: filesandordirs; Name: "{app}\logs"
; Type: files; Name: "{app}\config.json"
; Type: files; Name: "{app}\youmeng.db"

[Code]
// 安装前检查是否已安装
function InitializeSetup(): Boolean;
var
  UninstallKey: String;
  UninstallString: String;
  ResultCode: Integer;
begin
  Result := True;
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1';
  
  if RegQueryStringValue(HKEY_CURRENT_USER, UninstallKey, 'UninstallString', UninstallString) then
  begin
    if MsgBox('检测到已安装旧版本，是否先卸载？', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(RemoveQuotes(UninstallString), '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;

// 卸载前提示是否保留用户数据
function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('是否保留用户数据（配置文件、数据库、日志）？' + #13#10 + #13#10 + 
            '选择"是"将只删除程序文件。' + #13#10 +
            '选择"否"将删除所有数据。', 
            mbConfirmation, MB_YESNO) = IDNO then
  begin
    DelTree(ExpandConstant('{app}\logs'), True, True, True);
    DeleteFile(ExpandConstant('{app}\config.json'));
    DeleteFile(ExpandConstant('{app}\youmeng.db'));
  end;
end;
