; *** Inno Setup 简体中文语言文件 ***
; 适用于 Inno Setup 6.x

[LangOptions]
LanguageName=简体中文
LanguageID=$0804
LanguageCodePage=936

[Messages]
SetupAppTitle=安装
SetupWindowTitle=安装 - %1
UninstallAppTitle=卸载
UninstallAppFullTitle=%1 卸载

InformationTitle=信息
ConfirmTitle=确认
ErrorTitle=错误

SetupLdrStartupMessage=现在将安装 %1。您想要继续吗？
LdrCannotCreateTemp=无法创建临时文件。安装中止
LdrCannotExecTemp=无法执行临时目录中的文件。安装中止

LastErrorMessage=%1。%n%n错误 %2: %3
SetupFileMissing=安装目录中缺少文件 %1。请修正此问题或获取程序的新副本。
SetupFileCorrupt=安装文件已损坏。请获取程序的新副本。
SetupFileCorruptOrWrongVer=安装文件已损坏，或者与此安装程序的版本不兼容。请修正此问题或获取程序的新副本。
InvalidParameter=命令行中传递了无效参数：%n%n%1
SetupAlreadyRunning=安装程序已在运行。
WindowsVersionNotSupported=此程序不支持您计算机当前运行的 Windows 版本。
WindowsServicePackRequired=此程序需要 %1 Service Pack %2 或更高版本。
NotOnThisPlatform=此程序无法在 %1 上运行。
OnlyOnThisPlatform=此程序必须在 %1 上运行。
OnlyOnTheseArchitectures=此程序只能安装在为以下处理器架构设计的 Windows 版本上：%n%n%1
WinVersionTooLowError=此程序需要 %1 版本 %2 或更高版本。
WinVersionTooHighError=此程序无法安装在 %1 版本 %2 或更高版本上。
AdminPrivilegesRequired=安装此程序时您必须以管理员身份登录。
PowerUserPrivilegesRequired=安装此程序时您必须以管理员或 Power Users 组成员的身份登录。
SetupAppRunningError=安装程序检测到 %1 当前正在运行。%n%n请立即关闭其所有实例，然后单击"确定"继续，或者单击"取消"退出。
UninstallAppRunningError=卸载程序检测到 %1 当前正在运行。%n%n请立即关闭其所有实例，然后单击"确定"继续，或者单击"取消"退出。

PrivilegesRequiredOverrideTitle=选择安装模式
PrivilegesRequiredOverrideInstruction=选择安装模式
PrivilegesRequiredOverrideText1=%1 可以为所有用户安装（需要管理员权限），或者仅为您安装。
PrivilegesRequiredOverrideText2=%1 只能为您安装，或者为所有用户安装（需要管理员权限）。
PrivilegesRequiredOverrideAllUsers=为所有用户安装(&A)
PrivilegesRequiredOverrideAllUsersRecommended=为所有用户安装(&A)（推荐）
PrivilegesRequiredOverrideCurrentUser=仅为我安装(&M)
PrivilegesRequiredOverrideCurrentUserRecommended=仅为我安装(&M)（推荐）

ErrorCreatingDir=安装程序无法创建目录"%1"
ErrorTooManyFilesInDir=无法在目录"%1"中创建文件，因为其中包含的文件太多

ExitSetupTitle=退出安装
ExitSetupMessage=安装尚未完成。如果现在退出，程序将不会被安装。%n%n您可以稍后再次运行安装程序来完成安装。%n%n退出安装？
AboutSetupMenuItem=关于安装程序(&A)...
AboutSetupTitle=关于安装程序
AboutSetupMessage=%1 版本 %2%n%3%n%n%1 主页：%n%4
AboutSetupNote=

TranslatorNote=

ButtonBack=< 上一步(&B)
ButtonNext=下一步(&N) >
ButtonInstall=安装(&I)
ButtonOK=确定
ButtonCancel=取消
ButtonYes=是(&Y)
ButtonYesToAll=全是(&A)
ButtonNo=否(&N)
ButtonNoToAll=全否(&O)
ButtonFinish=完成(&F)
ButtonBrowse=浏览(&B)...
ButtonWizardBrowse=浏览(&R)...
ButtonNewFolder=新建文件夹(&M)

SelectLanguageTitle=选择安装语言
SelectLanguageLabel=选择安装过程中要使用的语言。

ClickNext=单击"下一步"继续，或单击"取消"退出安装。
BeveledLabel=
BrowseDialogTitle=浏览文件夹
BrowseDialogLabel=在下面的列表中选择一个文件夹，然后单击"确定"。
NewFolderName=新建文件夹

WelcomeLabel1=欢迎使用 [name] 安装向导
WelcomeLabel2=此程序将在您的计算机上安装 [name/ver]。%n%n建议您在继续之前关闭所有其他应用程序。

WizardPassword=密码
PasswordLabel1=此安装程序受密码保护。
PasswordLabel3=请输入密码，然后单击"下一步"继续。密码区分大小写。
PasswordEditLabel=密码(&P):
IncorrectPassword=您输入的密码不正确。请重试。

WizardLicense=许可协议
LicenseLabel=请在继续之前阅读以下重要信息。
LicenseLabel3=请阅读以下许可协议。您必须接受此协议的条款才能继续安装。
LicenseAccepted=我接受协议(&A)
LicenseNotAccepted=我不接受协议(&D)

WizardInfoBefore=信息
InfoBeforeLabel=请在继续之前阅读以下重要信息。
InfoBeforeClickLabel=准备好继续安装后，请单击"下一步"。
WizardInfoAfter=信息
InfoAfterLabel=请在继续之前阅读以下重要信息。
InfoAfterClickLabel=准备好继续安装后，请单击"下一步"。

WizardUserInfo=用户信息
UserInfoDesc=请输入您的信息。
UserInfoName=用户名(&U):
UserInfoOrg=组织(&O):
UserInfoSerial=序列号(&S):
UserInfoNameRequired=您必须输入用户名。

WizardSelectDir=选择目标位置
SelectDirDesc=将 [name] 安装到哪里？
SelectDirLabel3=安装程序将把 [name] 安装到以下文件夹中。
SelectDirBrowseLabel=单击"下一步"继续。如果您想选择其他文件夹，请单击"浏览"。
DiskSpaceGBLabel=至少需要 [gb] GB 的可用磁盘空间。
DiskSpaceMBLabel=至少需要 [mb] MB 的可用磁盘空间。
CannotInstallToNetworkDrive=安装程序无法安装到网络驱动器。
CannotInstallToUNCPath=安装程序无法安装到 UNC 路径。
InvalidPath=您必须输入带盘符的完整路径；例如：%n%nC:\APP%n%n或者以下格式的 UNC 路径：%n%n\\server\share
InvalidDrive=您选择的驱动器或 UNC 共享不存在或无法访问。请选择其他位置。
DiskSpaceWarningTitle=磁盘空间不足
DiskSpaceWarning=安装程序至少需要 %1 KB 的可用空间，但所选驱动器只有 %2 KB 可用空间。%n%n您想要继续吗？
DirNameTooLong=文件夹名或路径太长。
InvalidDirName=文件夹名无效。
BadDirName32=文件夹名不能包含以下任何字符：%n%n%1
DirExistsTitle=文件夹已存在
DirExists=文件夹：%n%n%1%n%n已存在。您想要安装到该文件夹吗？
DirDoesntExistTitle=文件夹不存在
DirDoesntExist=文件夹：%n%n%1%n%n不存在。您想要创建该文件夹吗？

WizardSelectComponents=选择组件
SelectComponentsDesc=应该安装哪些组件？
SelectComponentsLabel2=选择您想要安装的组件；清除您不想安装的组件。准备好后单击"下一步"。
FullInstallation=完全安装
CompactInstallation=简洁安装
CustomInstallation=自定义安装
NoUninstallWarningTitle=组件已存在
NoUninstallWarning=安装程序检测到以下组件已安装在您的计算机上：%n%n%1%n%n取消选择这些组件将不会卸载它们。%n%n您想要继续吗？
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceGBLabel=当前选择至少需要 [gb] GB 的磁盘空间。
ComponentsDiskSpaceMBLabel=当前选择至少需要 [mb] MB 的磁盘空间。

WizardSelectTasks=选择附加任务
SelectTasksDesc=应该执行哪些附加任务？
SelectTasksLabel2=选择安装 [name] 时您想要执行的附加任务，然后单击"下一步"。

WizardSelectProgramGroup=选择开始菜单文件夹
SelectStartMenuFolderDesc=安装程序应该在哪里放置程序的快捷方式？
SelectStartMenuFolderLabel3=安装程序将在以下"开始"菜单文件夹中创建程序的快捷方式。
SelectStartMenuFolderBrowseLabel=单击"下一步"继续。如果您想选择其他文件夹，请单击"浏览"。
MustEnterGroupName=您必须输入文件夹名。
GroupNameTooLong=文件夹名或路径太长。
InvalidGroupName=文件夹名无效。
BadGroupName=文件夹名不能包含以下任何字符：%n%n%1
NoProgramGroupCheck2=不要创建开始菜单文件夹(&D)

WizardReady=准备安装
ReadyLabel1=安装程序现在准备开始在您的计算机上安装 [name]。
ReadyLabel2a=单击"安装"继续安装，或者如果您想查看或更改任何设置，请单击"上一步"。
ReadyLabel2b=单击"安装"继续安装。
ReadyMemoUserInfo=用户信息：
ReadyMemoDir=目标位置：
ReadyMemoType=安装类型：
ReadyMemoComponents=所选组件：
ReadyMemoGroup=开始菜单文件夹：
ReadyMemoTasks=附加任务：

WizardPreparing=准备安装
PreparingDesc=安装程序正在准备在您的计算机上安装 [name]。
PreviousInstallNotCompleted=上一个程序的安装/卸载未完成。您需要重新启动计算机以完成该安装。%n%n重新启动计算机后，再次运行安装程序以完成 [name] 的安装。
CannotContinue=安装程序无法继续。请单击"取消"退出。
ApplicationsFound=以下应用程序正在使用需要由安装程序更新的文件。建议您允许安装程序自动关闭这些应用程序。
ApplicationsFound2=以下应用程序正在使用需要由安装程序更新的文件。建议您允许安装程序自动关闭这些应用程序。安装完成后，安装程序将尝试重新启动这些应用程序。
CloseApplications=自动关闭应用程序(&A)
DontCloseApplications=不要关闭应用程序(&D)
ErrorCloseApplications=安装程序无法自动关闭所有应用程序。建议您在继续之前关闭所有使用需要由安装程序更新的文件的应用程序。
PrepareToInstallNeedsRestart=安装程序必须重新启动您的计算机。重新启动计算机后，请再次运行安装程序以完成 [name] 的安装。%n%n您想要现在重新启动吗？

WizardInstalling=正在安装
InstallingLabel=请稍候，安装程序正在将 [name] 安装到您的计算机上。

FinishedHeadingLabel=[name] 安装向导完成
FinishedLabelNoIcons=安装程序已在您的计算机上安装了 [name]。
FinishedLabel=安装程序已在您的计算机上安装了 [name]。可以通过选择安装的快捷方式来启动此应用程序。
ClickFinish=单击"完成"退出安装程序。
FinishedRestartLabel=要完成 [name] 的安装，安装程序必须重新启动您的计算机。您想要现在重新启动吗？
FinishedRestartMessage=要完成 [name] 的安装，安装程序必须重新启动您的计算机。%n%n您想要现在重新启动吗？
ShowReadmeCheck=是，我想查看自述文件
YesRadio=是，现在重新启动计算机(&Y)
NoRadio=否，我将稍后重新启动计算机(&N)
RunEntryExec=运行 %1
RunEntryShellExec=查看 %1

ChangeDiskTitle=安装程序需要下一张磁盘
SelectDiskLabel2=请插入磁盘 %1 并单击"确定"。%n%n如果此磁盘上的文件位于与下面显示的不同的文件夹中，请输入正确的路径或单击"浏览"。
PathLabel=路径(&P):
FileNotInDir2=在"%2"中找不到文件"%1"。请插入正确的磁盘或选择其他文件夹。
SelectDirectoryLabel=请指定下一张磁盘的位置。

SetupAborted=安装未完成。%n%n请修正问题后再运行安装程序。
AbortRetryIgnoreSelectAction=选择操作
AbortRetryIgnoreRetry=重试(&T)
AbortRetryIgnoreIgnore=忽略错误并继续(&I)
AbortRetryIgnoreCancel=取消安装

StatusClosingApplications=正在关闭应用程序...
StatusCreateDirs=正在创建目录...
StatusExtractFiles=正在解压缩文件...
StatusCreateIcons=正在创建快捷方式...
StatusCreateIniEntries=正在创建 INI 条目...
StatusCreateRegistryEntries=正在创建注册表条目...
StatusRegisterFiles=正在注册文件...
StatusSavingUninstall=正在保存卸载信息...
StatusRunProgram=正在完成安装...
StatusRestartingApplications=正在重新启动应用程序...
StatusRollback=正在回滚更改...

ErrorInternal2=内部错误：%1
ErrorFunctionFailedNoCode=%1 失败
ErrorFunctionFailed=%1 失败；代码 %2
ErrorFunctionFailedWithMessage=%1 失败；代码 %2。%n%3
ErrorExecutingProgram=无法执行文件：%n%1

ErrorRegOpenKey=打开注册表项时出错：%n%1\%2
ErrorRegCreateKey=创建注册表项时出错：%n%1\%2
ErrorRegWriteKey=写入注册表项时出错：%n%1\%2

ErrorIniEntry=在文件"%1"中创建 INI 条目时出错。

FileAbortRetryIgnoreSkipNotRecommended=跳过此文件（不推荐）(&S)
FileAbortRetryIgnoreIgnoreNotRecommended=忽略错误并继续（不推荐）(&I)
SourceIsCorrupted=源文件已损坏
SourceDoesntExist=源文件"%1"不存在
ExistingFileReadOnly2=无法替换现有文件，因为它被标记为只读。
ExistingFileReadOnlyRetry=移除只读属性并重试(&R)
ExistingFileReadOnlyKeepExisting=保留现有文件(&K)
ErrorReadingExistingDest=尝试读取现有文件时出错：
FileExistsSelectAction=选择操作
FileExists2=文件已存在。
FileExistsOverwriteExisting=覆盖现有文件(&O)
FileExistsKeepExisting=保留现有文件(&K)
FileExistsOverwriteOrKeepAll=对所有冲突执行此操作(&D)
ExistingFileNewerSelectAction=选择操作
ExistingFileNewer2=现有文件比安装程序尝试安装的文件更新。
ExistingFileNewerOverwriteExisting=覆盖现有文件(&O)
ExistingFileNewerKeepExisting=保留现有文件（推荐）(&K)
ExistingFileNewerOverwriteOrKeepAll=对所有冲突执行此操作(&D)
ErrorChangingAttr=尝试更改现有文件的属性时出错：
ErrorCreatingTemp=尝试在目标目录中创建文件时出错：
ErrorReadingSource=尝试读取源文件时出错：
ErrorCopying=尝试复制文件时出错：
ErrorReplacingExistingFile=尝试替换现有文件时出错：
ErrorRestartReplace=RestartReplace 失败：
ErrorRenamingTemp=尝试重命名目标目录中的文件时出错：
ErrorRegisterServer=无法注册 DLL/OCX：%1
ErrorRegSvr32Failed=RegSvr32 失败，退出代码 %1
ErrorRegisterTypeLib=无法注册类型库：%1

ErrorOpeningReadme=尝试打开自述文件时出错。
ErrorRestartingComputer=安装程序无法重新启动计算机。请手动执行此操作。

UninstallNotFound=文件"%1"不存在。无法卸载。
UninstallOpenError=无法打开文件"%1"。无法卸载
UninstallUnsupportedVer=此版本的卸载程序无法识别卸载日志文件"%1"的格式。无法卸载
UninstallUnknownEntry=卸载日志中遇到未知条目 (%1)
ConfirmUninstall=您确定要完全移除 %1 及其所有组件吗？
UninstallOnlyOnWin64=此安装只能在 64 位 Windows 上卸载。
OnlyAdminCanUninstall=此安装只能由具有管理权限的用户卸载。
UninstallStatusLabel=正在从您的计算机中移除 %1，请稍候。
UninstalledAll=%1 已成功从您的计算机中移除。
UninstalledMost=%1 卸载完成。%n%n某些元素无法移除。可以手动移除它们。
UninstalledAndNeedsRestart=要完成 %1 的卸载，必须重新启动您的计算机。%n%n您想要现在重新启动吗？
UninstallDataCorrupted="%1"文件已损坏。无法卸载

ConfirmDeleteSharedFileTitle=移除共享文件？
ConfirmDeleteSharedFile2=系统表明以下共享文件不再被任何程序使用。您想要卸载程序移除此共享文件吗？%n%n如果有任何程序仍在使用此文件而它被移除，那些程序可能无法正常运行。如果您不确定，请选择"否"。将文件保留在系统中不会造成任何危害。
SharedFileNameLabel=文件名：
SharedFileLocationLabel=位置：
WizardUninstalling=卸载状态
StatusUninstalling=正在卸载 %1...

ShutdownBlockReasonInstallingApp=正在安装 %1。
ShutdownBlockReasonUninstallingApp=正在卸载 %1。

[CustomMessages]
NameAndVersion=%1 版本 %2
AdditionalIcons=附加快捷方式:
CreateDesktopIcon=创建桌面快捷方式(&D)
CreateQuickLaunchIcon=创建快速启动栏快捷方式(&Q)
ProgramOnTheWeb=%1 网站
UninstallProgram=卸载 %1
LaunchProgram=运行 %1
AssocFileExtension=将 %1 与 %2 文件扩展名关联(&A)
AssocingFileExtension=正在将 %1 与 %2 文件扩展名关联...
AutoStartProgramGroupDescription=启动:
AutoStartProgram=自动启动 %1
AddonHostProgramNotFound=在您选择的文件夹中找不到 %1。%n%n您仍然要继续吗？
