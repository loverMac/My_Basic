10 CLASS Animal
20   METHOD init(name)
30     LET this.name = name
40   END METHOD
50   
60   METHOD speak()
70     PRINT this.name; " says hello"
80   END METHOD
90 END CLASS
100
110 CLASS Dog EXTENDS Animal
120   METHOD speak()
130     PRINT this.name; " says woof!"
140   END METHOD
150   
160   METHOD wag_tail()
170     PRINT this.name; " is wagging tail"
180   END METHOD
190 END CLASS
200
210 LET a = NEW Animal("Generic")
220
230 LET d = NEW Dog("Rex")