import openai
import os

openai.api_key = os.environ['GPT_API_KEY']



from flask import jsonify

from flask import Flask, request, render_template


app = Flask(__name__)


default_message = "与えられた問いに対して、「賛成,反対,条件付き賛成,条件付き反対」の中から意見を必ず最初に述べ、その後にその理由を教えてください。また、もし「賛成」や「反対」ではなく、「条件付き賛成」又は「条件付き反対」最初にを選んだ際は、その条件を箇条書きで最後に述べてください。また、「理由:」や「条件:」と述べるときは、必ず改行してください。"


def get_overall_decision(opinions):
    pro_count = 0
    con_count = 0
    
    for opinion in opinions:
        if '賛成' in opinion:
            pro_count += 1
        elif '反対' in opinion:
            con_count += 1
    
    if pro_count == len(opinions):
        return '賛成'
    elif con_count == len(opinions):
        return '反対'
    else:
        return None

def make_response(input_role,input_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.0,
        messages=[
            {"role": "system", "content": input_role},
            {"role": "user", "content": input_message},
        ]
    )
    return response

def get_final_decision(opinion):
    pro_count = 0
    con_count = 0
    
    if '賛成' in opinion:
        pro_count += 1
    elif '反対' in opinion:
        con_count += 1
    
    if pro_count > con_count:
        return '賛成'
    else:
        return '反対'

def get_decision(opinion):
    if '条件付き賛成' in opinion:
        return "<p style='text-align: center;'><span style='color: green; font-weight: 900; font-size: 5rem; text-align:center'>【条件付き承認】<br></span>" + \
                      "<span style='color: orange; font-weight: 900; font-size: 2rem;'>""</span></p>"
    elif '条件付き反対' in opinion:
        return "<p style='text-align: center;'><span style='color: red; font-weight: 900; font-size: 5rem; text-align:center'>【条件付き否定】<br></span>" + \
                      "<span style='color: orange; font-weight: 900; font-size: 2rem;'>""</span></p>"
    elif '反対' in opinion:
        return "<p style='text-align: center;'><span style='color: red; font-weight: 900; font-size: 5rem;'>【否定】<br></span>"+ \
                      "<span style='color: orange; font-weight: 900; font-size: 2rem;'>""</span></p>"
    elif '賛成' in opinion:
        return "<p style='text-align: center;'><span style='color: green; font-weight: 900; font-size: 5rem; text-align:center'>【承認】<br></span>" + \
                      "<span style='color: orange; font-weight: 900; font-size: 2rem;'>""</span></p>"
    else:
        return '回答不能'
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_opinions', methods=['POST'])
def get_opinions():
    
    prompt = request.form.get('prompt', '')
    opinions = []

    # 科学者としての意見
    scientist_opinion = make_response("あなたは科学者です。一人の科学者として、科学的知見から、"+default_message,prompt)['choices'][0]['message']['content']
    scientist_opinion = get_decision(scientist_opinion) +"\n"+ scientist_opinion 

    opinions.append(scientist_opinion)

    # 女性としての意見
    woman_opinion = make_response("あなたは子供を持たない女性です。一人の女性としての立場から、"+default_message,prompt)['choices'][0]['message']['content']
    woman_opinion = get_decision(woman_opinion) +"\n"+ woman_opinion
        

    opinions.append(woman_opinion)

    # 母親としての意見
    mother_opinion = make_response("あなたは子供を持つ母親です。一人の母親としての立場から、"+default_message,prompt)['choices'][0]['message']['content']
    mother_opinion = get_decision(mother_opinion) +"\n"+ mother_opinion

    opinions.append(mother_opinion)

    result = get_final_decision(opinions)

    return jsonify(opinions)

if __name__ == '__main__':
    app.run()