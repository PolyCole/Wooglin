<img src="https://pbs.twimg.com/profile_images/1040408608067018752/yFS8LZve_400x400.jpg" alt="Wooglin logo" width="200" height="200"></img>
# Wooglin
***
Table of contents

* [Introduction](#Introduction)
* [Documentation](#Documentation)
* [Technicals](#Technicals)
***
### Introduction
Hello there and welcome to Wooglin. Wooglin is a slack bot used in the executive board workspace of my fraternity. Wooglin helps to manage mass communication through SMS, Chapter attendance and standing tracking, and specified SMS communications as necessary.

***
### Documentation
The following outlines the go-to phrasing that the bot has been trained on excessively. Using this phrasing increases the probability that the bot understands what you want.

| Goal          | Phrasing           |
| :------------ | ------------- |
| Sending a text to someone     | Send a text to [person] saying "[message]" |
| Getting stored info on someone     | Wooglin, please get all information on [person].      |
| Getting unexcused absences | Wooglin, how many times has [person] been unexcused from chapter?      |
| Getting excused absences | Wooglin, how many times has [person] been excused from chapter? |
| Getting excuses for missing chapter | Wooglin, what have been [person]'s excuses for missing chapter? |
| Getting phone number | Wooglin, what is [name]'s phone number? |
| Getting roll number | Wooglin, what is [name]'s roll number? |
| Getting sober bros | Wooglin, who are the sober bros on [date] | 
| Adding someone as a sober bro | Wooglin, [name] is a sober bro on [date] | 
| Removing someone as a sober bro | Wooglin, [name] is not a sober bro on [date] |

***
### Technicals
Wooglin physically is a series of python scripts being hosted by AWS lambda. The bot uses AWS DynamoDB for storage. To send text messages, Wooglin uses the Twilio SMS API. For general Natural Language Processing, Wooglin uses Wit.ai's NLP engine. 
