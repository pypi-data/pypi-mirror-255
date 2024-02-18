installed.packages(c("tm","stringr"))
library(tm)
library(stringr)
personal_emails <- c("Hello friend this is a personal email.",
                     "Claim your prize now!you've won $1,000,000!",
                     "Meeting tomorrow at 2PM in the office")
classify_email <- function(email){
  email <- tolower(email)
  if(str_detect(email,"won\\s*\\$\\d+")||
     str_detect(email,"claim")){
    return("spam")
  }
  else{
    return("personal")
  }
}
classified_emails <- sapply(personal_emails,classify_email)
print(classified_emails)