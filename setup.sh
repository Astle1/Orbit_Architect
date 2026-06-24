#!/bin/bash
echo "Starting setup..." > setup.log
curl -sL https://mise.run | sh >> setup.log 2>&1
echo "Mise installed" >> setup.log
~/.local/share/mise/bin/mise --version >> setup.log 2>&1
