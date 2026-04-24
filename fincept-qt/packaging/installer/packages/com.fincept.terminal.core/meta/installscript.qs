// installscript.qs -- Fincept Terminal QtIFW component script
// Handles: shortcuts on install, user data cleanup on uninstall
//
// Data locations cleaned on uninstall (when user confirms):
//   Windows:  %LOCALAPPDATA%\com.fincept.terminal\
//   macOS:    ~/Library/Application Support/com.fincept.terminal/
//   Linux:    ~/.local/share/com.fincept.terminal/
//   QSettings (registry/plist/conf), credentials, temp files

function Component()
{
    try {
        console.log("[Fincept] Component() constructor — isInstaller=" +
                    installer.isInstaller() +
                    " isUninstaller=" + installer.isUninstaller() +
                    " isUpdater=" + installer.isUpdater() +
                    " isPackageManager=" + installer.isPackageManager());

        // Pre-register the auto-answer for the data-cleanup confirmation
        // dialog. Without this, headless invocations (`purge --default-answer`)
        // deadlock on QMessageBox.question() in onUninstallationStarted —
        // --default-answer only handles IFW's *own* dialogs, not script-
        // spawned ones. This is what was causing the bug reported in #240
        // where `purge` exited 1 with no cleanup.
        // ID must match the first arg of QMessageBox.question() below.
        if (typeof QMessageBox !== "undefined" && installer.setMessageBoxAutomaticAnswer) {
            installer.setMessageBoxAutomaticAnswer(
                "fincept.uninstall.data", QMessageBox.No);
        }

        // Connect signals using the 1-arg form. The 2-arg form (thisObj, fn) is
        // not reliably supported by the QJSEngine that backs QtIFW component
        // scripts — connections silently no-op on some versions.
        if (installer.isInstaller()) {
            installer.installationFinished.connect(onInstallationFinished);
        }

        if (installer.isUninstaller()) {
            installer.uninstallationStarted.connect(onUninstallationStarted);
            installer.uninstallationFinished.connect(onUninstallationFinished);
        }
    } catch (e) {
        // Never throw out of Component() — IFW treats that as a fatal load
        // error and aborts before any UI shows (the "GUI flashes and closes"
        // symptom in #240). Log and continue with defaults.
        console.log("[Fincept] Component() constructor error: " + e);    }
}

// ---------------------------------------------------------------------------
// Install: create platform shortcuts
// ---------------------------------------------------------------------------

Component.prototype.createOperations = function()
{
    component.createOperations();

    var targetDir = installer.value("TargetDir");

    if (systemInfo.kernelType === "winnt") {
        // Start Menu shortcut
        component.addOperation("CreateShortcut",
            targetDir + "/FinceptTerminal.exe",
            "@StartMenuDir@/Fincept Terminal.lnk",
            "workingDirectory=" + targetDir,
            "iconPath=" + targetDir + "/FinceptTerminal.exe",
            "iconId=0",
            "description=Professional Financial Intelligence Terminal");

        // Desktop shortcut
        component.addOperation("CreateShortcut",
            targetDir + "/FinceptTerminal.exe",
            "@DesktopDir@/Fincept Terminal.lnk",
            "workingDirectory=" + targetDir,
            "iconPath=" + targetDir + "/FinceptTerminal.exe",
            "iconId=0",
            "description=Professional Financial Intelligence Terminal");
    }

    if (systemInfo.kernelType === "linux") {
        component.addOperation("CreateDesktopEntry",
            "@HomeDir@/.local/share/applications/fincept-terminal.desktop",
            "Version=1.0\n" +
            "Type=Application\n" +
            "Name=Fincept Terminal\n" +
            "GenericName=Financial Intelligence Terminal\n" +
            "Comment=Professional financial data terminal with AI analytics\n" +
            "Exec=" + targetDir + "/bin/FinceptTerminal %U\n" +
            "Icon=" + targetDir + "/share/icons/hicolor/256x256/apps/fincept-terminal.png\n" +
            "Terminal=false\n" +
            "StartupWMClass=FinceptTerminal\n" +
            "StartupNotify=true\n" +
            "Categories=Finance;Office;Science;\n" +
            "Keywords=finance;trading;stocks;crypto;portfolio;AI;analytics;markets;\n"
        );
    }

    // macOS: .app bundle is self-contained, no shortcuts needed
};

Component.prototype.installationFinished = function()
{
    // Reserved for future post-install actions (URL handlers, file associations)
};

// ---------------------------------------------------------------------------
// Uninstall: prompt for user data removal, then clean up
// ---------------------------------------------------------------------------

Component.prototype.uninstallationStarted = function()
{
    try {
        console.log("[Fincept] uninstallationStarted.");

        // Per-machine install at C:\Program Files\... requires elevation to
        // delete files. Without this, the cmd.exe / reg.exe calls below
        // silently fail and IFW's own RemoveTargetDir step hits ACCESS_DENIED.
        // gainAdminRights() is a no-op if we're already elevated, and on
        // non-Windows it just returns. Failure here is non-fatal — log and
        // continue; some Windows configurations let `cmd /c rmdir` work
        // unelevated for user-owned trees.
        if (systemInfo.kernelType === "winnt") {
            try {
                installer.gainAdminRights();
            } catch (e) {
                console.log("[Fincept] gainAdminRights failed (continuing): " + e);
            }
        }

        // Headless invocations (`purge --default-answer`, `--accept-messages`)
        // skip script-spawned QMessageBox confirmation entirely. The auto-
        // answer registered in Component() handles IFW's accounting; we just
        // need to not block here.
        var headless =
            (typeof installer.isCommandLineInstance === "function" &&
                installer.isCommandLineInstance()) ||
            (typeof gui === "undefined" || gui === null);

        var clean = false;
        if (headless) {
            console.log("[Fincept] Headless uninstall — skipping data-cleanup prompt.");
        } else {
            var answer = QMessageBox.question(
                "fincept.uninstall.data",
                "Remove Fincept Terminal User Data?",
                "Do you want to remove all Fincept Terminal user data?\n\n" +
                "This includes:\n" +
                "  - Databases (chat history, portfolio, watchlists)\n" +
                "  - Log files\n" +
                "  - Downloaded files and cached data\n" +
                "  - ML models (Whisper, etc.)\n" +
                "  - Python runtime and virtual environments\n" +
                "  - Workspaces and profiles\n" +
                "  - Saved credentials and API keys\n" +
                "  - Application settings\n\n" +
                "Choose 'No' to keep your data for a future reinstall.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            );
            clean = (answer === QMessageBox.Yes);
        }

        if (clean) {
            console.log("[Fincept] Cleaning user data.");
            try {
                cleanUserData();
            } catch (e) {
                console.log("[Fincept] cleanUserData threw: " + e);
            }
        } else {
            console.log("[Fincept] Keeping user data.");
        }
    } catch (e) {
        // Never propagate — IFW treats a thrown signal handler as a fatal
        // uninstall error and exits 1 with no cleanup, which is exactly the
        // symptom from #240.
        console.log("[Fincept] onUninstallationStarted error: " + e);    }
};

// ---------------------------------------------------------------------------
// Data cleanup implementation
// ---------------------------------------------------------------------------

function cleanUserData()
{
    // 1. Remove main data directory
    removeDataRoot();

    // 2. Remove legacy data directories (Windows only)
    removeLegacyDirs();

    // 3. Remove QSettings (registry / plist / conf)
    removeSettings();

    // 4. Remove credentials from OS secure storage
    removeCredentials();

    // 5. Clean temp files
    removeTempFiles();
}

// -- 1. Main data root --

function removeDataRoot()
{
    var dataRoot = "";

    if (systemInfo.kernelType === "winnt") {
        dataRoot = installer.environmentVariable("LOCALAPPDATA") +
                   "/com.fincept.terminal";
    } else if (systemInfo.kernelType === "darwin") {
        dataRoot = installer.environmentVariable("HOME") +
                   "/Library/Application Support/com.fincept.terminal";
    } else {
        dataRoot = installer.environmentVariable("HOME") +
                   "/.local/share/com.fincept.terminal";
    }

    if (installer.fileExists(dataRoot)) {
        removeDirectoryRecursive(dataRoot);
    }
}

// -- 2. Legacy directories (pre-v4 Windows paths) --

function removeLegacyDirs()
{
    if (systemInfo.kernelType !== "winnt") return;

    var localAppData = installer.environmentVariable("LOCALAPPDATA");

    var legacy1 = localAppData + "/Fincept/FinceptTerminal";
    if (installer.fileExists(legacy1)) {
        removeDirectoryRecursive(legacy1);
    }

    var legacy2 = localAppData + "/FinceptTerminal";
    if (installer.fileExists(legacy2)) {
        removeDirectoryRecursive(legacy2);
    }

    // Remove empty parent directory
    var finceptParent = localAppData + "/Fincept";
    if (installer.fileExists(finceptParent)) {
        installer.execute("cmd", ["/c", "rmdir", finceptParent.replace(/\//g, "\\")]);
    }
}

// -- 3. QSettings --

    // 5. Windows Credential Manager entries: FinceptTerminal/*
    //    cmdkey has no wildcard delete. Enumerate via a cmd.exe FOR loop —
    //    we used PowerShell originally but #240 confirmed the maintenance
    //    tool fails on locked-down Win11 boxes where AppLocker/Defender
    //    blocks installer-spawned powershell.exe. cmd.exe has no such
    //    restrictions. The FOR /F parses `cmdkey /list` lines that match
    //    "Target: FinceptTerminal/..." and deletes each.
    runAndLog("cmd.exe", ["/c",
        "for /f \"tokens=1,* delims=:\" %a in ('cmdkey /list 2^>nul ^| findstr /i \"FinceptTerminal/\"') do " +
        "(for /f \"tokens=*\" %c in (\"%b\") do cmdkey /delete:\"%c\" >nul 2>&1) & exit /b 0"
    ]);
    } else if (systemInfo.kernelType === "darwin") {
        var plistPath = installer.environmentVariable("HOME") +
            "/Library/Preferences/com.fincept.FinceptTerminal.plist";
        if (installer.fileExists(plistPath)) {
            installer.execute("rm", ["-f", plistPath]);
        }

    // 7. Screenshots saved under %USERPROFILE% by MainWindow "save screenshot"
    //    with the strict pattern fincept_YYYYMMDD_HHMMSS.png. cmd.exe's `del`
    //    wildcards aren't strict enough on their own ("fincept_*.png" would
    //    nuke any user file matching), so we narrow with a FOR loop that
    //    checks the digit-shape via findstr.
    var userProfile = installer.environmentVariable("USERPROFILE");
    if (userProfile) {
        var up = toWin(userProfile);
        runAndLog("cmd.exe", ["/c",
            "for /f \"delims=\" %f in ('dir /b /a-d \"" + up + "\\fincept_*.png\" 2^>nul ^| " +
            "findstr /r \"^fincept_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]\\.png$\"') do " +
            "del /q /f \"" + up + "\\%f\" 2>nul & exit /b 0"        ]);
    }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function removeDirectoryRecursive(path)
{
    if (systemInfo.kernelType === "winnt") {
        installer.execute("cmd", ["/c", "rmdir", "/s", "/q",
            path.replace(/\//g, "\\")]);
    } else {
        installer.execute("/bin/rm", ["-rf", path]);
    }
}
