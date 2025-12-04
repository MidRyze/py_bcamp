score = 0
ques_num = 0
questions = {
     "3 + 2 =":5,
     "5 - 3 =":2,
     "1 + 12 =":13,
     "32 / 4 =":8,
     "10 * 2 =":20,
     "1 / 0 =":0,
     "24 % 5 =":4,
     "0 / 9 =":0,
     "4 - 16 =":-12,
     "23 * 0 =":30 \
     }
# print(questions)

while ques_num <= len(questions)-1:
     q1 = input(list(questions.keys())[ques_num])
     if q1 == "": # if user enters nothing, skip question
          ques_num += 1
          continue
     if list(questions.keys())[ques_num][0:3] == "0 /": # special case for 0 divided by a number
          q1.lower() == "null" or q1.lower() == "undefined" or q1.lower() == "infinity"
          score += 1
          continue
     try:
          q1 = int(q1) # convert input to integer
          if q1 == list(questions.values())[ques_num]:
               score += 1
     except:
          print("Please enter a valid number.") # if user enters invalid input
          pass
     ques_num += 1

score_perct = int(score/ques_num * 100)
if score_perct == 100:
     text = "Excellent work!"
elif score_perct >= 75:
     text = "Good job!"
elif score_perct >= 50:
     text = "Passed."
else:
     text = "Keep trying."

print(f"Your score is: {score_perct}%\n{text}")