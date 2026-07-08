#!/bin/bash
set -e

URL="http://localhost:5050/api/timeline_post"
CONTENT="test post $RANDOM"

echo "POST: creating timeline post..."
ID=$(curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Test\", \"email\": \"test@example.com\", \"content\": \"$CONTENT\"}" \
  | jq .id)
echo "created post id=$ID"

echo "GET: checking post was added..."
curl -s "$URL" | jq -e --arg id "$ID" '.[] | select(.id == ($id | tonumber))'

echo "DELETE: cleaning up test post..."
curl -s -o /dev/null -w "delete status: %{http_code}\n" -X DELETE "$URL/$ID"
