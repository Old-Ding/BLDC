param(
    [Parameter(Mandatory = $true)]
    [string]$TitlePattern,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

public static class PlecsWindowCapture
{
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint flags);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int command);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    public static IntPtr FindPlecsWindow(string titleNeedle)
    {
        IntPtr match = IntPtr.Zero;
        EnumWindows((hWnd, lParam) =>
        {
            if (!IsWindowVisible(hWnd)) return true;
            int length = GetWindowTextLength(hWnd);
            if (length == 0) return true;
            var title = new StringBuilder(length + 1);
            GetWindowText(hWnd, title, title.Capacity);
            if (title.ToString().IndexOf(titleNeedle, StringComparison.OrdinalIgnoreCase) < 0) return true;
            uint processId;
            GetWindowThreadProcessId(hWnd, out processId);
            try
            {
                if (!Process.GetProcessById((int)processId).ProcessName.Equals("PLECS", StringComparison.OrdinalIgnoreCase)) return true;
            }
            catch
            {
                return true;
            }
            match = hWnd;
            return false;
        }, IntPtr.Zero);
        return match;
    }
}
'@

$titleNeedle = $TitlePattern.Trim('*')
$windowHandle = [PlecsWindowCapture]::FindPlecsWindow($titleNeedle)
if ($windowHandle -eq [IntPtr]::Zero) {
    throw "No PLECS window matched '$TitlePattern'."
}

[void][PlecsWindowCapture]::ShowWindow($windowHandle, 3)
Start-Sleep -Milliseconds 500

$rect = New-Object PlecsWindowCapture+RECT
if (-not [PlecsWindowCapture]::GetWindowRect($windowHandle, [ref]$rect)) {
    throw "Failed to read the PLECS window rectangle."
}

$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top
if ($width -lt 200 -or $height -lt 200) {
    throw "Unexpected PLECS window size: ${width}x${height}."
}

$output = [System.IO.Path]::GetFullPath($OutputPath)
$directory = [System.IO.Path]::GetDirectoryName($output)
[System.IO.Directory]::CreateDirectory($directory) | Out-Null

$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$hdc = $graphics.GetHdc()
try {
    # PW_RENDERFULLCONTENT captures the Scope even when another window overlaps it.
    if (-not [PlecsWindowCapture]::PrintWindow($windowHandle, $hdc, 2)) {
        throw "PLECS PrintWindow failed."
    }
}
finally {
    $graphics.ReleaseHdc($hdc)
    $graphics.Dispose()
}

try {
    $bitmap.Save($output, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $bitmap.Dispose()
}

Write-Output "Captured PLECS window: $output (${width}x${height})"
