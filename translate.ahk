#Requires AutoHotkey v2.0
#SingleInstance Force
A_IconHidden := true

^+x::
{
    KeyWait("Shift")
    Sleep(10)
    Send("^c")
    if ClipWait(1)
    {
        doneFile := A_Temp "\ClipTranslate.done"
        if FileExist(doneFile)
            FileDelete(doneFile)
        FileAppend("", A_Temp "\ClipTranslate.trigger")
        Loop 50
        {
            Sleep(100)
            if FileExist(doneFile)
            {
                FileDelete(doneFile)
                Send("^v")
                break
            }
        }
    }
}
