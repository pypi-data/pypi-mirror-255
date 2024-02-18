import argparse
import os
from flask import Flask, render_template, request, make_response, redirect, url_for
from dotenv import load_dotenv

from panoramaTool import PostRulesManager
from panoramaTool.logic.business_logic import BusinessLogic
from panoramaTool.logic.csv_manager import CSVManager
from panoramaTool.panorama_api.api_call import APICall

load_dotenv()

app = Flask(__name__)
template_path = os.path.join(os.path.dirname(__file__), 'templates')
app.template_folder = template_path
app.static_folder = os.path.join(os.path.dirname(__file__), 'static')

@app.route('/', methods=['GET'])
def index():
    if BusinessLogic.check_for_valid_session(request):
        print("Valid Session")
        response = make_response(redirect(url_for('addresses')))
        return response
    response = make_response(redirect(url_for('login')))
    print("Not a valid session. Redirect to login!")
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    response = make_response(redirect(url_for('addresses')))
    if request.method == 'GET' and not BusinessLogic.check_for_valid_session(request):
        print("Not a valid session. Login.")
        response = render_template('login.html')
    elif request.method == 'POST':
        panorama_url = request.form['url']
        username = request.form['username']
        password = request.form['password']
        api_key = APICall.get_api_key(user=username, password=password, panorama_url=panorama_url)
        if api_key == "Invalid Credentials":
            response = make_response(redirect(url_for('index')))
            return response
        response.set_cookie('panorama_url', panorama_url)
        response.set_cookie('api_key', api_key)
    return response


@app.route('/addresses', methods=['GET', 'POST'])
def addresses():
    if request.method == 'GET' and BusinessLogic.check_for_valid_session(request):
        return make_response(render_template('addresses.html'))
    elif request.method == 'POST':
        save_path = CSVManager.save_csv(request.files['csv_file'])
        csv_data = CSVManager.read_csv(save_path)
        BusinessLogic.make_concurrent_calls(
            request=request,
            function=BusinessLogic.create_address,
            csv=csv_data
        )
        return make_response(redirect(url_for('addresses')))
    return make_response(redirect(url_for('index')))



@app.route('/services', methods=['GET', 'POST'])
def services():
    if request.method == 'GET' and BusinessLogic.check_for_valid_session(request):
        return make_response(render_template('services.html'))
    elif request.method == 'POST':
        save_path = CSVManager.save_csv(request.files['csv_file'])
        csv_data = CSVManager.read_csv(save_path)
        BusinessLogic.make_concurrent_calls(
            request=request,
            function=BusinessLogic.create_services,
            csv=csv_data
        )
        return make_response(redirect(url_for('services')))
    return make_response(redirect(url_for('index')))


@app.route('/address_groups', methods=['GET', 'POST'])
def address_groups():
    if request.method == 'GET' and BusinessLogic.check_for_valid_session(request):
        return make_response(render_template('groups.html'))
    elif request.method == 'POST':
        save_path = CSVManager.save_csv(request.files['csv_file'])
        csv_data = CSVManager.read_csv(save_path)
        BusinessLogic.make_concurrent_calls(
            request=request,
            function=BusinessLogic.create_address_groups,
            csv=csv_data
        )
        return make_response(redirect(url_for('address_groups')))
    return make_response(redirect(url_for('index')))

@app.route('/security_rules', methods=['GET', 'POST'])
def security_rules():
    if request.method == 'GET' and BusinessLogic.check_for_valid_session(request):
        return make_response(render_template('security_rules.html'))
    elif request.method == 'POST':
        save_path = CSVManager.save_csv(request.files['csv_file'])
        csv_data = CSVManager.read_csv(save_path)
        BusinessLogic.make_concurrent_post_rule_calls(
            request=request,
            function=BusinessLogic.create_security_post_rules,
            csv=csv_data,
            device_group=request.form.get('device-group') or 'shared'
        )
        return make_response(redirect(url_for('security_rules')))
    return make_response(redirect(url_for('index')))


# def create_post_rules_concurrent(csv, post_rules_manager, rule_name):
#     response = ["No CSV"]
#
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = []
#         for counter, csv_data in enumerate(csv):
#             futures.append(executor.submit(create_post_rule, csv_data, post_rules_manager, rule_name, counter))
#
#         concurrent.futures.wait(futures)
#
#         for future in futures:
#             response.append(future.result())
#
#     return response
#
#
# def create_new_post_rule(csv_data, post_rules_manager):
#     return post_rules_manager.create_post_rule(name=csv_data.get('NAME'),
#                                                action=csv_data.get('ACTION'),
#                                                description=csv_data.get('DESCRIPTION'),
#                                                source_zone=csv_data.get('FROM'),
#                                                source_address=csv_data.get('SOURCE'),
#                                                destination_zone=csv_data.get('TO'),
#                                                destination_address=csv_data.get('DESTINATION'),
#                                                service=csv_data.get('SERVICE'),
#                                                profile_type=csv_data.get('PROFILE TYPE'),
#                                                profile=csv_data.get('PROFILE'),
#                                                application="any")
#
#
# def create_post_rule(csv_data, post_rules_manager):
#     return post_rules_manager.create_post_rule(action=csv_data.get('ACTION'),
#                                                source_address=csv_data.get('SOURCE'),
#                                                source_zone=csv_data.get('FROM'),
#                                                destination_address=csv_data.get('DESTINATION'),
#                                                destination_zone=csv_data.get('TO'),
#                                                protocol=csv_data.get('IP Protocol').upper(),
#                                                destination_port=csv_data.get('Destination Port'),
#                                                name=csv_data.get('Rul'),
#                                                application="any")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    args = parser.parse_args()
    app.run(port=args.port)

