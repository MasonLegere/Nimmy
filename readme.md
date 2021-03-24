```
 _   _ _                           
| \ | (_)                                
|  \| |_ _ __ ___  _ __ ___  _   _ 
| . ` | | '_ ` _ \| '_ ` _ \| | | |
| |\  | | | | | | | | | | | | |_| |
\_| \_/_|_| |_| |_|_| |_| |_|\__, |
                              __/ |        
```

Nimmy is a simple command line interface for playing a modified version of the game Nim given an initial configuration
of the piles. This modified version of Nim is different from the traditional rules in the sense that there are three ways
of winning/losing - adding complexity to decision making. In particular, a player will lose the game if on the start
of their turn

- all piles are empty.
- 3 piles each with 2 objects, and all other piles are empty.
- 1 pile with 1 object, 1 pile with 2 objects, 1 pile with 3 objects, all other piles are empty.
- 2 piles with 1 object, 2 piles with 2 objects, all other piles empty. 


