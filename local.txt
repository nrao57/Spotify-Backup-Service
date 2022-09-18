
export SPOTIFY_CLIENT_ID=$(gcloud secrets versions access latest --secret="SPOTIFY_CLIENT_ID")
export SPOTIFY_CLIENT_SECRET=$(gcloud secrets versions access latest --secret="SPOTIFY_CLIENT_SECRET")
export USER_ID=fx0fcvdi81cgb2s7x7irvplzq
python backup.py