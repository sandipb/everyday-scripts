#!/bin/bash
# Credit: https://gist.github.com/angelo-v/e0208a18d455e2e6ea3c40ad637aac53#gistcomment-3439919
jq -R 'gsub("-";"+") | gsub("_";"/")| split(".") | .[0],.[1] | @base64d | fromjson'
