#!/bin/bash
# adapted from https://gist.github.com/jgamblin/9701ed50398d138c65ead316b5d11b26
APIKEY="From Here https://api.slack.com/custom-integrations/legacy-tokens"
EMOJI="headphones,musical_note,loud_sound,musical_score,notes"

while true
      SONG=$(osascript -e 'tell application "Spotify" to (name of current track & " -- " & artist of current track) as string')
      URLSONG=$(echo "$SONG" | perl -MURI::Escape -ne 'chomp;print uri_escape($_),"\n"')
      EMO=$(echo $EMOJI | perl -e 'my $l=<STDIN>; chomp($l);my @f=split/,/,$l;print $f[int(rand($#f+1))];')
do
    curl -s -d "payload=$json" "https://slack.com/api/users.profile.set?token="$APIKEY"&profile=%7B%22status_text%22%3A%22"$URLSONG"%22%2C%22status_emoji%22%3A%22%3A$EMO%3A%22%7D"  > /dev/null
    sleep 60 
done 
