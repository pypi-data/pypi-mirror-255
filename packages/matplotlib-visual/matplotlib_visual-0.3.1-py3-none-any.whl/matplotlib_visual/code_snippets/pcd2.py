#include<stdio.h>
#include<string.h>
#include<ctype.h>

void identifyToken(char *token){
    int i;
    int hasAlpha = 0;
    int hasDigit = 0;

    char a[][10]={"if","else","while","do","for","int","void","float","char","return","break","enum","switch","case","struct"};

    for(i=0;i<sizeof(a)/sizeof(a[0]);i++){
        if(strcmp(token,a[i])==0){
            printf("Keywords : %s\n",token);
            return;
        }
    }

    for(i = 0; token[i] != '\0'; i++) {
        if(isalpha(token[i])) {
            hasAlpha = 1;
        } else if(isdigit(token[i])) {
            hasDigit = 1;
        }
    }

    if(hasAlpha && hasDigit) {
        printf("Invalid character : %s\n", token);
        return;
    }

    if(isdigit(token[0]) || (token[0]=='-' && isdigit(token[1]))){
        printf("Constants : %s\n",token);
        return;
    }

    if(isalpha(token[0]) || token[0]=='_'){
        printf("Identifier : %s\n",token);
        return;
    }

    if(strchr("+-*/=",token[0]) !=NULL){
        printf("Operator : %s\n",token);
        return;
    }

    printf("Special Character : %s\n",token);
}

void displayToken(char *paragraph){
    int j=0;
    char *token=strtok(paragraph,"\t \n");
    while(token!=NULL){
        identifyToken(token);
        token=strtok(NULL,"\t \n");
        j++;
    }
    printf("\nNumber of tokens : %d",j);
}

int main(){
    char paragraph[1000];
    printf("Enter the paragraph: ");
    fgets(paragraph,sizeof(paragraph),stdin);
    printf("\nToken with types: \n");
    displayToken(paragraph);
    return 0;
}