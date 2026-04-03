import sys
import os

labelCount = 0
returnCount = 0
curFile = ""
curFunction = ""


def funcLabel(label):
    if curFunction:
        return curFunction +"$"+ label
    else :
        return label

# push D onto stack 
def pushD(asm):
    asm.append("@SP")
    asm.append("A=M")
    asm.append("M=D")
    # move pointer
    asm.append("@SP")
    asm.append("M=M+1")

# pop stack into D
def popD(asm):
    asm.append("@SP")
    asm.append("AM=M-1")
    asm.append("D=M")

# eq gt lt comparison  
def comp(cmd, asm):
    global labelCount
    t = "T" + str(labelCount)
    e = "E"+ str(labelCount)
    labelCount += 1
    if cmd == "eq":
        j = "JEQ"
    elif cmd == "gt":
        j = "JGT"
    elif cmd == "lt":
        j = "JLT"

    #subtract
    asm.append("@SP")
    asm.append("AM=M-1")
    asm.append("D=M")
    asm.append("A=A-1")
    asm.append("D=M-D")
    #if true jump
    asm.append("@" + t)
    asm.append("D;"+j)
    # false 
    asm.append("@SP")
    asm.append("A=M-1")
    asm.append("M=0")
    asm.append("@" + e)
    asm.append("0;JMP")
    #true 
    asm.append("("+ t +")")
    asm.append("@SP")
    asm.append("A=M-1")
    asm.append("M=-1")
    #end
    asm.append("("+ e +")")

# call a function
def callFunc(name, n, asm):
    global returnCount
    ret = name + "$ret"+ str(returnCount)
    returnCount = returnCount + 1

    # return address
    asm.append("@"+ret)
    asm.append("D=A")
    pushD(asm)

    # save segments
    asm.append("@LCL")
    asm.append("D=M")
    pushD(asm)
    asm.append("@ARG")
    asm.append("D=M")
    pushD(asm)
    asm.append("@THIS")
    asm.append("D=M")
    pushD(asm)
    asm.append("@THAT")
    asm.append("D=M")
    pushD(asm)    
    #arguments
    asm.append("@SP")
    asm.append("D=M")
    asm.append("@" + str(n+5))
    asm.append("D=D-A")
    asm.append("@ARG")
    asm.append("M=D")
    #local vars
    asm.append("@SP")
    asm.append("D=M")
    asm.append("@LCL")
    asm.append("M=D")
    #jump + return label
    asm.append("@" + name)
    asm.append("0;JMP")
    asm.append("("+ ret +")")

#return from function
def retFunc(asm):
    #store lcl
    asm.append("@LCL")
    asm.append("D=M")
    asm.append("@R13")
    asm.append("M=D")
    asm.append("@5")
    asm.append("A=D-A")
    asm.append("D=M")
    asm.append("@R14")
    asm.append("M=D")
    popD(asm)
    asm.append("@ARG")
    asm.append("A=M")
    asm.append("M=D")
    asm.append("@ARG")
    asm.append("D=M+1")
    asm.append("@SP")
    asm.append("M=D")
    #fix THAT
    asm.append("@R13")
    asm.append("D=M")
    asm.append("@1")
    asm.append("A=D-A")
    asm.append("D=M")
    asm.append("@THAT")
    asm.append("M=D")
    #THIS
    asm.append("@R13")
    asm.append("D=M")
    asm.append("@2")
    asm.append("A=D-A")
    asm.append("D=M")
    asm.append("@THIS")
    asm.append("M=D")
    #ARG
    asm.append("@R13")
    asm.append("D=M")
    asm.append("@3")
    asm.append("A=D-A")
    asm.append("D=M")
    asm.append("@ARG")
    asm.append("M=D")
    #LCL
    asm.append("@R13")
    asm.append("D=M")
    asm.append("@4")
    asm.append("A=D-A")
    asm.append("D=M")
    asm.append("@LCL")
    asm.append("M=D")
    #jump back
    asm.append("@R14")
    asm.append("A=M")
    asm.append("0;JMP")

#bread and butter 
def translate(lines, asm):
    global curFunction
    for line in lines:
        line = line.split("//")[0].strip()
        if len(line) > 0:
            p = line.split()
            cmd = p[0]
            seg = ""
            i = 0
            if len(p) > 1:
                seg = p[1]
            if len(p) > 2:
                i = int(p[2])
 
            if cmd == "push":
                if seg == "constant":
                    asm.append("@" + p[2])
                    asm.append("D=A")
                elif seg == "local":
                    asm.append("@LCL")
                    asm.append("D=M")
                    asm.append("@" +str(i))
                    asm.append("A=D+A")
                    asm.append("D=M")
                elif seg == "argument":
                    asm.append("@ARG")
                    asm.append("D=M")
                    asm.append("@" +str(i))
                    asm.append("A=D+A")
                    asm.append("D=M")
                elif seg == "this":
                    asm.append("@THIS")
                    asm.append("D=M")
                    asm.append("@" +str(i))
                    asm.append("A=D+A")
                    asm.append("D=M")
                elif seg == "that":
                    asm.append("@THAT")
                    asm.append("D=M")
                    asm.append("@" +str(i))
                    asm.append("A=D+A")
                    asm.append("D=M")
                elif seg == "temp":
                    asm.append("@" +str(5 + i))
                    asm.append("D=M")
                elif seg == "pointer":
                    if i == 0:
                        asm.append("@THIS")
                    else:
                        asm.append("@THAT")
                    asm.append("D=M")
                elif seg == "static":
                    asm.append("@" + curFile + "." + str(i))
                    asm.append("D=M")
                pushD(asm)

            elif cmd == "pop":
                if seg == "local":
                    asm.append("@LCL")
                    asm.append("D=M")
                    asm.append("@" +str(i))
                    asm.append("D=D+A")
                    asm.append("@R13")
                    asm.append("M=D")
                    popD(asm)
                    asm.append("@R13")
                    asm.append("A=M")
                    asm.append("M=D")
                elif seg == "argument":
                    asm.append("@ARG")
                    asm.append("D=M")
                    asm.append("@" +str(i))
                    asm.append("D=D+A")
                    asm.append("@R13")
                    asm.append("M=D")
                    popD(asm)
                    asm.append("@R13")
                    asm.append("A=M")
                    asm.append("M=D")
                elif seg == "this":
                    asm.append("@THIS")
                    asm.append("D=M")
                    asm.append("@" +str(i))
                    asm.append("D=D+A")
                    asm.append("@R13")
                    asm.append("M=D")
                    popD(asm)
                    asm.append("@R13")
                    asm.append("A=M")
                    asm.append("M=D")
                elif seg == "that":
                    asm.append("@THAT")
                    asm.append("D=M")
                    asm.append("@" +str(i))
                    asm.append("D=D+A")
                    asm.append("@R13")
                    asm.append("M=D")
                    popD(asm)
                    asm.append("@R13")
                    asm.append("A=M")
                    asm.append("M=D")
                elif seg == "temp":
                    popD(asm)
                    asm.append("@" +str(5 + i))
                    asm.append("M=D")
                elif seg == "pointer":
                    popD(asm)
                    if i == 0:
                        asm.append("@THIS")
                    else:
                        asm.append("@THAT")
                    asm.append("M=D")
                elif seg == "static":
                    popD(asm)
                    asm.append("@" + curFile + "." + str(i))
                    asm.append("M=D")

            elif cmd in ("add", "sub", "and", "or"):
                op = {"add": "M=D+M", "sub": "M=M-D", "and": "M=D&M", "or": "M=D|M"}[cmd]
                asm.append("@SP")
                asm.append("AM=M-1")
                asm.append("D=M")
                asm.append("A=A-1")
                asm.append(op)

            elif cmd in ("neg", "not"):
                asm.append("@SP")
                asm.append("A=M-1")
                if cmd == "neg":
                    asm.append("M=-M")
                else:
                    asm.append("M=!M")
                

            elif cmd in ("eq", "gt", "lt"):
                comp(cmd, asm)

            elif cmd == "label":
                asm.append("(" + funcLabel(seg) + ")")
            elif cmd == "goto":
                asm.append("@" + funcLabel(seg))
                asm.append("0;JMP")
            elif cmd == "if-goto":
                popD(asm)
                asm.append("@" + funcLabel(seg))
                asm.append("D;JNE")

            elif cmd == "function":
                curFunction = seg
                asm.append("(" + seg + ")")
                for _ in range(i):
                    asm.append("@0")
                    asm.append("D=A")
                    pushD(asm)
 
            elif cmd == "call":
                callFunc(seg, i, asm)
            elif cmd == "return":
                retFunc(asm)

if __name__ == "__main__": 
    path = sys.argv[1]
    out = []
 
    if os.path.isdir(path):
        folderName = os.path.basename(path)
        oFile = os.path.join(path, folderName + ".asm")

        out.append("@256")
        out.append("D=A")
        out.append("@SP")
        out.append("M=D")
        callFunc("Sys.init", 0, out)
 
        for fileName in sorted(os.listdir(path)):
            if fileName.endswith(".vm"):
                curFile = fileName.replace(".vm", "")
                full_path = os.path.join(path, fileName)
                translate(open(full_path).readlines(), out)
    else:
        oFile = path.replace(".vm", ".asm")
        curFile = os.path.splitext(os.path.basename(path))[0]
        translate(open(path).readlines(), out)
 
    open(oFile, "w").write("\n".join(out))
#torture done