#!/usr/bin/env python3
from genaiRouter import generate_res
import requests
import argparse
import random
import json
import sys
import os
import re

def main():
    try:
        parser = argparse.ArgumentParser(
            description="Use ChatGPT to generate a description for a pull request."
        )
        parser.add_argument(
            "--github-api-url", type=str, required=True, help="The GitHub API URL"
        )
        parser.add_argument(
            "--github-repository", type=str, required=True, help="The GitHub repository"
        )
        parser.add_argument(
            "--pull-request-id",
            type=int,
            required=True,
            help="The pull request ID",
        )
        parser.add_argument(
            "--github-token",
            type=str,
            required=False,
            help="The GitHub token",
        )
        parser.add_argument(
            "--openai-api-base",
            type=str,
            required=False,
            help="The OpenAI API base URL",
            default="https://x.x.x.x"
        )
        parser.add_argument(
            "--openai-api-key",
            type=str,
            required=False,
            help="The OpenAI API key",
                    ) 
        parser.add_argument(
            "--allowed-users",
            type=str,
            required=False,
            help="A comma-separated list of GitHub usernames that are allowed to trigger the action, empty or missing means all users are allowed",
        )

        args = parser.parse_args()
        print(args.openai_api_key,args.github_token)
        github_api_url = args.github_api_url
        repo = args.github_repository
        github_token = args.github_token
        pull_request_id = args.pull_request_id
        openai_api_key = args.openai_api_key
        openai_api_base = args.openai_api_base
        allowed_users = os.environ.get("INPUT_ALLOWED_USERS", "")
        runner = True
        connection_data = {
            "base":openai_api_base,
            "key":openai_api_key
        }
        if runner:
            if allowed_users:
                allowed_users = allowed_users.split(",")
            open_ai_model = os.environ.get("INPUT_OPENAI_MODEL", "gpt-35-turbo-16k")
            max_prompt_tokens = int(os.environ.get("INPUT_MAX_TOKENS", "6500"))
            model_temperature = float(os.environ.get("INPUT_TEMPERATURE", "0.7"))
            authorization_header = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token %s" % github_token,
            }
            pull_request_url = f"{github_api_url}/repos/{repo}/pulls/{pull_request_id}"
            pull_request_result = requests.get(
                pull_request_url,
                headers=authorization_header,
            )
            if pull_request_result.status_code != requests.codes.ok:
                print(
                    "Request to get pull request data failed: "
                    + str(pull_request_result.status_code)
                )
                return 1
            pull_request_data = json.loads(pull_request_result.text) 
            if allowed_users:
                pr_author = pull_request_data["user"]["login"]
                if pr_author not in allowed_users:
                    print(
                        f"Pull request author {pr_author} is not allowed to trigger this action"
                    )
                    return 0
            max_pages = 30
            for page_num in range(1, max_pages):
                pull_files_url = f"{pull_request_url}/files?page={page_num}&per_page=30"
                pull_files_result = requests.get(
                    pull_files_url,
                    headers=authorization_header,
                )
                if pull_files_result.status_code != requests.codes.ok:
                    print(
                        "Request to get list of files failed with error code: "
                        + str(pull_files_result.status_code)
                    )
                    return 1
                pull_files_chunk = json.loads(pull_files_result.text)
                if len(pull_files_chunk) == 0:
                    break
                # pull_request_files.extend(pull_files_chunk)
                pull_request_files = pull_files_chunk
                # print(pull_files_chunk)
                def find_comment_id(issue_number, comment_body):  
                    url = f'{github_api_url}/repos/{repo}/issues/{issue_number}/comments'  
                    response = requests.get(url, headers=authorization_header)  
                    comments = json.loads(response.text)  
                    for comment in comments:  
                        if comment_body in comment['body']:  
                            return comment['id']  
                    return None  
            
            if pull_request_data["body"]:
                model_temperature=0.8
                max_prompt_tokens = 6500
                open_ai_model="gpt-35-turbo-16k"
                bot_data = "you are a nice bot that validate the code inside a PR , please make it short , effective you can be also bit funny give code recommantions "
                messages=[{"role": "system","content": str(bot_data)},{"role": "user", "content": str(pull_request_files)}]
                print(f"DEBUG: messages: {messages}")
                openai_response = generate_res(messages,open_ai_model,model_temperature,max_prompt_tokens,connection_data)
                pull_req_genai = openai_response.choices[0].message.content
                # open_ai_model="gpt-4"
                # max_prompt_tokens = 6000
                # model_temperature = 0.8
                # messages=[{"role": "system","content": 'you bot that create PR review, make it short and to the point'},{"role": "user", "content": str(pull_req_genai)}]
                # openai_response = generate_res(messages,open_ai_model,model_temperature,max_prompt_tokens,connection_data)
                pull_req_genai = '# PR BOT ' + str(pull_req_genai)
                def find_comment_id(issue_number, comment_body):  
                    url = f'{github_api_url}/repos/{repo}/issues/{issue_number}/comments'  
                    response = requests.get(url, headers=authorization_header)  
                    comments = json.loads(response.text)  
                    for comment in comments:  
                        if comment_body in comment['body']:  
                            return comment['id']  
                    return None  
                def update_comment(comment_id, new_body):  
                    url = f'{github_api_url}/repos/{repo}/issues/comments/{comment_id}'  
                    response = requests.patch(url, headers=authorization_header, json={'body': new_body})  
                    return response.status_code == 200  
                
                def update_comment_in_pull_request(issue_number, comment_body, new_body):  
                    comment_id = find_comment_id(issue_number, comment_body)  
                    if comment_id:  
                        return update_comment(comment_id, new_body)  
                    return False  
                update_comment_in_pull_request(pull_request_id, 'PR BOT', pull_req_genai)
                print("need to generate new comment")
                requests.post(
                        f'{github_api_url}/repos/{repo}/issues/{pull_request_id}/comments',
                        headers=authorization_header,
                        json={"body": f'{pull_req_genai}'},
                    )

    except Exception as e:
        print("An exception occurred: " + str(e))
        pass

main()
