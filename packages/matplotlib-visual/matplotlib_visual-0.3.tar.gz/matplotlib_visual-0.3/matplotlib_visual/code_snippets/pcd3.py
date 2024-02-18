#include <stdio.h>
#include <stdlib.h>
char l;
void match (char c) {
	if (l ==c)
		l= getchar();
	else {
		printf ("gnvalid Input");
		exit (0);
	}
}

void B() {
	if(l=='b'){
		match ('b'); 
	}
	else{
		printf ("Invalid Input \n");
		exit(0); 
	}
}

void A(){ 
	if (l=='a'){
		match('a');
		B();
	}
	else
		return;
}

void s(){
	A();
	A();
}

int main() {
	char input [10];
	printf ("Enter string with $ at the end \n");
	l= getchar();
	s();
	if(l== '$'){
		printf ("\n Parsing successful \n"); }
	else 
		printf ("Invalid Input");
}