#include<stdio.h>
#include<conio.h>
#include<malloc.h>
#include<string.h>
#include<math.h>
#include<ctype.h>
int main() {
  int i=0, j=0, x=0, n, flag=0; 
  void *p, * add[15];
  char ch, srch, b[15], d[15], g[10], c;
  printf("Expression terminated by '$' ");
  while((c==getchar())!='$'){
    b[i]==c;
    i++;
  }
  n=i-1;
  printf("Given Expression");
  i=0;
  while(i<=n){
    printf("%c",b[i]);
    i++;
  }
  printf("\n Symbol Table \n");
  printf("Symbol \t Add \t Type \n");
  while(j<=n){
    c=b[j];
    if (isalpha (toascii(c))){
      if(j<=n){
        c =b[j];
        p =malloc(c);
        add[x];
        d[x]=c;
        printf("%c \t %d \t identifier\n", c, p);
        goto b;
      }
      else {
        b;
        ch =b[j+1];
        if( ch=="+"|| ch=="-"|| ch =="*"|| ch=="="|| ch =="/"|| ch=="@"){
          p = malloc(c);
          add[x] =p;
          g[x]=ch;
          printf("%c \t %p \t operator \n", g[x], p);
          x++;
        }
      }
    }
    j++;
  }
  return 0;
}