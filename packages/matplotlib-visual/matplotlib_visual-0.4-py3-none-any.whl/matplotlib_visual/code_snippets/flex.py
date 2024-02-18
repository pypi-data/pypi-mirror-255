%{
#include <stdio.h>
int yywrap(void);
%}

%%

[ \t\n]          /* Ignore whitespace */
[0-9]+           { printf("NUMBER: %s\n", yytext); }
[a-zA-Z][a-zA-Z0-9]*   { printf("IDENTIFIER: %s\n", yytext); }
[-+*/=()<>;]      { printf("OPERATOR: %s\n", yytext); }
.                { printf("UNKNOWN CHARACTER: %s\n", yytext); }

%%

int yywrap(void) {
    return 1;  // Indicate no more input
}

int main(int argc, char** argv) {
    yyin = fopen(argv[1], "r");   // Open the input file
    yylex();                      // Call the lexer
    fclose(yyin);                 // Close the file

    return 0;
}