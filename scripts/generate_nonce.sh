#!/bin/bash
# Generates a 6-character random alphanumeric nonce
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 6 | head -n 1
