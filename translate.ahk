#Requires AutoHotkey v2.0
#SingleInstance Force
A_IconHidden := true

^+x::
{
    KeyWait("Shift")
    Sleep(10)
    Send("^c")
    if ClipWait(1)
        FileAppend("", A_Temp "\ClipTranslate.trigger")
}
