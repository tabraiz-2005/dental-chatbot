echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
git add Procfile
git commit -m "Add Procfile"
git push
```

### Step 2 — Deploy on Railway

1. Go to **railway.app**
2. Sign up with GitHub
3. Click **New Project → Deploy from GitHub repo**
4. Select **tabraiz-2005/dental-chatbot**
5. Click **Add Variables** and add:
   - `GROQ_API_KEY` = your actual Groq key
6. Wait 2 minutes for it to build

<!-- ### Step 3 — Get your public URL

Railway will give you a URL like:
```
https://dental-chatbot-production.up.railway.app -->